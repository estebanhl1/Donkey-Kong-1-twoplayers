"""Llegar al final de un nivel (desde el checkpoint) con el bot invulnerable.
uso: test_forkD_end.py ROM ENTRADA P2UNIDO(0/1) [p2_adelante]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
rom, ent, joined = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3])
ahead = len(sys.argv) > 4
e = warp(rom, ent); e.w16(0x4F0, joined)
ent0 = e.r16(0x3E); lives0 = e.r16(0x575); last = None
for t in range(6000):
    lx = e.r16(0xB1B) if e.r16(0x56F) == 1 else e.r16(0xB1D)
    if ahead:
        e.set_buttons(1, *(['RIGHT'] if t % 3 else []), *(['B'] if t % 45 < 10 else []))
        e.set_buttons(2, 'RIGHT', 'Y', *(['B'] if t % 37 < 9 else []))
    else:
        e.set_buttons(1, 'RIGHT', *(['B'] if t % 45 < 10 else []))
        e.set_buttons(2, *(['RIGHT'] if joined else []), *(['B'] if joined and t % 37 < 9 else []))
    e.run(1)
    for k in (2, 4):
        if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x3E), e.r16(0x56F))
    if v != last and (v[0] not in (0, 1) or v[1] not in (0, 1, 2, 5, 6)):
        print('t%4d DK %04X,%04X st%02X | Di %04X,%04X st%02X | lider %X ent %02X 579=%04X vidas %d' % (
            t, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[3], v[2], e.r16(0x579), e.r16(0x575)))
    last = v
    if e.r16(0x3E) != ent0 and t > 50:
        print('CAMBIO DE ENTRADA %02X -> %02X en t=%d' % (ent0, e.r16(0x3E), t)); break
print('fin: vidas perdidas', lives0 - e.r16(0x575))
