"""Romper el barril checkpoint con el lider o con el companero (P2) y morir: ¿reinicia en el checkpoint?
uso: test_forkD_checkpoint.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
for who, idx in (('nadie', None), ('DK (lider)', 2), ('Diddy (P2)', 4)):
    e = Emu(rom); e.load_state(open('work/spr_JHmain_4A.state', 'rb').read()); e.w16(0x4F0, 1)
    s = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x4A][0]
    bx, by = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
    for k in (2, 4):   # los dos cerca del barril, camara centrada
        e.w16(0xB19 + k, bx - (0x30 if k == 2 else 0x40)); e.w16(0xBC1 + k, by + 0x10); e.w16(0x1029 + k, 1)
    for f in range(20):
        e.w16(0x1A62, bx - 0x80); e.set_buttons(2, 'UP'); e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
    if idx:
        e.w16(0xB19 + idx, bx); e.w16(0xBC1 + idx, by + 0x30); e.w16(0x1029 + idx, 1); e.w16(0xEF1 + idx, 0xFC00)
    for f in range(60):
        e.set_buttons(2, 'UP'); e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
    broke = e.r16(0xD45 + 2*s) != 0x4A
    # matar: los dos caen fuera del nivel
    ent0 = e.r16(0x3E)
    for k in (2, 4): e.w16(0xBC1 + k, 0xFF80); e.w16(0x1029 + k, 1)
    ents = []
    for f in range(600):
        e.set_buttons(2, 'UP'); e.run(1)
        if not ents or ents[-1] != (e.r16(0x3E), e.r16(0x2E)): ents.append((e.r16(0x3E), e.r16(0x2E)))
    print('%-11s rompe el barril: %-5s | entradas despues de morir: %s | vidas %d' % (who, broke, ' -> '.join('%02X/$2E=%02X' % x for x in ents), e.r16(0x575)))
