"""Camara compartida: posicion en pantalla de cada Kong. uso: test_camera.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image
rom = sys.argv[1]
S = sys.argv[2] if len(sys.argv) > 2 else None
def scr(e, a): return ((e.r16(a) - e.r16(0x1A62) + 0x8000) & 0xFFFF) - 0x8000
for title, plan in (('DK der / Diddy izq', [('RIGHT', 'LEFT', 150)]),
                    ('ambos derecha', [('RIGHT', 'RIGHT', 150)]),
                    ('DK corre der, Diddy salta en el lugar', [('RIGHT+Y', 'B', 150)]),
                    ('DK izq / Diddy der', [('LEFT', 'RIGHT', 150)])):
    e = Emu(rom); e.load_state(open('work/1p_twokongs.state', 'rb').read())
    e.set_buttons(2, 'UP'); e.run(2)
    mins = [999, 999]; maxs = [-999, -999]; shots = []
    for p1, p2, n in plan:
        e.set_buttons(1, *p1.split('+')); e.set_buttons(2, *p2.split('+'))
        for f in range(n):
            e.run(1)
            for k in (2, 4): e.w16(0x1595 + k, 0)
            for i, a in enumerate((0xB1B, 0xB1D)):
                v = scr(e, a); mins[i] = min(mins[i], v); maxs[i] = max(maxs[i], v)
            if S and f in (50, 149): shots.append(e.image().resize((256, 224)))
    print('%-38s DK en pantalla x[%4d..%4d]  Diddy x[%4d..%4d]  final DK %d Diddy %d' % (title, mins[0], maxs[0], mins[1], maxs[1], scr(e, 0xB1B), scr(e, 0xB1D)))
    if S:
        m = Image.new('RGB', (512, 224))
        for i, im in enumerate(shots): m.paste(im, (i*256, 0))
        m.save(os.path.join(S, 'cam_%s.png' % (title.split()[0] + title.split()[1])))
