"""Recorre niveles con un bot invulnerable a enemigos buscando sprites; guarda savestates.
uso: find_sprites.py ROM IDS(hex,coma) ENTRADA:NOMBRE ..."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
rom = sys.argv[1]
ids = {int(x, 16) for x in sys.argv[2].split(',')}
for arg in sys.argv[3:]:
    ent, name = arg.split(':')
    e = warp(rom, int(ent, 16)); e.w16(0x4F0, 0)
    found = {}; lives = e.r16(0x575)
    for t in range(4000):
        if t % 10 == 0:
            for s in range(3, 26):
                i = e.r16(0xD45 + 2*s)
                if i in ids and i not in found:
                    found[i] = (e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s))
                    open('work/spr_%s_%02X.state' % (name, i), 'wb').write(e.save_state())
        e.set_buttons(1, 'RIGHT', *(['B'] if t % 30 < 10 else [])); e.set_buttons(2)
        e.run(1)
        e.w16(0x1595 + 2, 0); e.w16(0x1595 + 4, 0)      # invulnerable a enemigos
        if e.r16(0x575) < lives: break
    print('%-18s' % name, {'%02X' % k: '%04X,%04X' % v for k, v in found.items()},
          'DK llego a %04X  vidas %d' % (e.r16(0xB1B), e.r16(0x575)), flush=True)
