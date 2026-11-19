"""¿Puede cada Kong matar al Gnawty saltandole encima o rodando? uso: test_stomp.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
base = Emu(rom); base.load_state(open('work/1p_twokongs.state', 'rb').read())
# ambos avanzan un poco para que aparezca el Gnawty; P2 se une
base.set_buttons(1, 'RIGHT'); base.set_buttons(2, 'RIGHT'); base.run(40)
base.set_buttons(1); base.set_buttons(2); base.run(1)
snap = base.save_state()

def gnawty(e):
    for s in range(3, 26):
        if e.r16(0xD45 + 2*s) == 0x4D:
            return s
    return None

def trial(who, action, delay):
    e = base; e.load_state(snap)
    pl = 2 if who == 'Diddy(P2)' else 1
    other = 1 if pl == 2 else 2
    s = gnawty(e)
    if s is None: return 'sin gnawty'
    st0 = e.r16(0x1029 + 2*s)
    for f in range(200):
        btn = ['RIGHT']
        if action == 'salto' and f >= delay and f < delay + 12: btn = ['RIGHT', 'B']
        if action == 'rodar' and f >= delay and f < delay + 6: btn = ['RIGHT', 'Y']
        e.set_buttons(pl, *btn)
        e.set_buttons(other, *(['UP'] if other == 2 else []))   # el otro quieto (P2 sigue unido)
        e.run(1)
        me = 0x102B if pl == 1 else 0x102D
        if e.r16(me) in (0x0D, 0x11): return 'GOLPEADO'
        if e.r16(0xD45 + 2*s) != 0x4D or e.r16(0x1029 + 2*s) != st0:
            return 'MATA (gnawty st %X)' % e.r16(0x1029 + 2*s)
    return '-'

for who in ('DK(P1)', 'Diddy(P2)'):
    for action in ('salto', 'rodar'):
        res = {}
        for d in range(0, 60, 4):
            r = trial(who, action, d)
            res.setdefault(r.split(' ')[0], []).append(d)
        print('%-10s %-6s' % (who, action), {k: len(v) for k, v in res.items()})
