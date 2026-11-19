"""Modo One player: la ROM parcheada debe comportarse igual que la original
(mismos botones, incluso si el P2 aprieta cosas). uso: test_1p_identical.py"""
import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
os.environ.pop('COOP', None)
WATCH = [(0x0B1B, 'DK x'), (0x0BC3, 'DK y'), (0x102B, 'DK st'), (0x0B1D, 'Di x'), (0x0BC5, 'Di y'), (0x102D, 'Di st'),
         (0x056F, 'lider'), (0x0575, 'vidas'), (0x057B, 'bananas'), (0x1A62, 'cam x'), (0x003E, 'entrada')]
for state in ('work/1p_twokongs.state', 'work/1p_start.state', 'work/spr_JungleHijinxs_18.state', 'work/lvl_CoralCapers.state', 'work/spr_BarrelCannonCanyon_38.state'):
    emus = [Emu('roms/dkc_orig.sfc'), Emu('roms/dkc_2p.sfc')]
    for e in emus: e.load_state(open(state, 'rb').read())
    random.seed(7); diff = None
    for f in range(3000):
        p1 = random.choice([['RIGHT'], ['RIGHT', 'B'], ['RIGHT', 'Y'], ['LEFT'], ['A'], [], ['RIGHT', 'B', 'Y']])
        p2 = random.choice([['LEFT'], ['RIGHT', 'B'], ['START'] if f % 500 == 0 else [], ['A'], []])
        for e in emus:
            e.set_buttons(1, *p1); e.set_buttons(2, *p2); e.run(1)
        if diff is None:
            for a, n in WATCH:
                if emus[0].r16(a) != emus[1].r16(a):
                    diff = (f, n, emus[0].r16(a), emus[1].r16(a)); break
    print('%-40s %s' % (state, 'IDENTICO en 3000 frames' if diff is None else 'DIFIERE en f%d: %s original %04X parche %04X' % diff))
