"""Secuencia fija de botones (sin leer RAM) y capturas, para comparar nucleos.
uso: CORE=bsnes python tools/test_visual_core.py ROM OUT.png"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image
rom, out = sys.argv[1], sys.argv[2]
class E(Emu):
    def __init__(self, r):
        try: super().__init__(r)
        except RuntimeError: self.ram = None
e = E(rom)
e.run(600)
for i in range(6): e.tap(1, 'START', hold=3, after=120)
e.tap(1, 'DOWN', hold=3, after=30); e.tap(1, 'DOWN', hold=3, after=30)   # Two player team
e.tap(1, 'START', hold=3, after=150)
for i in range(5): e.tap(1, 'A', hold=3, after=60)                       # entrar a Jungle Hijinxs
shots = []
e.run(150); shots.append(e.image().resize((256, 224)))       # DK solo
e.run(300); shots.append(e.image().resize((256, 224)))       # Diddy aparecio solo
e.set_buttons(1, 'RIGHT'); e.set_buttons(2, 'LEFT'); e.run(60)
shots.append(e.image().resize((256, 224)))                   # cada uno para su lado
e.set_buttons(1, 'RIGHT'); e.set_buttons(2, 'RIGHT', 'B'); e.run(40)
shots.append(e.image().resize((256, 224)))                   # los dos avanzan, P2 salta
e.set_buttons(1); e.set_buttons(2, 'START'); e.run(3); e.set_buttons(2); e.run(40)
shots.append(e.image().resize((256, 224)))                   # P2 pausa
e.set_buttons(2, 'START'); e.run(3); e.set_buttons(2); e.set_buttons(1, 'RIGHT'); e.run(40)
shots.append(e.image().resize((256, 224)))                   # P2 quita la pausa
m = Image.new('RGB', (256 * 6, 224))
for i, im in enumerate(shots): m.paste(im, (i * 256, 0))
m.save(out)
print('ok', out)
