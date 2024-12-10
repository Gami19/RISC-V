#! /usr/bin/python3

import rvsim
import argparse
import re
import readline

#
# Argument Parser
#

ap = argparse.ArgumentParser(description="rvsim : RISC-V simurator" )
ap.add_argument( "prog_file",  nargs=1, help="Program file")
ap.add_argument( "data_file",  nargs=1, help="Data file"   )
ap.add_argument( '-n', '--no_trace_out', action='store_true', help='no trace mode only executed instruction count' )
ap.add_argument( '-d', '--debug',        action='store_true', help='interactive debug mode'  )
ap.add_argument( '-v', '--verbose',      action='store_true', help='internal debugging message' )
ap.add_argument( '-m', '--mdump',        action='store_true', help='data memory dump'  )

args = ap.parse_args()

p_file = args.prog_file[0]
d_file = args.data_file[0]
nto   = args.no_trace_out
dmode = args.debug
vmode = args.verbose
mdump = args.mdump

#
# Main
#
rv = rvsim.rvsim() # Constructor

rv.reset()
status = rv.init_imem( p_file )
if vmode:
    print("#instruction:",status) 

status = rv.init_dmem( d_file )
if vmode:
    print("#data:",status) 

rv.set_trace( 1 ) # trace all inst

global b_flag
b_flag = 0

def alltrace (nto):
    inum = 0
    if nto != True:
        print( "Address  Inst.    Assembly code         RD/RS1   RS1/RS2  RS2/Imm" )

    while True :
        trace = rv.step()
        if nto != True:
            print( trace )
        inum += 1
        token = re.split('[\s\t]', trace)
        if token[2] == "ebreak" :
            break

    print("'ebreak' detected.")
    print("{0:d} instructions are executed.".format(inum) )

# end alltrace()

def chr_printable( ch ):
    return chr(ch) if ch>=0x20 and ch<0x7f else "."

