"""ForkA: TNT ($27) con DK o Diddy. uso: ROM quien modo(lanzar|tocar|lanzar_cerca)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, who, mode = sys.argv[1:4]
e = Emu(rom); e.load_state(open('work/spr_Millstone_27.state', 'rb').read()); e.w16(0x4F0, 1)
idx = 2 if who == 'dk' else 4; pl = 1 if idx == 2 else 2; ty = idx - 2; oth = idx ^ 6
def spr(i): return [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == i]
t = spr(0x27)[0]; tx, ty_ = e.r16(0xB19 + 2*t), e.r16(0xBC1 + 2*t)
e.w16(0xB19 + idx, tx - 0x28); e.w16(0xBC1 + idx, ty_)
e.w16(0xB19 + oth, tx - 0x70); e.w16(0xBC1 + oth, ty_)
e.w16(0x1A62, tx - 0x80); e.run(20)
last = None
for f in range(260):
    if mode == 'tocar':
        btn = ['RIGHT']
    elif mode == 'lanzar':
        btn = ['RIGHT', 'Y'] if f < 40 else (['Y'] if f < 70 else [])
    else:  # lanzar_cerca: lanzar hacia la izquierda, al otro Kong
        btn = ['RIGHT', 'Y'] if f < 30 else (['LEFT', 'Y'] if f < 50 else [])
    e.set_buttons(pl, *btn); e.set_buttons(3 - pl, *(['UP'] if pl == 1 else []))
    e.run(1)
    ts = [(s, e.r16(0xD45+2*s), e.r16(0x1029+2*s)) for s in (6, 7)]
    v = (e.r16(0x1029 + idx), e.r16(0x1029 + oth), e.r16(0x16F5 + ty), tuple(ts), e.r16(0x56F), e.r16(0x579) & 1)
    if v != last:
        print('f%3d %s st%02X 16F5=%04X | otro st%02X | lider %X 579=%d vidas %d | %s' % (f, who, v[0], v[2], v[1], v[4], v[5], e.r16(0x575), ['s%d id%02X st%X' % x for x in ts]))
        last = v
