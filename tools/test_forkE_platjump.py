"""Kong salta desde el suelo a la plataforma $39 de Platform Perils y luego intenta saltar de nuevo.
uso: test_forkE_platjump.py ROM QUIEN(dk|diddy)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, who = sys.argv[1], sys.argv[2]
idx, pl = (2, 1) if who == 'dk' else (4, 2)
best = None
for start in range(0x40, 0x80, 4):
  for hold in (6, 10, 14, 18):
    e = Emu(rom); e.load_state(open('work/spr_PlatformPerils_39.state', 'rb').read()); e.w16(0x4F0, 1)
    s = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x39][0]; px, py = e.r16(0xB19+2*s), e.r16(0xBC1+2*s)
    e.w16(0x1A62, px - 0x90)
    other = idx ^ 6
    e.w16(0xB19 + idx, px - start); e.w16(0xBC1 + idx, 0x0070); e.w16(0x1029 + idx, 0)
    e.w16(0xB19 + other, px - 0x70); e.w16(0xBC1 + other, 0x0070); e.w16(0x1029 + other, 0)
    e.run(40)
    landed = None; sts = []
    for f in range(160):
        b = []
        if f < 40: b = ['RIGHT'] + (['B'] if f < hold else [])
        if 100 <= f < 110: b = ['B']
        e.set_buttons(pl, *b); e.set_buttons(3 - pl, *(['UP'] if pl == 1 else []))
        e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
        dx = (e.r16(0xB19 + idx) - e.r16(0xB19 + 2*s) + 0x8000 & 0xFFFF) - 0x8000
        on = abs(dx) < 0x18 and 0 <= (e.r16(0xBC1 + idx) - e.r16(0xBC1 + 2*s)) & 0xFFFF <= 0x0A
        if f == 99: landed = (on, e.r16(0x1029 + idx), e.r16(0xBC1 + idx))
        if f >= 100: sts.append(e.r16(0xBC1 + idx))
    if landed and landed[0]:
        jumped = max(sts) > landed[2] + 0x20
        print('%s: inicio -%02X salto %d -> sobre la plataforma en estado %02X; vuelve a saltar: %s' % (who, start, hold, landed[1], 'SI' if jumped else 'NO'))
        best = True; break
  if best: break
if not best: print(who, ': no logro subir a la plataforma con estas combinaciones')
