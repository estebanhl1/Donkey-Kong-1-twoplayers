"""Caja de animal con el P2 unido: ¿salen 2 animales y cada Kong monta el suyo?
uso: test_animals.py ROM STATE_CON_CAJA OUT.png"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image
rom, state, out = sys.argv[1:4]
box_type = int(sys.argv[4]) if len(sys.argv) > 4 else None
ANIM = {9: 'Rambi', 0xA: 'Expresso', 0xB: 'Winky', 0xC: 'Enguarde'}
e = Emu(rom); e.load_state(open(state, 'rb').read()); e.w16(0x4F0, 1)
def slots(ids): return [s for s in range(3, 26) if e.r16(0xD45 + 2*s) in ids]
def info():
    a = ' '.join('%s@%04X,%04X st%X jinete=%X' % (ANIM[e.r16(0xD45+2*s)], e.r16(0xB19+2*s), e.r16(0xBC1+2*s), e.r16(0x1029+2*s), e.r16(0x1375+2*s)) for s in slots(ANIM))
    return 'f%4d DK %04X,%04X st%02X | Di %04X,%04X st%02X | 0512=%04X/%04X | %s' % (
        e.frames, e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D), e.r16(0x512), e.r16(0x514), a)
b = slots({0x18})[0]
if box_type is not None: e.w16(0x1375 + 2*b, box_type)
bx, by = e.r16(0xB19 + 2*b), e.r16(0xBC1 + 2*b)
e.w16(0xB1B, bx - 0x40); e.w16(0xBC3, by + 0x10); e.w16(0xB1D, bx - 0x60); e.w16(0xBC5, by + 0x10)
e.w16(0x1A62, bx - 0x80); e.run(30)
shots = []
dk_done = False
def drop(idx, s):
    e.w16(0xB19 + idx, e.r16(0xB19 + 2*s)); e.w16(0xBC1 + idx, e.r16(0xBC1 + 2*s) + 0x30)
    e.w16(0x1029 + idx, 1); e.w16(0xEF1 + idx, 0xFC00)
for f in range(420):
    if f == 5: drop(2, slots({0x18})[0])                      # DK rompe la caja
    an = slots(ANIM)
    if f >= 60 and not dk_done and an and e.r16(0x102B) == 0:
        drop(2, an[0]); dk_done = True; print('animales tras abrir la caja:', len(an)); print(info())
    if f == 120 and len(an) > 1: drop(4, an[1])
    e.set_buttons(1, *(['RIGHT'] if 200 <= f < 300 else []))
    e.set_buttons(2, *(['LEFT'] if 200 <= f < 260 else (['RIGHT'] if 260 <= f < 300 else ['UP'])))
    e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    if f % 40 == 0: print(info())
    if f in (100, 180, 230, 280, 330, 400): shots.append(e.image().resize((256, 224)))
m = Image.new('RGB', (256 * 6, 224))
for i, im in enumerate(shots): m.paste(im, (i * 256, 0))
m.save(out)
open(out.replace('.png', '.state'), 'wb').write(e.save_state())
