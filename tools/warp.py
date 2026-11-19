"""Teletransporta a cualquier nivel (para pruebas) y guarda un savestate con los 2 Kongs.

uso: python tools/warp.py ROM ENTRANCE_ID_HEX NOMBRE [out.png]
  -> work/lvl_NOMBRE.state

Como funciona: nueva partida en "One player"; cuando el mapa fija la entrada de
Jungle Hijinxs ($3E/$40 = $16) la reemplazamos por la pedida. Ya en el nivel, el
P2 aprieta un boton (se une) y la reaparicion del parche trae al segundo Kong.
Requiere la ROM parcheada (v0.2+) para tener los 2 Kongs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu


def warp(rom, entrance, frames_after=420):
    e = Emu(rom)
    e.run(600)
    for i in range(6):
        e.tap(1, 'START', hold=3, after=120)
    e.tap(1, 'START', hold=3, after=150)          # "One player"
    patched = False
    for t in range(30):
        e.set_buttons(1, 'A'); e.run(3); e.set_buttons(1)
        for k in range(60):
            e.run(1)
            if not patched and e.r16(0x3E) == 0x16 and e.r16(0x40) == 0x16:
                e.w16(0x3E, entrance); e.w16(0x40, entrance)
                patched = True
            if patched and 1 in [e.r16(0xD45 + 2 * s) for s in range(26)]:
                break
        if patched and 1 in [e.r16(0xD45 + 2 * s) for s in range(26)]:
            break
    # P2 se une (UP no hace nada peligroso); adelantamos el contador de
    # reaparicion ($04F4) para que el 2do Kong aparezca apenas el lider pueda.
    if os.environ.get('COOP'):          # modo "Two player team" (co-op)
        e.w16(0x42, 1)
    e.set_buttons(2, 'UP')
    for i in range(frames_after):
        if e.r16(0x579) & 1 == 0 and e.r16(0x4F4) < 170:
            e.w16(0x4F4, 170)
        e.run(1)
        if e.r16(0x579) & 1 and i > 60:
            e.run(30)
            break
    e.set_buttons(2)
    return e


if __name__ == '__main__':
    rom, ent, name = sys.argv[1], int(sys.argv[2], 16), sys.argv[3]
    e = warp(rom, ent)
    open('work/lvl_%s.state' % name, 'wb').write(e.save_state())
    print('%-22s entrada %02X  DK st%02X  Diddy st%02X  579=%04X lider %X' % (
        name, ent, e.r16(0x102B), e.r16(0x102D), e.r16(0x579), e.r16(0x56F)))
    if len(sys.argv) > 4:
        e.screenshot(sys.argv[4])
