"""Cuerda que se balancea (Ropey Rampage). uso: test_forkB_swing.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
from emu import Emu
rom = sys.argv[1]
if not os.path.exists('work/forkB_swing.state'):
    e = warp('roms/dkc_2p.sfc', 0x0C); e.w16(0x4F0, 0)
    x0 = e.r16(0xB1B)
    for step in range(80):
        e.w16(0xB1B, x0 + step*0x40); e.w16(0xBC3, 0xC0); e.w16(0x102B, 1); e.w16(0xEF3, 0); e.run(6)
        if any(e.r16(0xD45+2*s) == 0x31 for s in range(3, 26)): break
    open('work/forkB_swing.state', 'wb').write(e.save_state())
e = Emu(rom); e.load_state(open('work/forkB_swing.state', 'rb').read()); e.w16(0x4F0, 1)
r = [s for s in range(3, 26) if e.r16(0xD45+2*s) == 0x31][0]
last = None
for f in range(400):
    rx, ry = e.r16(0xB19+2*r), e.r16(0xBC1+2*r)
    if 5 <= f < 200 and e.r16(0x102B) not in (0x25, 0x26):   # DK flota bajo la cuerda hasta agarrarse
        e.w16(0xB1B, rx); e.w16(0xBC3, ry - 0x10); e.w16(0x102B, 1); e.w16(0xEF3, 0)
    if f == 5:   # Diddy (P2) en el suelo cerca
        e.w16(0xB1D, rx - 0x30); e.w16(0xBC5, 0x90); e.w16(0x102D, 1); e.w16(0xEF5, 0)
    b2 = ['UP'] if f < 150 else (['LEFT'] if f % 40 < 20 else ['RIGHT'])
    e.set_buttons(1, *(['B'] if f == 300 else [])); e.set_buttons(2, *b2)
    e.run(1)
    for k in (2, 4): e.w16(0x1595+k, 0)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x1B01))
    if v != last:
        print('f%3d cuerda %04X,%04X | DK %04X,%04X st%02X | Di %04X,%04X st%02X | 1AFD=%04X 1AFF=%04X 1B01=%04X' % (
            f, rx, ry, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], e.r16(0x1AFD), e.r16(0x1AFF), v[2]))
        last = v
