"""Golpe del jefe al Kong del P2: debe huir y reaparecer sin traspaso. uso: ROM NOMBRE"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, name = sys.argv[1:3]
e = Emu(rom); e.load_state(open('work/lvl_B_%s.state' % name, 'rb').read()); e.w16(0x4F0, 1)
seen = []; last = None; swap = False; froze = 0; back = None; lost = None
for f in range(2500):
    b = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x70]
    btn = []
    if b and e.r16(0x102D) in (0, 1):        # el P2 camina hacia el jefe (sin saltar) para que lo golpee
        d = ((e.r16(0xB19 + 2*b[0]) - e.r16(0xB1D) + 0x8000) & 0xFFFF) - 0x8000
        if abs(d) > 4: btn = ['RIGHT' if d > 0 else 'LEFT']
    e.set_buttons(2, *(btn or ['UP'])); e.set_buttons(1)
    e.run(1)
    e.w16(0x1595 + 2, 0)                      # DK invulnerable (solo queremos golpes al P2)
    if e.r16(0x56F) != 1: swap = True
    if e.r16(0x1929) & 0x1A and e.r16(0x102D) in (0x0D, 0x09, 0x54): froze += 1
    st = e.r16(0x102D)
    if st != last: seen.append('%02X' % st); last = st
    if lost is None and st == 0x0D: lost = f
    if lost is not None and st in (0x23,) and back is None: back = f - lost
print('%-14s estados P2: %s | traspaso:%s congelado:%d frames | reaparece: %s | DK st%02X vidas %d' % (
    name, ' '.join(seen[:16]), 'SI' if swap else 'no', froze, ('%d frames despues' % back) if back else 'no', e.r16(0x102B), e.r16(0x575)))
