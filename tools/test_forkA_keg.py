"""ForkA: Steel Keg ($22, convertido desde el barril de Reptile Rumble). uso: ROM quien"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, who = sys.argv[1:3]
e = Emu(rom); e.load_state(open('work/spr_ReptileRumble_23.state', 'rb').read()); e.w16(0x4F0, 1)
idx = 2 if who == 'dk' else 4; pl = 1 if idx == 2 else 2; ty = idx - 2; oth = idx ^ 6
b = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x23][0]
e.w16(0xD45 + 2*b, 0x22)
bx, by = e.r16(0xB19 + 2*b), e.r16(0xBC1 + 2*b)
e.w16(0xB19 + idx, bx - 0x28); e.w16(0xBC1 + idx, by)
e.w16(0xB19 + oth, bx - 0x40); e.w16(0xBC1 + oth, by)
e.w16(0x1A62, bx - 0x80); e.run(20)
last = None; jumped = False
for f in range(300):
    if f < 20: btn = ['RIGHT', 'Y']
    elif f < 70: btn = ['Y']
    else: btn = ['B'] if 200 <= f < 204 else []
    e.set_buttons(pl, *btn)
    e.set_buttons(3 - pl, *((['RIGHT'] if f > 60 else []) + (['UP'] if pl == 1 else [])))
    if f >= 95 and not jumped and e.r16(0x1029 + 2*b) == 2 and e.r16(0xD45 + 2*b) == 0x22:   # dejar caer al Kong sobre el barril rodando
        e.w16(0xB19 + idx, e.r16(0xB19 + 2*b)); e.w16(0xBC1 + idx, e.r16(0xBC1 + 2*b) + 0x30)
        e.w16(0x1029 + idx, 1); e.w16(0xEF1 + idx, 0xFC00); jumped = True
    e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    v = (e.r16(0x1029 + idx), e.r16(0x16F5 + ty), e.r16(0x1029 + 2*b), e.r16(0xD45 + 2*b), e.r16(0x512 + ty))
    if v != last:
        print('f%3d %s st%02X anim%02X 16F5=%04X 0512=%04X %04X,%04X | keg id%02X st%X %04X,%04X 1375=%X | otro st%02X' % (
            f, who, v[0], e.r16(0x10D1 + idx), v[1], v[4], e.r16(0xB19 + idx), e.r16(0xBC1 + idx), v[3], v[2],
            e.r16(0xB19 + 2*b), e.r16(0xBC1 + 2*b), e.r16(0x1375 + 2*b), e.r16(0x1029 + oth)))
        last = v
