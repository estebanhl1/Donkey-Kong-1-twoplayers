"""Recorre un nivel de agua teletransportando al lider; busca IDs. uso: ROM ENT NOMBRE IDS"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
rom, ent, name, ids = sys.argv[1], int(sys.argv[2], 16), sys.argv[3], {int(x, 16) for x in sys.argv[4].split(',')}
e = warp(rom, ent); e.w16(0x4F0, 0)
x0, y0 = e.r16(0xB1B), e.r16(0xBC3)
found = {}
for step in range(120):
    x = x0 + step * 0x50
    for yy in (y0, (y0 - 0x60) & 0xFFFF, y0 + 0x60):
        e.w16(0xB1B, x & 0xFFFF); e.w16(0xBC3, yy)
        e.w16(0xEF3, 0); e.w16(0xE8B, 0)
        for f in range(12):
            e.set_buttons(1); e.run(1); e.w16(0x1595 + 2, 0); e.w16(0x1595 + 4, 0)
        for s in range(3, 26):
            i = e.r16(0xD45 + 2*s)
            if i in ids and i not in found:
                found[i] = (e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s), e.r16(0x1375 + 2*s))
                open('work/water_%s_%02X.state' % (name, i), 'wb').write(e.save_state())
    if len(found) == len(ids): break
print(name, {('%02X' % k): '%04X,%04X (1375=%X)' % v for k, v in found.items()}, 'x final %04X' % e.r16(0xB1B))
