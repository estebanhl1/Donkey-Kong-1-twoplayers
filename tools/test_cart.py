"""Mine Cart Madness: subir a DK a la vagoneta y ver que pasa con el companero.
uso: test_cart.py ROM P2_UNIDO(0/1) OUT.png"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image
rom, joined, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
e = Emu(rom); e.load_state(open('work/lvl_MineCartMadness.state', 'rb').read())
e.w16(0x4F0, joined)
last = None; shots = []; dropped = False
for f in range(1400):
    cart = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x51]
    if not dropped and cart and e.r16(0xB1B) > 0x270:
        s = cart[0]
        e.w16(0xB1B, e.r16(0xB19 + 2*s)); e.w16(0xBC3, e.r16(0xBC1 + 2*s) + 0x18)
        e.w16(0x102B, 1); e.w16(0xEF3, 0xFE00)
        dropped = True
    if not dropped:
        e.set_buttons(1, 'RIGHT', *(['B'] if f % 24 < 10 else []))
    else:
        e.set_buttons(1, *(['B'] if f % 60 < 3 else []))
    e.set_buttons(2, *(['UP'] if joined else []))
    e.run(1)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x56F))
    if v != last:
        print('f%4d DK %04X,%04X st%02X | Di %04X,%04X st%02X | lider %X 579=%04X vidas %d cam %04X' % (
            f, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[2], e.r16(0x579), e.r16(0x575), e.r16(0x1A62)))
        last = v
    if dropped and f % 40 == 0 and len(shots) < 10:
        shots.append(e.image().resize((256, 224)))
m = Image.new('RGB', (256*5, 224*2))
for i, im in enumerate(shots): m.paste(im, ((i % 5)*256, (i // 5)*224))
m.save(out)
