#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# RISC-V (rv32im) simulator by M. KUGA 2020/09/13
#

import rvsim
import tkinter as tk
import curses
import re
import threading
import argparse

from tkinter   import messagebox
from functools import partial

#
# Argument Parser
#
ap = argparse.ArgumentParser(description="RISC-V simurator" )
ap.add_argument( "prog_file",  nargs=1, help="Program file")
ap.add_argument( "data_file",  nargs=1, help="Data file"   )

args = ap.parse_args()

p_file = args.prog_file[0]
d_file = args.data_file[0]

#
# Main
#
rv = rvsim.rvsim() # Constructor

rv.reset()

scr = tk.Tk()
scr.title("rvsim")

# GUI Resource

frame_reg=[]
for i in range(9):
    frame_reg.append(tk.Frame(scr))

frame_cmd  = tk.Frame(scr)
frame_led7 = tk.Frame(scr)
frame_led  = tk.Frame(scr)
frame_ssw  = tk.Frame(scr)
frame_psw  = tk.Frame(scr)
frame_stat = tk.Frame(scr)


led7 = [
    tk.PhotoImage(file="resource/led{0:1x}.gif".format(i)) for i in range(16)
]

led = [
    tk.PhotoImage(file="resource/rgb_w.gif"),
    tk.PhotoImage(file="resource/rgb_g.gif")
]

rgb = [
    tk.PhotoImage(file="resource/rgb_k.gif"),
    tk.PhotoImage(file="resource/rgb_b.gif"),
    tk.PhotoImage(file="resource/rgb_c.gif"),
    tk.PhotoImage(file="resource/rgb_g.gif"),
    tk.PhotoImage(file="resource/rgb_r.gif"),
    tk.PhotoImage(file="resource/rgb_m.gif"),
    tk.PhotoImage(file="resource/rgb_y.gif"),
    tk.PhotoImage(file="resource/rgb_w.gif")
]

ssw = [
    tk.PhotoImage(file="resource/ssw0.gif"),
    tk.PhotoImage(file="resource/ssw1.gif")
]
    
psw = [
    tk.PhotoImage(file="resource/psw0.gif"),
    tk.PhotoImage(file="resource/psw1.gif")
]

#
# Simlation Methods
#

def reset():
    rv.init_imem( p_file )
    rv.init_dmem( d_file )
    rv.set_trace( 1 ) # 1: All instruction trace
    rv.reset()
    statusbar.configure(text="Reset processor and load program." )

global go_background
global go_mode
go_mode = 0

global stdscr     # for curses

def step(n):
    global go_mode
    global stdscr
