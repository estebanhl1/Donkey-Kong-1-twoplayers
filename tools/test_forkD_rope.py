"""Cuerdas verticales (Slipslide Ride): companero solo, lider solo, los dos en la misma cuerda.
uso: test_forkD_rope.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
def ropes(e): return [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x30]
for case in ('Diddy (P2) solo', 'DK solo', 'los dos', 'los dos, DK se suelta'):
    e = Emu(rom); e.load_state(open('work/spr_Slipslide_30.state', 'rb').read()); e.w16(0x4F0, 1)
    r = ropes(e)[0]; rx = e.r16(0xB19 + 2*r)
    gy = e.r16(0xBC1 + 2*r) - 0x60
    for f in range(10): e.w16(0x1A62, rx - 0x80); e.set_buttons(2, 'UP'); e.run(1)
    who = [4] if case.startswith('Diddy') else ([2] if case == 'DK solo' else [2, 4])
    for k in (2, 4):
        if k in who: e.w16(0xB19 + k, rx); e.w16(0xBC1 + k, gy + (0x30 if k == 2 else 0x50)); e.w16(0x1029 + k, 1); e.w16(0xEF1 + k, 0)
        else: e.w16(0xB19 + k, rx - 0x50)
    log = []; last = None
    for f in range(240):
        p1 = ['UP'] if f < 120 else (['B', 'RIGHT'] if case.endswith('suelta') and f < 130 else [])
        e.set_buttons(1, *p1); e.set_buttons(2, 'UP')
        e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
        v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x1B01), e.r16(0x1AFD), e.r16(0x1AFF))
        if v != last:
            log.append('f%3d DK %04X,%04X st%02X | Di %04X,%04X st%02X | 1B01=%04X 1AFD=%04X 1AFF=%04X' % (f, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[2], v[3], v[4]))
            last = v
    print('=====', case); print('\n'.join(log[:14]))
