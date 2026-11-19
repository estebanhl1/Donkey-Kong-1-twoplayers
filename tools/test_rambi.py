"""Rambi en Jungle Hijinxs. uso: test_rambi.py ROM QUIEN(dk|diddy) P2UNIDO(0/1) OUT.png"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
from PIL import Image
rom, who, joined, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
e = Emu(rom); e.load_state(open('work/spr_JungleHijinxs_18.state', 'rb').read())
e.w16(0x4F0, joined)
idx = 2 if who == 'dk' else 4
def slot(i):
    for s in range(3, 26):
        if e.r16(0xD45 + 2*s) == i: return s
def info():
    r = slot(9); b = slot(0x18)
    return 'f%4d DK %04X,%04X st%02X | Di %04X,%04X st%02X | lider %X 579=%04X 0512=%04X/%04X | Rambi %s caja %s vidas %d' % (
        e.frames, e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D), e.r16(0x56F),
        e.r16(0x579), e.r16(0x512), e.r16(0x514),
        ('%04X,%04X st%X' % (e.r16(0xB19+2*r), e.r16(0xBC1+2*r), e.r16(0x1029+2*r))) if r else '-',
        ('%04X,%04X' % (e.r16(0xB19+2*b), e.r16(0xBC1+2*b))) if b else '-', e.r16(0x575))
# acercar a ambos a la caja
b = slot(0x18); bx, by = e.r16(0xB19+2*b), e.r16(0xBC1+2*b)
for k in (2, 4):
    e.w16(0xB19+k, bx - (0x40 if k == idx else 0x60)); e.w16(0xBC1+k, by + 0x10)
e.w16(0x1A62, bx - 0x80)
e.run(30)
print(info())
shots = []; last = None
for f in range(500):
    if f == 5:   # dejar caer al elegido sobre la caja para romperla
        b = slot(0x18)
        if b: e.w16(0xB19+idx, e.r16(0xB19+2*b)); e.w16(0xBC1+idx, e.r16(0xBC1+2*b)+0x30); e.w16(0x1029+idx, 1); e.w16(0xEF1+idx, 0xFC00)
    r = slot(9)
    if f == 40 and r:  # y luego caer sobre Rambi
        e.w16(0xB19+idx, e.r16(0xB19+2*r)); e.w16(0xBC1+idx, e.r16(0xBC1+2*r)+0x30); e.w16(0x1029+idx, 1); e.w16(0xEF1+idx, 0xFC00)
    pl = 1 if idx == 2 else 2
    e.set_buttons(pl, *(['RIGHT'] if f > 120 else []))
    e.set_buttons(3 - pl, *(['UP'] if (3 - pl) == 2 and joined else []))
    e.run(1)
    for k in (2, 4): e.w16(0x1595+k, 0)
    r = slot(9)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x512), e.r16(0x514), (e.r16(0x1029+2*r), e.r16(0x1375+2*r)) if r else None)
    if v != last: print(info(), 'rambi1375=%s' % (('%X' % e.r16(0x1375+2*r)) if r else '-')); last = v
    if f % 50 == 0: shots.append(e.image().resize((256, 224)))
m = Image.new('RGB', (256*5, 224*2))
for i, im in enumerate(shots[:10]): m.paste(im, ((i % 5)*256, (i // 5)*224))
m.save(out)
open('work/rambi_%s_%d.state' % (who, joined), 'wb').write(e.save_state())
