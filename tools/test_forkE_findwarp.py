"""Busca barriles canon con bit $0080 (llevan a otro cuarto/bonus). uso: ROM ENT:NOMBRE ..."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
rom = sys.argv[1]
for arg in sys.argv[2:]:
    ent, name = arg.split(':')
    e = warp(rom, int(ent, 16)); e.w16(0x4F0, 0); lives = e.r16(0x575); found = None
    for t in range(4000):
        if t % 10 == 0:
            for s in range(3, 26):
                if e.r16(0xD45 + 2*s) == 0x38 and e.r16(0x145D + 2*s) & 0x80:
                    found = (s, e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s), e.r16(0x145D + 2*s))
                    open('work/warpbarrel_%s.state' % name, 'wb').write(e.save_state())
                    break
        if found: break
        e.set_buttons(1, 'RIGHT', *(['B'] if t % 30 < 10 else [])); e.set_buttons(2)
        e.run(1)
        e.w16(0x1595 + 2, 0); e.w16(0x1595 + 4, 0)
        if e.r16(0x575) < lives: break
    print('%-18s' % name, ('barril-warp slot %d en %04X,%04X props %04X' % found) if found else 'no encontrado (DK en %04X)' % e.r16(0xB1B), flush=True)
