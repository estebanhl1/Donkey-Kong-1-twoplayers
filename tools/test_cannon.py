"""Barril canon en Barrel Cannon Canyon. uso: test_cannon.py ROM CASO
CASO: orig (P2 ausente, entra DK) | dk (P2 unido, entra DK) | diddy (P2 unido, entra Diddy)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, case = sys.argv[1], sys.argv[2]
e = Emu(rom); e.load_state(open('work/spr_BarrelCannonCanyon_38.state', 'rb').read())
e.w16(0x4F0, 0 if case == 'orig' else 1)
idx = 4 if case == 'diddy' else 2
def cannons(): return [(s, e.r16(0xB19+2*s), e.r16(0xBC1+2*s), e.r16(0x1029+2*s)) for s in range(3, 26) if e.r16(0xD45+2*s) == 0x38]
c = cannons()[0]
last = None
for f in range(700):
    if f == 5:
        e.w16(0xB19 + idx, c[1]); e.w16(0xBC1 + idx, c[2] + 0x20); e.w16(0x1029 + idx, 1); e.w16(0xEF1 + idx, 0xFE00)
    e.set_buttons(1); e.set_buttons(2, *(['UP'] if case != 'orig' else []))
    if f > 120 and f % 90 < 3:          # disparar (B) al siguiente
        e.set_buttons(1 if idx == 2 else 2, 'B')
    e.run(1)
    for k in (2, 4):
        if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x56F), e.r16(0x579) & 1)
    if v != last:
        print('f%3d DK %04X,%04X st%02X | Di %04X,%04X st%02X | lider %X 579=%04X cam %04X vidas %d | canones %s' % (
            f, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[2], e.r16(0x579), e.r16(0x1A62), e.r16(0x575),
            ['%04X,%04X st%X' % x[1:] for x in cannons()][:3]))
        last = v
