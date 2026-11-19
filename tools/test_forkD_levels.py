"""Recorre niveles especiales con P2 unido (bot invulnerable a enemigos) y reporta rarezas.
uso: test_forkD_levels.py ROM OUTDIR ENT:NOMBRE ..."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
from PIL import Image
rom, out = sys.argv[1], sys.argv[2]
for arg in sys.argv[3:]:
    ent, name = arg.split(':'); ent = int(ent, 16)
    e = warp(rom, ent)
    lives0 = e.r16(0x575); ent0 = e.r16(0x3E)
    pst = collections.Counter(); lst = collections.Counter(); tele = 0; lastpx = None; maxdx = 0
    shots = []; stuck = 0; worst_stuck = (0, None)
    prev = None
    for t in range(3000):
        e.set_buttons(1, 'RIGHT', *(['B'] if t % 45 < 10 else []), *(['Y'] if t % 90 < 20 else []))
        e.set_buttons(2, 'RIGHT', *(['B'] if t % 37 < 9 else []))
        e.run(1)
        for k in (2, 4):
            if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
        L = e.r16(0x56F) * 2
        if L not in (2, 4): continue
        P = L ^ 6
        ps, ls = e.r16(0x1029 + P), e.r16(0x1029 + L)
        pst[ps] += 1; lst[ls] += 1
        px = e.r16(0xB19 + P); lx = e.r16(0xB19 + L)
        if lastpx is not None and abs(((px - lastpx + 0x8000) & 0xFFFF) - 0x8000) > 0x30: tele += 1
        lastpx = px
        dx = abs(((px - lx + 0x8000) & 0xFFFF) - 0x8000); maxdx = max(maxdx, dx)
        key = (ps, px, e.r16(0xBC1 + P))
        stuck = stuck + 1 if key == prev else 0
        prev = key
        if stuck > worst_stuck[0]: worst_stuck = (stuck, '%02X@%04X' % (ps, px))
        if t % 600 == 300: shots.append(e.image().resize((256, 224)))
        if e.r16(0x3E) != ent0 and t > 100: pass
    m = Image.new('RGB', (256 * len(shots), 224))
    for i, im in enumerate(shots): m.paste(im, (i * 256, 0))
    m.save(os.path.join(out, 'lvl_%s.png' % name))
    print('%-16s vidas-%d teleports=%d maxdx=%04X quieto_max=%s lider=%s comp=%s fin_x=%04X 579=%04X unido=%d' % (
        name, lives0 - e.r16(0x575), tele, maxdx, worst_stuck,
        ' '.join('%02X:%d' % (k, v) for k, v in sorted(lst.items())[:10]),
        ' '.join('%02X:%d' % (k, v) for k, v in sorted(pst.items())[:14]), e.r16(0xB19 + L), e.r16(0x579), e.r16(0x4F0)), flush=True)