def debug ():
    reg = [ 0 for  i in range(32) ]
    reg_name = [ "pc", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
                 "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
                 "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
                 "s8", "s9", "s10","s11","t3", "t4", "t5", "t6"
    ]
    perf_name = [ "7SEG", "  16", "2RGB" ]
    cmd      = ""
    last_cmd = "h"
    addr      = 0
    next_addr = 0
    print( "Interactive debug mode" )
    while( True ):
        cmd = input( "> " )
        if cmd == "":
            cmd = last_cmd
        else:
            last_cmd = cmd
        token = re.split('[\s\t]', cmd)
        if len(token) == 0:
            continue
        #
        # step execution
        #
        if token[0] == "s" :
            global b_flag
            if b_flag :
                print("'ebreak' detected.")
                continue
            if len(token) > 1:
                num = int(token[1])
            else:
                num = 1
            while( num ):
                trace = rv.step()
                print( trace )
                num -= 1
                trace_token = re.split('[\s\t]', trace)
                if trace_token[2] == "ebreak" :
                    print("'ebreak' detected.")
                    b_flag = 1
                    break
        #
        # Dump data memory by word
        #
        if token[0] == "dw":
            if len(token) > 1:
                try:
                    addr = int(token[1], 16)
                except:
                    addr = next_addr
            else:
                addr = next_addr
            addr &= 0x1ffff
            print( "Address: +3+2+1+0 +7+6+5+4 +B+A+9+8 +F+E+D+C" )
            print( "--------+--------+--------+--------+--------" )
            for i in range(16):
                print( "{0:08x}:".format(addr+0x00100000+i*4*4), end="" )
                for j in range(4):
                    word = rv.read_dmem(addr+(i*4+j)*4)
                    print( "{0:08x} ".format(word), end="" )
                for j in range(4):
                    word = rv.read_dmem(addr+(i*4+j)*4)
                    print( "{0:1s}{1:1s}{2:1s}{3:1s}".format(
                        chr_printable((word>>24)&0xff),
                        chr_printable((word>>16)&0xff),
                        chr_printable((word>> 8)&0xff),
                        chr_printable((word    )&0xff)
                    ), end="" )
                print()
            next_addr = addr + 256
        #
        # Dump data memory by byte
        #
        if token[0] == "db":
            if len(token) > 1:
                try:
                    addr = int(token[1], 16)
                except:
                    addr = next_addr
            else:
                addr = next_addr
            addr &= 0x1ffff
            print( "Address: +0+1+2+3 +4+5+6+7 +8+9+A+B +C+D+E+F" )
            print( "--------+--------+--------+--------+--------" )
            for i in range(16):
                print( "{0:08x}:".format(addr+0x00100000+i*4*4), end="" )
                for j in range(4):
                    word = rv.read_dmem(addr+(i*4+j)*4)
                    print( "{0:02x}{1:02x}{2:02x}{3:02x} "
                           .format(word&0xff, (word>>8)&0xff, (word>>16)&0xff, (word>>24)&0xff), end="" )
                for j in range(4):
                    word = rv.read_dmem(addr+(i*4+j)*4)
                    print( "{0:1s}{1:1s}{2:1s}{3:1s}".format(
                        chr_printable((word    )&0xff),
                        chr_printable((word>> 8)&0xff),
                        chr_printable((word>>16)&0xff),
                        chr_printable((word>>24)&0xff)
                    ), end="" )
                print()
            next_addr += 256
        #
        # Show video memory as the screen image
        #
        elif token[0] == "v" :
            for i in range(45):
                for j in range(20):
                    word = rv.read_vram((i*20+j)*4)
                    print( "{0:1s}{1:1s}{2:1s}{3:1s}".format(
                        chr_printable((word    )&0xff),
                        chr_printable((word>> 8)&0xff),
                        chr_printable((word>>16)&0xff),
                        chr_printable((word>>24)&0xff)
                    ), end="" )
                print()
            next_addr = addr + 256
        #
        # Show and set value of SWs
        #
        elif token[0] == "sw":
            if len(token) > 1:
                try:
                    num = int(token[1], 16)
                except:
                    num = 0
                rv.set_sw(num)
            print( "SW: {0:08x}".format( rv.read_sw() ) )
        #
        # Show registers
        #
        elif token[0] == "reg" or token[0] == "r":
            reg = rv.read_reg()
            reg[0]  = rv.read_pc()
            for i in range(8):
                for j in range(4):
                    print( "{0:3s}: {1:08x}  ".format( reg_name[i*4+j], reg[i*4+j] ), end="" )
                print()
        #
        # Show LEDs
        #
        elif token[0] == "led" or token[0] == "l":
            for i in range(3):
                print( "{0:4s}: {1:08x}  ".format( perf_name[i], rv.read_perf(i) ))
        #
        # Help
        #
        elif token[0] == "h" or token[0] == "help" :
            print( "h          : Help" )
            print( "q          : Quit rvsim" )
            print( "s [n]      : Step [n] execution" )
            print( "dw [adder] : Dump data memory from [addr] address by word" )
            print( "db [adder] : Dump data memory from [addr] address by byte" )
            print( "v          : Show video memory as the screen image" )
            print( "sw [value] : Show and Set value of Slide and Push switches" )
            print( "led        : Show LEDs value" )
            print( "reg        : Show Registers" )
        #
        # Quit
        #
        elif token[0] == "q":
            break
# end debug()

def memory_dump():
    addr = 0
    print( "Address: +3+2+1+0 +7+6+5+4 +B+A+9+8 +F+E+D+C" )
    print( "--------+--------+--------+--------+--------" )
    for j in range(16):
        for i in range(16):
            print( "{0:08x}:".format(addr+0x00100000+i*4*4), end="" )
            for j in range(4):
                word = rv.read_dmem(addr+(i*4+j)*4) & 0xffffffff
                print( "{0:08x} ".format(word), end="" )
            for j in range(4):
                word = rv.read_dmem(addr+(i*4+j)*4)
                print( "{0:1s}{1:1s}{2:1s}{3:1s}".format(
                    chr_printable((word>>24)&0xff),
                    chr_printable((word>>16)&0xff),
                    chr_printable((word>> 8)&0xff),
                    chr_printable((word    )&0xff)
                ), end="" )
            print()
        addr = addr + 256

#
# Main 
#
if dmode == False :
    alltrace(nto)
else :
    debug()

if mdump == True :
    memory_dump()
    
