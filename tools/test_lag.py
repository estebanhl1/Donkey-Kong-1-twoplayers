"""Ralentizacion: frames de logica ($28) por frame de video. uso: test_lag.py"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
S = 'work'   # carpeta con savestates extra (anim2.state)
cases = [('Jungle Hijinxs (2 Kongs)', 'work/1p_twokongs.state'), ('2 Rambis montados', S + '/anim2.state'),
         ('Oil Drum Alley', 'work/lvl_OilDrumAlley.state'), ('Platform Perils', 'work/lvl_PlatformPerils.state'),
         ('Trick Track Trek', 'work/lvl_TrickTrackTrek.state'), ('Barrel Cannon Canyon', 'work/spr_BarrelCannonCanyon_38.state'),
         ('Coral Capers (agua)', 'work/lvl_CoralCapers.state'), ('Gangplank Galleon', 'work/lvl_B_GangplankGalleon.state')]
N = 900
for name, st in cases:
    if not os.path.exists(st): continue
    res = []
    for rom, joined in (('roms/dkc_orig.sfc', 0), ('roms/dkc_2p.sfc', 1)):
        e = Emu(rom); e.load_state(open(st, 'rb').read())
        if joined: e.w16(0x4F0, 1)
        lag = 0; valid = 0
        for f in range(N):
            c0 = e.r16(0x28)
            e.set_buttons(1, 'RIGHT', *(['B'] if f % 40 < 8 else []))
            e.set_buttons(2, *(['RIGHT', 'Y'] if joined and f % 60 < 40 else (['LEFT'] if joined else [])), *(['B'] if joined and f % 50 < 8 else []))
            e.run(1)
            for k in (2, 4): e.w16(0x1595 + k, 0)
            lead = e.r16(0x56F) * 2
            normal = (e.r16(0x51A) & 0xFF) == 0x0F and e.r16(0x1029 + lead) in (0, 1, 0x14, 0x15, 0x2B, 0x2E, 0x2F, 0x28, 0x30)
            if normal:
                valid += 1
                if e.r16(0x28) == c0: lag += 1
        res.append((lag, valid))
    print('%-28s atraso en juego normal: original %3d/%3d (%.1f%%) | 2P %3d/%3d (%.1f%%)' % (
        name, res[0][0], res[0][1], 100.0*res[0][0]/max(1,res[0][1]), res[1][0], res[1][1], 100.0*res[1][0]/max(1,res[1][1])))