#   statusbar.configure(text="Step")
    repeat = int( n, 10 )
    while go_mode or repeat > 0:
        trace = rv.step() 
        token = re.split('[\s\t]', trace)
        if len(token) >= 8 :
            addr = int( token[7], 16 )
            data = int( token[6], 16 )
            if go_mode and token[2] == "sb" and ( addr >= 0x7ff00000 and addr <= 0x7ff0ffff ):
                addr &= 0x0000ffff
                stdscr.addch( addr//80, addr%80, chr(data) )
                stdscr.refresh()
            elif token[2] == "sw" and addr == 0x7ff10000 :
                update_led7(data)
            elif (token[2] == "sw" or token[2] == "sh") and addr == 0x7ff10004 :
                update_led(data)
            elif (token[2] == "sw" or token[2] == "sh" or token[2] == "sb") and addr == 0x7ff10008 :
                update_rgb(data)
        if go_mode == 0:
            print( trace )
            repeat -= 1
    update_reg()

global th
th = 0

def cmd_go():
    global go_mode
    global go_background
    global stdscr
    global th
    if go_mode == 0:
        stdscr = curses.initscr()
        max_yx = stdscr.getmaxyx()
#       print( max_yx )
        if max_yx[0] < 46 or max_yx[1] < 80:
            curses.endwin()
            print( "Current window size (%d,%d)."%(max_yx[1],max_yx[0]) )
            print( "Set terminal windows size over 80x46" )
            return
        stdscr.clear()
        curses.noecho()
        curses.cbreak()
        stdscr.nodelay(True)
        stdscr.keypad(True)
        rv.set_trace(2)         # Trace mode : Peripheral only
        go_mode = 1
        th = threading.Thread(target=step, args=("1",))
        th.setDaemon(True)
        th.start()
        go_background = btn_go.cget("background")
        btn_go.configure(background="red")
        statusbar.configure(text="Enter GO mode with Curses window. Re-push ∞ button to exit.")
    else:
        go_mode = 0
#       th.join()
        curses.echo()
        curses.nocbreak()
        stdscr.nodelay(False)
        stdscr.keypad(False)
        stdscr.clear()
        stdscr.refresh()
        curses.endwin()
        rv.set_trace(1)         # Trace mode : All inst.
        btn_go.configure(background=go_background)
        statusbar.configure(text="Exit GO mode.")

#
# Dump data memory
#
    
def dmem(addr, mode):
    def chr_printable( ch ):
        return ch if ord(ch)>=0x20 and ord(ch)<=0x7f else "."

    daddr = int(addr,16)
    if mode == 1: # Byte mode
        print( "Address: +0+1+2+3 +4+5+6+7 +8+9+A+B +C+D+E+F" )
        print( "--------+--------+--------+--------+--------" )
        for j in range(16):
            print( "{0:08x}:".format(daddr+j*16), end="" )
            data=[]
            for i in range(4):
                data.append( rv.read_dmem((daddr+(j*4+i)*4)&0x1ffff) )
                print( "{0:02x}{1:02x}{2:02x}{3:02x} ".format(
                    (data[i]    )&0xff,
                    (data[i]>> 8)&0xff,
                    (data[i]>>16)&0xff,
                    (data[i]>>24)&0xff
                ), end="" )
            for i in range(4):
                print( "{0:1s}{1:1s}{2:1s}{3:1s}".format(
                    chr_printable(chr((data[i]    )&0xff)),
                    chr_printable(chr((data[i]>> 8)&0xff)),
                    chr_printable(chr((data[i]>>16)&0xff)),
                    chr_printable(chr((data[i]>>24)&0xff))
                ), end="" )
            print()
    else: # Word mode
        print( "Address: +3+2+1+0 +7+6+5+4 +B+A+9+8 +F+E+D+C" )
        print( "--------+--------+--------+--------+--------" )
        for j in range(16):
            print( "{0:08x}:".format(daddr+j*16), end="" )
            data=[]
            for i in range(4):
                data.append( rv.read_dmem((daddr+(j*4+i)*4)&0x1ffff) )
                print( "{0:08x} ".format(data[i]&0xffffffff), end="" )
            for i in range(4):
                print( "{0:1s}{1:1s}{2:1s}{3:1s}".format(
                    chr_printable(chr((data[i]>>24)&0xff)),
                    chr_printable(chr((data[i]>>16)&0xff)),
                    chr_printable(chr((data[i]>> 8)&0xff)),
                    chr_printable(chr((data[i]    )&0xff))
                ), end="" )
            print()
    print()
            
#
# Register
#

global reg
reg = [ 0 for  i in range(32) ]
reg_label=[ 0 for i in range(32) ]

def init_reg ():
    for i in range(8) :
        for j in range(4) :
            reg_label[i*4+j] = tk.Label( frame_reg[i],
                                         borderwidth = 5, relief=tk.GROOVE,
                                         font=("Consolas",20),
                                         justify="left"
            )
            reg_label[i*4+j].pack(side=tk.LEFT)
    
def update_reg ():
    global reg
    reg_name = [ "pc", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
                 "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
                 "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
                 "s8", "s9", "s10","s11","t3", "t4", "t5", "t6"
    ]
    new_reg     = rv.read_reg()
    new_reg[0]  = rv.read_pc()
    for i in range(32) :
        reg_label[i].configure( foreground="red" if reg[i] != new_reg[i] else "black" )
        if i==0 :
            reg_label[0].configure( text="   pc :{0:08x} ".format(new_reg[0]&0xffffffff) )
        else:
            reg_label[i].configure(
                text="{0:02d}:{1:3s}:{2:08x} ".format(i, reg_name[i], new_reg[i]&0xffffffff )
            )
        reg[i] = new_reg[i]
            
#
# 7 segment LEDs
#
    
led7_label=[ 0 for i in range(8) ]

def init_led7( value ):
    mask = 0xf
    for i in range(8):
        led7_label[i] = tk.Label(frame_led7, image=led7[value & mask])
        led7_label[i].pack(side=tk.RIGHT)
        value >>= 4

def update_led7( value ):
    mask = 0xf
    for i in range(8):
        led7_label[i].configure( image=led7[value & mask] )
        value >>= 4

#
# 16 LEDs
#

led_label=[ 0 for i in range(16) ]

def init_led( value ):
    mask = 0x1
    for i in range(16):
        led_label[i] = tk.Label(frame_led, image=led[value & mask])
        led_label[i].pack(side=tk.RIGHT)
        value >>= 1

def update_led( value ):
    mask = 0x1
    for i in range(16):
        led_label[i].configure( image=led[value & mask] )
        value >>= 1

#
# RGB LEDs
#

rgb_label=[ 0 for i in range(2) ]

def init_rgb( value ):
    mask = 0x7
    for i in range(2):
        rgb_label[i] = tk.Label(frame_led7, image=rgb[value & mask])
        rgb_label[i].pack(side=tk.RIGHT)
        value >>= 3

def update_rgb( value ):
    mask = 0x7
    for i in range(2):
        rgb_label[i].configure( image=rgb[value & mask] )
        value >>= 3

#
# Slide SW
#

btn_ssw = [ 0 for i in range(16) ]
def init_ssw( value ):
    mask = 0x1
    for i in range(16):
        btn_ssw[i] = tk.Button(frame_ssw, image=ssw[value & mask], command=partial( set_ssw, i ) )
        btn_ssw[i].pack(side=tk.RIGHT)
        value >>= 1
        
global sw_val
sw_val = 0
        
def set_ssw( value ):
    global sw_val
    if( sw_val & ( 1 << value ) ):
        btn_ssw[value].configure( image=ssw[0] )
    else:
        btn_ssw[value].configure( image=ssw[1] )
    sw_val = sw_val ^ ( 1<< value )
    rv.set_sw( sw_val )
    statusbar.configure(text="Switch:{0:08x}".format(sw_val))

    
#
# Push SW
#

btn_psw = [ 0 for i in range(5) ]
def init_psw( value ):
    mask = 0x1
    for i in range(5):
        btn_psw[i] = tk.Button(frame_psw, image=psw[value & mask], command=partial( set_psw, i ) )
        value >>= 1
    btn_psw[1].grid( row=0, column=1) # Up
    btn_psw[3].grid( row=1, column=0) # Left
    btn_psw[4].grid( row=1, column=1) # Center
    btn_psw[0].grid( row=1, column=2) # Right
    btn_psw[2].grid( row=2, column=1) # Down
        
def set_psw( value ):
    global sw_val
    if( sw_val & ( 0x10000 << value ) ):
        btn_psw[value].configure( image=psw[0] )
    else:
        btn_psw[value].configure( image=psw[1] )
    sw_val = sw_val ^ ( 0x10000 << value )
    rv.set_sw( sw_val )
    statusbar.configure(text="Switch:{0:08x}".format(sw_val))

#
# Command Frame
#
btn_reset = tk.Button( frame_cmd, text="Reset", command=reset  )
btn_go    = tk.Button( frame_cmd, text="∞",    command=cmd_go )
btn_step  = tk.Button( frame_cmd, text="Step",  command=lambda : step( "1" ) )

stepn_num = tk.StringVar()
ent_stepn = tk.Entry ( frame_cmd, textvariable=stepn_num, width=10 )
ent_stepn.insert(0, "10")
btn_stepn = tk.Button( frame_cmd, text="StepN", command=lambda : step(stepn_num.get()) )

btn_dmem  = tk.Button( frame_cmd, text="D_Mem", command=lambda : dmem(dmem_addr.get(), dmem_mode.get())  )
dmem_addr = tk.StringVar()
ent_dmem  = tk.Entry ( frame_cmd, textvariable=dmem_addr, width=10 )
ent_dmem.insert(0, "0x00100000")

dmem_mode = tk.IntVar()
dmem_mode.set(4) # defaullt Word  mode
btn_dmemw = tk.Radiobutton( frame_cmd, text=":W", value=4, variable=dmem_mode )
btn_dmemb = tk.Radiobutton( frame_cmd, text=":B", value=1, variable=dmem_mode )

#
# Status Bar
#
statusbar = tk.Label(scr, text="Status", bd=1, relief=tk.SUNKEN, anchor=tk.W)
statusbar.pack(side=tk.BOTTOM, fill=tk.X)

#
# Frame packing
#
for i in range(8):
    frame_reg[i].pack(anchor=tk.W)
frame_cmd.pack()
frame_led.pack()
frame_led7.pack()
frame_ssw.pack()
frame_psw.place(relx=0.86,rely=0.75)

btn_reset.pack(side=tk.LEFT)
btn_go.pack   (side=tk.LEFT)
btn_step.pack (side=tk.LEFT)
btn_stepn.pack(side=tk.LEFT)
ent_stepn.pack(side=tk.LEFT)
btn_dmem.pack (side=tk.LEFT)
ent_dmem.pack (side=tk.LEFT)
btn_dmemw.pack(side=tk.LEFT)
btn_dmemb.pack(side=tk.LEFT)

scr.resizable(0,0) # no resize

#
# initial
#

def close_window():
    global go_mode
    if messagebox.askokcancel( "Quit", "プログラムを終了しますか？"):
        if go_mode:
            curses.echo()
            curses.nocbreak()
            stdscr.nodelay(False)
            stdscr.keypad(False)
            stdscr.clear()
            stdscr.refresh()
            curses.endwin()
        scr.destroy()
        
init_ssw( sw_val )
init_psw( (sw_val>>16) & 0x1f )
init_reg()
update_reg()
init_led(0)
init_rgb(0)
init_led7(0)

rv.set_sw( sw_val )
reset()

scr.protocol("WM_DELETE_WINDOW", close_window)

scr.mainloop()
