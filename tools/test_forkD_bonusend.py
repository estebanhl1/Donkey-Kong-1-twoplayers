"""Fin de bonus ($1E2B): ¿quien festeja? ¿termina el bonus? uso: test_forkD_bonusend.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
def run(name, ev, setup):
    e = Emu(rom); e.load_state(open('work/lvl_JHbonus1.state', 'rb').read()); e.run(30)
    e.w16(0x4F0, 1); setup(e); ent0 = e.r16(0x3E)
    e.w16(0x1E2B, ev)
    last = None; out = []
    for t in range(500):
        e.set_buttons(2, 'UP'); e.run(1)
        for k in (2, 4):
            if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
        v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x1E2B))
        if v != last:
            out.append('t%3d DK st%02X anim %02X | Di st%02X anim %02X | lider %X 1E2B=%X' % (t, v[0], e.r16(0x16AD), v[1], e.r16(0x16AF), e.r16(0x56F), v[2])); last = v
        if e.r16(0x3E) != ent0: out.append('SALE DEL BONUS en t=%d (entrada %02X)' % (t, e.r16(0x3E))); break
    else: out.append('NO SALE')
    print('=====', name); print('\n'.join(out[:8] + out[-2:]))
def air(k): return lambda e: (e.w16(0xBC1 + k, e.r16(0xBC1 + k) + 0x40), e.w16(0x1029 + k, 1), e.w16(0xEF1 + k, 0x0400))
run('victoria, DK lider en el aire, Diddy en el suelo', 1, air(2))
run('victoria, ambos en el suelo', 1, lambda e: None)
def dlead_air(e):
    e.w16(0x56F, 2); air(4)(e)
run('victoria, Diddy lider en el aire, DK (companero) en el suelo', 1, dlead_air)
run('fracaso (2), DK lider en el aire', 2, air(2))
