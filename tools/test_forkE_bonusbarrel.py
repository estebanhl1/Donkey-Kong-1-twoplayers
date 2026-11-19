"""Barril a bonus con el P2 unido. uso: ROM STATE"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image
rom, state = sys.argv[1], sys.argv[2]
e = Emu(rom); e.load_state(open(state, 'rb').read()); e.w16(0x4F0, 1)
c = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x38 and e.r16(0x145D + 2*s) & 0x80][0]
cx, cy = e.r16(0xB19 + 2*c), e.r16(0xBC1 + 2*c)
print('destino del barril: %04X' % e.r16(0x1561 + 2*c))
last = None; shots = []
for f in range(2400):
    if f == 5:
        e.w16(0xB1B, cx); e.w16(0xBC3, cy + 0x20); e.w16(0x102B, 1); e.w16(0xEF3, 0xFE00)
    # en el bonus: caminar a la derecha y saltar (P1), el P2 sigue unido
    e.set_buttons(1, *(['RIGHT'] + (['B'] if f % 40 < 8 else []) if f > 200 else []))
    e.set_buttons(2, *(['RIGHT'] if f > 200 and f % 3 else ['UP']))
    e.run(1)
    for k in (2, 4):
        if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x3E), e.r16(0x579) & 1)
    if v != last:
        print('f%4d entrada %02X | DK %04X,%04X st%02X | Di %04X,%04X st%02X | 579=%04X vidas %d' % (f, v[2], e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], e.r16(0x579), e.r16(0x575)))
        last = v
    if f % 300 == 150 and len(shots) < 8: shots.append(e.image().resize((256, 224)))
m = Image.new('RGB', (256 * 4, 224 * 2))
for i, im in enumerate(shots): m.paste(im, ((i % 4) * 256, (i // 4) * 224))
m.save(sys.argv[3] if len(sys.argv) > 3 else 'work/bonusbarrel.png')
