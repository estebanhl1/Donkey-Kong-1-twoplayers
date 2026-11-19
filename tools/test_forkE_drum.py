"""¿Se puede parar cada Kong sobre un tambor de aceite ($25) / barril generador ($4C)? uso: ROM STATE ID"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, state, sid = sys.argv[1], sys.argv[2], int(sys.argv[3], 16)
for case in ('solo DK', 'solo Diddy', 'los dos'):
    e = Emu(rom); e.load_state(open(state, 'rb').read()); e.w16(0x4F0, 1)
    s = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == sid][0]
    dx, dy = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
    e.w16(0x1A62, dx - 0x80)
    on = {'solo DK': [2], 'solo Diddy': [4], 'los dos': [2, 4]}[case]
    for k in (2, 4):
        if k in on:
            e.w16(0xB19 + k, dx - 4 + (k - 2) * 4); e.w16(0xBC1 + k, dy + 0x30); e.w16(0x1029 + k, 0); e.w16(0xEF1 + k, 0xFE00)
        else:
            e.w16(0xB19 + k, dx - 0x40)
    for f in range(90):
        e.set_buttons(1); e.set_buttons(2, 'UP'); e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
    res = []
    for k in on:
        y = e.r16(0xBC1 + k); st = e.r16(0x1029 + k)
        res.append('%s y=%04X st%02X %s' % ('DK' if k == 2 else 'Diddy', y, st, 'ENCIMA' if abs(((y - dy) & 0xFFFF) - 0x10) < 0x20 and (y - dy) & 0x8000 == 0 else 'NO (cayo/atraveso)'))
    print('%-10s tambor y=%04X | %s' % (case, dy, ' | '.join(res)))
