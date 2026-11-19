"""Fin de Jungle Hijinxs: teletransporta a ambos cerca de la salida (x~0x14BF) y prueba casos.
uso: test_forkD_exit2.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
def run(name, joined, dkx, dix, p1, p2, setup=None, frames=500):
    e = Emu(rom); e.load_state(open('work/lvl_JHcheckpoint.state', 'rb').read()); e.run(60)
    e.w16(0x4F0, joined)
    for k, x in ((2, dkx), (4, dix)):
        e.w16(0xB19 + k, x); e.w16(0xBC1 + k, 0x90); e.w16(0x1029 + k, 1); e.w16(0xEF1 + k, 0)
    if setup: setup(e)
    for f in range(5): e.w16(0x1A62, dkx - 0x80); e.run(1)
    ent0 = e.r16(0x3E); last = None; out = []
    for t in range(frames):
        e.set_buttons(1, *p1(t)); e.set_buttons(2, *p2(t)); e.run(1)
        for k in (2, 4):
            if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
        v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x56F))
        if v != last:
            out.append('t%3d DK %04X,%04X st%02X | Di %04X,%04X st%02X | lider %X 579=%04X 1929=%04X' % (t, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[2], e.r16(0x579), e.r16(0x1929)))
            last = v
        if e.r16(0x3E) != ent0:
            out.append('NIVEL TERMINADO (entrada %02X -> %02X) en t=%d' % (ent0, e.r16(0x3E), t)); break
    else:
        out.append('NO TERMINO')
    print('=====', name); print('\n'.join(out[-9:]))
R = lambda t: ['RIGHT']; N = lambda t: []; U = lambda t: ['UP']
run('P2 ausente (original)', 0, 0x1440, 0x1420, R, N)
run('P2 unido, ambos caminan', 1, 0x1440, 0x1420, R, R)
run('P2 llega primero (DK quieto atras)', 1, 0x1400, 0x1480, N, R, frames=200)
run('...y luego DK llega', 1, 0x1400, 0x1480, lambda t: ['RIGHT'] if t > 150 else [], R)
def dlead(e):
    e.w16(0x102B, 0x0C); e.w16(0x579, e.r16(0x579) & 0xFFFE); e.w16(0x56F, 2); e.w16(0xB1B, 0x1000)
run('Diddy lider (DK ausente)', 1, 0x1000, 0x1440, N, R, dlead)
