#! /usr/bin/python3

import re
import curses
import rvsim
import argparse

#
# Argument Parser
#

ap = argparse.ArgumentParser(description="RISC-V simurator" )
ap.add_argument( "prog_file",  nargs=1, help="Program file")
ap.add_argument( "data_file",  nargs=1, help="Data file"   )
#ap.add_argument( "--trace", type=int, default=2, choices=range(3), help="Trace mode, 0:None, 1:All, 2:Only perif store" )

args = ap.parse_args()

p_file = args.prog_file[0]
d_file = args.data_file[0]
#t_mode = args.trace

#
# Main
#
rv = rvsim.rvsim() # Constructor

rv.reset()
rv.init_imem( p_file )
rv.init_dmem( d_file )
rv.set_trace( 2 ) # Trace only peripheral store

stdscr = curses.initscr()
max_yx = stdscr.getmaxyx()
# print( max_yx )
if max_yx[0] < 46 or max_yx[1] < 80:
    curses.endwin()
    print( "Current window size (%d,%d)."%(max_yx[1],max_yx[0]) )
    print( "Set terminal windows size over 80x46" )
    exit()
stdscr.clear()
curses.noecho()
curses.raw()
curses.cbreak()
stdscr.nodelay(True)
stdscr.keypad(True)

while True :
    trace = rv.step()
    token = re.split('[\s\t]', trace)
    if len(token) >= 8 and token[2] == "sb" :
        addr = int( token[7], 16 )
        data = int( token[6], 16 )
        if( addr >= 0x7ff00000 and addr <= 0x7ff00fff ):
            addr &= 0x0fff
            stdscr.addch( addr//80, addr%80, chr(data) )
            stdscr.refresh()

    ch = stdscr.getch()
    if ch == curses.ERR:
        continue
#   print(ch)
    sw_val=0
    if ch == ord("l") or ch == curses.KEY_RIGHT:
        sw_val |= 0x010000
    if ch == ord("k") or ch == curses.KEY_UP:
        sw_val |= 0x020000
    if ch == ord("j") or ch == curses.KEY_DOWN:
        sw_val |= 0x040000
    if ch == ord("h") or ch == curses.KEY_LEFT:
        sw_val |= 0x080000
    if ch == ord("c"):
        sw_val |= 0x100000
    rv.set_sw( sw_val )
    if ch == ord("q"):
        break
    
stdscr.keypad(False)
stdscr.nodelay(False)
curses.nocbreak()
curses.noraw()
curses.echo()
curses.endwin()
