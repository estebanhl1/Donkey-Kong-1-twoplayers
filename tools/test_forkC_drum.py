import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
names = {}
for l in open('disasm/DKC1/Misc_Defines_DKC1.asm'):
    m = re.match(r'!Define_DKC1_NorSpr([0-9A-F]{2})_(\w+) = \$00([0-9A-F]{2})', l)
    if m: names[int(m.group(3), 16)] = m.group(2)
rom, mode, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
e = Emu(rom); e.load_state(open('work/lvl_B_DumbDrum.state', 'rb').read())
idx, pad, other = (2, 1, 2) if mode == 'dk' else (4, 2, 1)
e.w16(0x4F0, 0 if mode == 'dk' else 1)
last = None
for f in range(N):
    b = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x70]
    en = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) not in (0, 0x70, 0x6C, 0x17, 0x0F, 0x3B, 0x69) and e.r16(0x11A1 + 2*s)]
    tgt = en if en else b
    btn = []
    if tgt:
        s = tgt[0]; d = ((e.r16(0xB19 + 2*s) - e.r16(0xB19 + idx) + 0x8000) & 0xFFFF) - 0x8000
        if abs(d) > 0x50: btn = ['RIGHT' if d > 0 else 'LEFT']
        elif e.r16(0x1029 + idx) in (0, 1) and f % 4 == 0: btn = ['B', 'RIGHT' if d > 0 else 'LEFT']
    e.set_buttons(pad, *btn)
    ob = []
    if mode != 'dk' and tgt:
        d2 = ((e.r16(0xB19 + 2*tgt[0]) - 0x60 - e.r16(0xB1B) + 0x8000) & 0xFFFF) - 0x8000
        if abs(d2) > 0x20: ob = ['RIGHT' if d2 > 0 else 'LEFT']
    e.set_buttons(other, *ob)
    e.run(1)
    if mode != 'dk': e.w16(0x4F0, 1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    e.w16(0x11A1 + (idx ^ 6), 0)
    sig = (tuple((e.r16(0x1029 + 2*x), e.r16(0x14F9 + 2*x)) for x in b), tuple(sorted(names.get(e.r16(0xD45 + 2*x), '?') for x in en)))
    if sig != last:
        print('f%5d jefe %s | enemigos %s | DK %04X Di %04X' % (f, ['st%X v%X' % q for q in sig[0]], list(sig[1]), e.r16(0xB1B), e.r16(0xB1D)))
        last = sig
    if e.r16(0x3E) != 0xE3: print('TERMINA', f); break
