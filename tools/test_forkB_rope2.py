"""Cuerda vertical en Ropey Rampage, ambos Kongs cerca en el suelo; el/los que agarran saltan hacia la cuerda.
uso: test_forkB_rope2.py ROM QUIEN(dk|diddy|ambos) [P2UNIDO=1]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, who = sys.argv[1], sys.argv[2]
joined = int(sys.argv[3]) if len(sys.argv) > 3 else 1
e = Emu(rom); e.load_state(open('work/spr_RopeyRampage_30.state', 'rb').read())
e.w16(0x4F0, joined)
r = [s for s in range(3, 26) if e.r16(0xD45+2*s) == 0x30][0]
rx = e.r16(0xB19+2*r)
for idx, dx in ((2, -0x28), (4, -0x40)):
    e.w16(0xB19+idx, rx + dx); e.w16(0xBC1+idx, 0x60); e.w16(0x1029+idx, 1)
e.w16(0x1A62, rx - 0x80)
e.run(30)
grab = {'dk': [1], 'diddy': [2], 'ambos': [1, 2]}[who]
last = None
for f in range(330):
    b = {1: [], 2: ['UP'] if joined else []}
    for pl in grab:
        me = 0xB1B if pl == 1 else 0xB1D
        if f < 40: b[pl] = ['RIGHT', 'B'] if e.r16(me) < rx - 2 else ['B']
        elif 60 < f < 120: b[pl] = ['UP']          # subir
        elif 120 < f < 160: b[pl] = ['DOWN']       # bajar
        elif f == 200: b[pl] = ['RIGHT', 'B']      # saltar fuera
    if who == 'dk' and joined and 40 < f < 200: b[2] = ['LEFT'] if f % 40 < 20 else ['RIGHT']   # P2 camina en el suelo
    e.set_buttons(1, *b[1]); e.set_buttons(2, *b[2])
    e.run(1)
    for k in (2, 4): e.w16(0x1595+k, 0)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x1B01))
    if v != last:
        print('f%3d DK %04X,%04X st%02X | Di %04X,%04X st%02X | 1AFD=%04X 1AFF=%04X 1B01=%04X' % (
            f, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], e.r16(0x1AFD), e.r16(0x1AFF), v[2]))
        last = v
