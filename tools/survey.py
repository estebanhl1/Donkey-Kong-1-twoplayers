"""Recorre niveles de todos los mundos con 2 jugadores y resume como se comporta el parche.
uso: python tools/survey.py ROM OUT_DIR"""
import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
from PIL import Image, ImageDraw

LEVELS = [
 ('M1', 0x16, 'Jungle Hijinxs'), ('M1', 0x0C, 'Ropey Rampage'), ('M1', 0xEA, 'Reptile Rumble'),
 ('M1', 0xBF, 'Coral Capers'), ('M1', 0x17, 'Barrel Cannon Canyon'), ('M1', 0xE0, 'JEFE Very Gnawty'),
 ('M2', 0xD9, "Winky's Walkway"), ('M2', 0x2E, 'Mine Cart Carnage'), ('M2', 0x07, 'Bouncy Bonanza'),
 ('M2', 0x31, 'Stop & Go Station'), ('M2', 0x42, 'Millstone Mayhem'), ('M2', 0xE1, "JEFE Necky's Nuts"),
 ('M3', 0xA5, 'Vulture Culture'), ('M3', 0xA4, 'Tree Top Town'), ('M3', 0xD0, 'Forest Frenzy'),
 ('M3', 0x43, 'Temple Tempest'), ('M3', 0x0D, 'Orang-utan Gang'), ('M3', 0xDE, 'Clam City'),
 ('M3', 0xE5, 'JEFE Bumble B'),
 ('M4', 0x24, 'Snow Barrel Blast'), ('M4', 0x6D, 'Slipslide Ride'), ('M4', 0xA7, 'Ice Age Alley'),
 ('M4', 0x3E, 'Croctopus Chase'), ('M4', 0x14, 'Torchlight Trouble'), ('M4', 0xCE, 'Rope Bridge Rumble'),
 ('M4', 0xE2, 'JEFE Really Gnawty'),
 ('M5', 0x40, 'Oil Drum Alley'), ('M5', 0x2F, 'Trick Track Trek'), ('M5', 0x18, 'Elevator Antics'),
 ('M5', 0x22, 'Poison Pond'), ('M5', 0x27, 'Mine Cart Madness'), ('M5', 0x41, 'Blackout Basement'),
 ('M5', 0xE3, 'JEFE Dumb Drum'),
 ('M6', 0x30, 'Tanked Up Trouble'), ('M6', 0x12, 'Manic Mincers'), ('M6', 0x0A, 'Misty Mine'),
 ('M6', 0x36, 'Loopy Lights'), ('M6', 0x2B, 'Platform Perils'), ('M6', 0xE4, "JEFE Necky's Revenge"),
 ('K', 0x68, 'JEFE Gangplank Galleon'),
]

rom, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows, thumbs = [], []
for world, ent, name in LEVELS:
    e = warp(rom, ent)
    lead = e.r16(0x56F) * 2; part = lead ^ 6
    both = bool(e.r16(0x579) & 1)
    st0 = (e.r16(0x1029 + lead), e.r16(0x1029 + part))
    # prueba de independencia: P1 quieto, P2 derecha 40f y luego izquierda 40f
    moved = '-'
    if both:
        x0 = e.r16(0xB19 + part)
        e.set_buttons(1); e.set_buttons(2, 'RIGHT'); e.run(40)
        x1 = e.r16(0xB19 + part)
        e.set_buttons(2, 'LEFT'); e.run(40)
        x2 = e.r16(0xB19 + part)
        lx = e.r16(0xB19 + lead)
        moved = 'si' if (x1 - x0) % 65536 not in range(0, 8) or (x1 - x2) % 65536 not in range(0, 8) else 'NO'
    # juego libre ~15 s
    random.seed(ent)
    lives0 = e.r16(0x575); pst = set(); hang = False; last = None; same = 0
    for t in range(90):
        p1 = ['RIGHT'] + (['B'] if t % 5 == 0 else [])
        p2 = random.choice([['RIGHT'], ['RIGHT', 'B'], ['LEFT'], ['RIGHT', 'Y'], ['UP']])
        e.set_buttons(1, *p1); e.set_buttons(2, *p2); e.run(10)
        lead = e.r16(0x56F) * 2; part = lead ^ 6
        pst.add(e.r16(0x1029 + part))
        snap = bytes(e.ram[0x0B19:0x0B19 + 0x34])
        same = same + 1 if snap == last else 0
        last = snap
        if same > 30: hang = True
    lives1 = e.r16(0x575)
    img = e.image().resize((256, 224))
    d = ImageDraw.Draw(img); d.rectangle([0, 0, 256, 12], fill=(0, 0, 0)); d.text((2, 1), '%s %s' % (world, name), fill=(255, 255, 0))
    thumbs.append(img)
    row = (world, name, ent, 'si' if both else 'NO', '%02X/%02X' % st0, moved,
           ' '.join('%02X' % s for s in sorted(pst))[:40], lives0 - lives1, 'CONGELADO?' if hang else 'ok')
    rows.append(row)
    print('%-3s %-24s %02X  2kongs=%-2s  est=%s  P2mueve=%-2s  vidas-%d  %s  estados_comp=[%s]' % (
        row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8], row[6]), flush=True)
cols = 6
m = Image.new('RGB', (256 * cols, 224 * ((len(thumbs) + cols - 1) // cols)))
for i, im in enumerate(thumbs):
    m.paste(im, ((i % cols) * 256, (i // cols) * 224))
m.save(os.path.join(out, 'survey.png'))
