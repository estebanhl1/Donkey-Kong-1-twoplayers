"""Ejecuta escenarios de prueba sobre una ROM, desde un savestate.
uso: python tools/scenario.py ROM STATE OUT_PNG "P1btns/P2btns*frames; ..." """
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image

rom, state, out, script = sys.argv[1:5]
every = int(sys.argv[5]) if len(sys.argv) > 5 else 10
e = Emu(rom)
e.load_state(open(state, 'rb').read())
ENEMIES = {0x4D: 'Gnawty', 0x1A: 'Klaptrap', 0x19: 'Zinger', 0x29: 'Slippa', 0x2F: 'Army', 0x4E: 'Kritter', 0x48: 'Kritter'}

def info():
    en = ' '.join('%s@%04X/%X' % (ENEMIES[e.r16(0xD45+2*s)], e.r16(0xB19+2*s), e.r16(0x1029+2*s))
                  for s in range(3, 26) if e.r16(0xD45+2*s) in ENEMIES)
    return ('DK %04X,%04X st%02X | Di %04X,%04X st%02X | cam %04X lead %X lives %d | %s' %
            (e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D),
             e.r16(0x1A62), e.r16(0x56F), e.r16(0x575), en))

shots = []
for step in [s.strip() for s in script.split(';') if s.strip()]:
    btns, n = step.split('*')
    p1, p2 = (btns.split('/') + [''])[:2]
    e.set_buttons(1, *[b for b in p1.split('+') if b])
    e.set_buttons(2, *[b for b in p2.split('+') if b])
    for i in range(int(n)):
        e.run(1)
        if e.frames % every == 0:
            print(('%-10s %-12s' % (p1, p2)), info())
            shots.append(e.image().resize((256, 224)))
cols = 6
rows = (len(shots) + cols - 1) // cols
shots = shots[:cols * 4]
rows = min(rows, 4)
m = Image.new('RGB', (256 * cols, 224 * rows))
for i, im in enumerate(shots):
    m.paste(im, ((i % cols) * 256, (i // cols) * 224))
m.save(out)
open(out.replace('.png', '.state'), 'wb').write(e.save_state())
