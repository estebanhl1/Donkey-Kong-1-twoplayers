"""ForkA: tomar/llevar/lanzar barril ($23) con DK o Diddy. uso: ROM STATE quien(dk|diddy)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, state, who = sys.argv[1:4]
e = Emu(rom); e.load_state(open(state, 'rb').read()); e.w16(0x4F0, 1)
idx = 2 if who == 'dk' else 4; pl = 1 if idx == 2 else 2; ty = idx - 2
def spr(i): return [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == i]
b = spr(0x23)[0]; bx, by = e.r16(0xB19 + 2*b), e.r16(0xBC1 + 2*b)
# kong a la izquierda del barril en el suelo, el otro lejos atras
e.w16(0xB19 + idx, bx - 0x28); e.w16(0xBC1 + idx, by)
e.w16(0xB19 + (idx ^ 6), bx - 0x60); e.w16(0xBC1 + (idx ^ 6), by)
e.w16(0x1A62, bx - 0x80); e.run(20)
last = None
for f in range(220):
    if f < 60: btn = ['RIGHT', 'Y']        # caminar hacia el barril con Y
    elif f < 120: btn = ['Y']              # sostener
    elif f < 125: btn = []                 # soltar Y = lanzar
    else: btn = []
    e.set_buttons(pl, *btn); e.set_buttons(3 - pl, *(['UP'] if pl == 1 else []))
    e.run(1)
    en = [(s, e.r16(0xD45+2*s), e.r16(0x1029+2*s)) for s in (5,)]
    v = (e.r16(0x1029 + idx), e.r16(0x16F5 + ty), e.r16(0x1029 + 2*b), e.r16(0xD45 + 2*b), tuple(en), e.r16(0x1029 + (idx^6)))
    if v != last:
        print('f%3d %s st%02X anim%02X 16F5=%04X otro st%02X | barril id%02X st%X %04X,%04X | slot5 %s' % (f, who, v[0], e.r16(0x10D1 + idx), v[1], v[5], v[3], v[2], e.r16(0xB19 + 2*b), e.r16(0xBC1 + 2*b), ['id%02X st%X' % x[1:] for x in en]))
        last = v
