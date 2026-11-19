"""DK camina hacia la cuerda que se balancea y salta (varios tiempos). uso: ROM P2UNIDO"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, joined = sys.argv[1], int(sys.argv[2])
base = Emu(rom); base.load_state(open('work/forkB_swing.state', 'rb').read())
r = [s for s in range(3, 26) if base.r16(0xD45+2*s) == 0x31][0]
rx = base.r16(0xB19+2*r)
base.w16(0x4F0, joined)
base.w16(0xB1B, rx - 0x60); base.w16(0xBC3, 0x95); base.w16(0x102B, 1)
base.w16(0xB1D, rx - 0x80); base.w16(0xBC5, 0x95); base.w16(0x102D, 1)
base.w16(0x1A62, rx - 0xA0)
base.run(20)
snap = base.save_state()
res = []
for jt in range(0, 80, 4):
    for hold in (0, 1):
        e = base; e.load_state(snap); got = None; dropped = None
        for f in range(200):
            b = ['RIGHT'] if f < jt + 10 or not hold else []
            if jt <= f < jt + 12: b = b + ['B']
            if got is not None: b = []
            e.set_buttons(1, *b)
            e.set_buttons(2, *(['UP'] if joined else []))
            e.run(1)
            for k in (2, 4): e.w16(0x1595 + k, 0)
            st = e.r16(0x102B)
            if got is None and st in (0x25, 0x26): got = f
            if got is not None and dropped is None and st not in (0x25, 0x26) and f < got + 60: dropped = f - got
        if got is not None:
            res.append((jt, hold, got, dropped, '%02X' % e.r16(0x102D)))
print('agarres (salto, quieto?, frame, se_solto_tras, estado_Diddy):', res[:6], 'total', len(res))
