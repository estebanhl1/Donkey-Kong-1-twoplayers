"""Genera savestates de prueba (con la ROM original) en work/:
   work/1p_start.state     -> modo One player, inicio de Jungle Hijinxs (solo DK)
   work/1p_twokongs.state  -> mismo nivel, despues de liberar a Diddy del barril DK
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu

rom = sys.argv[1] if len(sys.argv) > 1 else 'roms/dkc_orig.sfc'
e = Emu(rom)
e.run(600)
for i in range(6):
    e.tap(1, 'START', hold=3, after=120)
# menu de modo: "One player" ya seleccionado; MODE=team elige "Two player team"
if os.environ.get('MODE') == 'team':
    e.tap(1, 'DOWN', hold=3, after=30); e.tap(1, 'DOWN', hold=3, after=30)
e.tap(1, 'START', hold=3, after=150)
ids = lambda: [e.r16(0xD45 + 2 * s) for s in range(26)]
n = 0
while 1 not in ids() and n < 40:
    e.tap(1, 'A', hold=3, after=1)
    for k in range(60):
        e.run(1)
        if 1 in ids():
            break
    n += 1
e.run(200)
pre = 'team' if os.environ.get('MODE') == 'team' else '1p'
assert e.r16(0x42) == (1 if pre == 'team' else 0), 'modo incorrecto'
open('work/%s_start.state' % pre, 'wb').write(e.save_state())

# liberar a Diddy: caminar un poco, teletransportar a DK junto al barril DK y tomarlo
e.set_buttons(1, 'RIGHT'); e.run(70)
e.w16(0xB19 + 2, 0x0240); e.run(2)
for t in range(40):
    e.set_buttons(1, 'RIGHT', 'Y'); e.run(4)
    e.set_buttons(1); e.run(6)
    if e.r16(0x1029 + 4) != 0xC:
        break
e.set_buttons(1)
e.run(150)
print('Diddy state=%X  579=%04X  56F=%X' % (e.r16(0x102D), e.r16(0x579), e.r16(0x56F)))
open('work/%s_twokongs.state' % pre, 'wb').write(e.save_state())
e.screenshot(sys.argv[2] if len(sys.argv) > 2 else 'work/1p_twokongs.png')
