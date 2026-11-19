"""Caja de Rambi en co-op llegando caminando. Casos: P2 jugando (Diddy se sube solo) y
P2 sin tocar el control (salen 2; al montar DK, Diddy recibe uno). uso: COOP=1 test_rhino_coop.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
def rams(e): return [(e.r16(0x1029+2*s), e.r16(0x1375+2*s)) for s in range(3, 26) if e.r16(0xD45+2*s) == 9]
# B: P2 jugando
e = Emu(rom); e.load_state(open('work/spr_JungleHijinxs_18.state', 'rb').read()); e.w16(0x4F0, 0)
mx = 0
for f in range(260):
    e.set_buttons(1, 'RIGHT', *(['B'] if f % 40 < 8 else [])); e.set_buttons(2, *(['RIGHT'] if f % 30 < 20 else []))
    e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    mx = max(mx, len(rams(e)))
print('B P2 jugando: animales %d, Diddy montado %s' % (mx, e.r16(0x102D) in (0x14, 0x15)))
# A: P2 sin tocar; se une; DK monta
e = Emu(rom); e.load_state(open('work/spr_JungleHijinxs_18.state', 'rb').read()); e.w16(0x4F0, 0)
mx = 0
for f in range(320):
    if f < 140: e.set_buttons(1, 'RIGHT', *(['B'] if f % 40 < 8 else []))
    else: e.set_buttons(1)
    e.set_buttons(2, *([] if f < 200 else ['UP']))
    if f == 230:
        r = [s for s in range(3, 26) if e.r16(0xD45+2*s) == 9 and e.r16(0x1029+2*s) == 0][0]
        e.w16(0xB1B, e.r16(0xB19+2*r)); e.w16(0xBC3, e.r16(0xBC1+2*r)+0x30); e.w16(0x102B, 1); e.w16(0xEF3, 0xFC00)
    e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    if f < 200: mx = max(mx, len(rams(e)))
print('A P2 sin tocar: animales al abrir %d, DK montado %s, Diddy montado %s' % (mx, e.r16(0x102B) in (0x14, 0x15), e.r16(0x102D) in (0x14, 0x15)))
