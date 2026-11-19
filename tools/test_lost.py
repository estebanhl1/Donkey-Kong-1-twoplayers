"""Casos en que el Kong del P2 se pierde: debe reaparecer. uso: test_lost.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
def info(e): return 'f%4d DK %04X,%04X st%02X | Di %04X,%04X st%02X | 579=%04X unido %d resp %3d vidas %d' % (
    e.frames, e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D),
    e.r16(0x579), e.r16(0x4F0), e.r16(0x4F4), e.r16(0x575))
def back(e): return e.r16(0x579) & 1 and e.r16(0x102D) in (0, 1, 0x23)

print('=== 1) Diddy cae al hoyo de Mine Cart Madness (DK se queda antes); despues el P2 NO toca nada')
e = Emu(rom); e.load_state(open('work/lvl_MineCartMadness.state', 'rb').read())
lost = None
for f in range(1100):
    dk, di = e.r16(0xB1B), e.r16(0xB1D)
    e.set_buttons(1, *(['RIGHT'] if dk < 0x250 else []), *(['B'] if f % 24 < 10 and dk < 0x250 else []))
    if lost is None:
        e.set_buttons(2, 'RIGHT', *(['B'] if f % 24 < 10 and di < 0x240 else []))
    else:
        e.set_buttons(2)
    e.run(1)
    if lost is None and e.r16(0x579) & 1 == 0: lost = f; print('  perdido:', info(e))
    if lost is not None and back(e): print('  VOLVIO a los %d frames:' % (f - lost), info(e)); break
    if f % 100 == 0: print(' ', info(e))
else:
    print('  NO VOLVIO:', info(e))

print('=== 2) golpean a Diddy; el P2 no toca nada; DK salta todo el tiempo')
e = Emu(rom); e.load_state(open('work/1p_twokongs.state', 'rb').read())
e.set_buttons(1, 'RIGHT'); e.set_buttons(2, 'RIGHT'); e.run(40)
e.set_buttons(1); e.run(60)
lost = None
for f in range(900):
    e.set_buttons(2)
    e.set_buttons(1, *(['B'] if f % 30 < 12 else []))
    for s in range(3, 26):
        if e.r16(0xD45 + 2*s) == 0x4D: e.w16(0xD45 + 2*s, 0)
    e.run(1)
    if lost is None and e.r16(0x579) & 1 == 0: lost = f; print('  perdido:', info(e))
    if lost is not None and back(e): print('  VOLVIO a los %d frames:' % (f - lost), info(e)); break
else:
    print('  NO VOLVIO:', info(e))
