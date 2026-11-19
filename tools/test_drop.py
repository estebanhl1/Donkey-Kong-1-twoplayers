"""Deja caer a un Kong justo encima de un enemigo: ¿lo mata (pisoton)? uso: test_drop.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
e = Emu(rom); e.load_state(open('work/1p_twokongs.state', 'rb').read())
e.set_buttons(1, 'RIGHT'); e.set_buttons(2, 'RIGHT'); e.run(40)
e.set_buttons(1); e.set_buttons(2, 'UP'); e.run(2)
snap = e.save_state()
gs = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x4D][0]
for who, idx in (('DK (lider, P1)', 2), ('Diddy (comp., P2)', 4)):
    for dy in (0x20, 0x30, 0x40):
        e.load_state(snap)
        gx, gy = e.r16(0xB19 + 2*gs), e.r16(0xBC1 + 2*gs)
        other = idx ^ 6
        e.w16(0xB19 + other, (gx - 0x60) & 0xFFFF)     # el otro lejos
        res = '-'
        for f in range(40):
            if f < 2:
                gx, gy = e.r16(0xB19 + 2*gs), e.r16(0xBC1 + 2*gs)
                e.w16(0xB19 + idx, gx); e.w16(0xBC1 + idx, (gy + dy) & 0xFFFF)
                e.w16(0x1029 + idx, 1); e.w16(0xEF1 + idx, 0xFC00)   # en el aire, cayendo
            e.run(1)
            if e.r16(0x1029 + idx) in (0x0D, 0x11): res = 'GOLPEADO'; break
            if e.r16(0x1029 + 2*gs) != 0 or e.r16(0xD45 + 2*gs) != 0x4D: res = 'MATA'; break
        print('%-18s cae desde %02X px: %s' % (who, dy, res))
