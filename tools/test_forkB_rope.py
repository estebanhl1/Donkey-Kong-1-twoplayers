"""Cuerdas en Ropey Rampage. uso: test_forkB_rope.py ROM CASO [STATE]
CASOS: dk_rope_p2_suelo | diddy_solo | orig_seguidor | ambos_misma"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, case = sys.argv[1], sys.argv[2]
state = sys.argv[3] if len(sys.argv) > 3 else 'work/spr_RopeyRampage_30.state'
e = Emu(rom); e.load_state(open(state, 'rb').read())
e.w16(0x4F0, 0 if case == 'orig_seguidor' else 1)
ropes = [s for s in range(3, 26) if e.r16(0xD45+2*s) in (0x30, 0x31)]
r = ropes[0]; rx, ry = e.r16(0xB19+2*r), e.r16(0xBC1+2*r)
print('cuerda id %02X en %04X,%04X ; DK %04X,%04X Di %04X,%04X' % (e.r16(0xD45+2*r), rx, ry, e.r16(0xB1B), e.r16(0xBC3), e.r16(0xB1D), e.r16(0xBC5)))
def put(idx, x, y):
    e.w16(0xB19+idx, x); e.w16(0xBC1+idx, y); e.w16(0x1029+idx, 1); e.w16(0xEF1+idx, 0x0000); e.w16(0xE89+idx, 0)
grab = {'dk_rope_p2_suelo': [2], 'diddy_solo': [4], 'orig_seguidor': [2], 'ambos_misma': [2, 4]}[case]
last = None
for f in range(300):
    if f == 3:
        for i, idx in enumerate(grab): put(idx, rx + (4 if i else 0), ry - 0x40 - 0x10*i)
    p1 = []; p2 = ['UP'] if case != 'orig_seguidor' else []
    if case == 'dk_rope_p2_suelo' and 60 < f < 140: p2 = ['LEFT'] if f % 40 < 20 else ['RIGHT']
    if 150 < f < 190: (p1 if 2 in grab else p2).append('UP')
    if f == 220: (p1 if 2 in grab else p2).append('B')
    e.set_buttons(1, *p1); e.set_buttons(2, *p2)
    e.run(1)
    for k in (2, 4): e.w16(0x1595+k, 0)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x1AFD), e.r16(0x1AFF), e.r16(0x1B01))
    if v != last:
        print('f%3d DK %04X,%04X st%02X | Di %04X,%04X st%02X | 1AFD=%04X 1AFF=%04X 1B01=%04X' % (
            f, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[2], v[3], v[4]))
        last = v
