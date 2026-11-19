"""Ascensor $3D: ¿lleva a cada Kong? uso: ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
for case in ('solo DK', 'solo Diddy', 'los dos'):
    e = Emu(rom); e.load_state(open('work/spr_ElevatorAnticsCP_3D.state', 'rb').read()); e.w16(0x4F0, 1)
    s = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x3D][0]
    lx, ly = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
    e.w16(0x1A62, lx - 0x80)
    on = {'solo DK': [2], 'solo Diddy': [4], 'los dos': [2, 4]}[case]
    for k in on:
        e.w16(0xB19 + k, lx - 4 + (k - 2) * 4); e.w16(0xBC1 + k, ly + 0x20); e.w16(0x1029 + k, 0); e.w16(0xEF1 + k, 0xFE00)
    for k in (2, 4):
        if k not in on and case != 'los dos':
            e.w16(0xB19 + k, lx - 0x40); e.w16(0xBC1 + k, ly + 0x20)
    rows = []
    for f in range(150):
        e.set_buttons(1); e.set_buttons(2, 'UP'); e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
        if f in (30, 90, 149):
            rows.append('f%3d ascensor y%04X | %s' % (f, e.r16(0xBC1 + 2*s), ' | '.join(
                '%s y%04X st%02X (dy %+d)' % ('DK' if k == 2 else 'Di', e.r16(0xBC1 + k), e.r16(0x1029 + k),
                ((e.r16(0xBC1 + k) - e.r16(0xBC1 + 2*s) + 0x8000) & 0xFFFF) - 0x8000) for k in on)))
    print(case); [print('   ', r) for r in rows]
