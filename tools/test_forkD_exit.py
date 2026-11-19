"""Bot invulnerable y a prueba de hoyos hasta la puerta de salida del nivel.
uso: test_forkD_exit.py ROM ENTRADA MODO   (MODO: solo | p2 | p2adelante | p2lider)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from warp import warp
rom, ent, mode = sys.argv[1], int(sys.argv[2], 16), sys.argv[3]
if len(sys.argv) > 4:
    from emu import Emu
    e = Emu(rom); e.load_state(open(sys.argv[4], 'rb').read()); e.run(1)
else:
    e = warp(rom, ent)
e.w16(0x4F0, 0 if mode == 'solo' else 1)
if mode == 'p2lider':   # DK ausente, Diddy lidera
    e.w16(0x102B, 0x0C); e.w16(0x579, e.r16(0x579) & 0xFFFE); e.w16(0x56F, 2); e.w16(0x4F4, 0)
ent0 = e.r16(0x3E); lives0 = e.r16(0x575); last = None; safe = {}
door = None
for t in range(9000):
    L = e.r16(0x56F) * 2
    for k in (2, 4):
        st = e.r16(0x1029 + k)
        if st == 0: safe[k] = (e.r16(0xB19 + k), e.r16(0xBC1 + k))
        if st == 0x3B and k in safe and (k == L):
            e.w16(0xB19 + k, safe[k][0] - 0x30); e.w16(0xBC1 + k, safe[k][1] + 0x10); e.w16(0x1029 + k, 1); e.w16(0xEF1 + k, 0); e.w16(0x1929, 0)
        if st not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)
    if mode == 'p2adelante':
        e.set_buttons(1, *(['RIGHT'] if t % 4 else []), *(['B'] if t % 45 < 12 else []))
        e.set_buttons(2, 'RIGHT', 'Y', *(['B'] if t % 33 < 12 else []))
    elif mode == 'p2lider':
        e.set_buttons(2, 'RIGHT', *(['B'] if t % 45 < 12 else []))
    else:
        e.set_buttons(1, 'RIGHT', *(['B'] if t % 45 < 12 else []), *(['Y'] if t % 100 < 30 else []))
        if mode != 'solo': e.set_buttons(2, 'RIGHT', *(['B'] if t % 37 < 9 else []))
    e.run(1)
    d = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x6A]
    if d and door is None: door = e.r16(0xB19 + 2*d[0]); print('puerta en x=%04X (t=%d)' % (door, t))
    if False:
        print('  t%4d 1929=%04X  DK %04X,%04X st%02X | Di %04X,%04X st%02X | 579=%04X lider %X' % (t, e.r16(0x1929), e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D), e.r16(0x579), e.r16(0x56F)))
        e._l1929 = e.r16(0x1929)
    v = (e.r16(0x102B), e.r16(0x102D), e.r16(0x56F))
    if (door is not None or os.environ.get('TRAZA')) and v != last:
        print('t%4d DK %04X,%04X st%02X | Di %04X,%04X st%02X | lider %X 579=%04X 1929=%04X ent %02X 0512=%04X/%04X resp %d' % (t, e.r16(0xB1B), e.r16(0xBC3), v[0], e.r16(0xB1D), e.r16(0xBC5), v[1], v[2], e.r16(0x579), e.r16(0x1929), e.r16(0x3E), e.r16(0x512), e.r16(0x514), e.r16(0x4F4)))
    last = v
    if e.r16(0x3E) != ent0 and t > 50:
        print('CAMBIO DE ENTRADA %02X -> %02X en t=%d (vidas perdidas %d)' % (ent0, e.r16(0x3E), t, lives0 - e.r16(0x575))); break
else:
    e.screenshot('work/stuck.png')
    import re
    names={}
    for l in open('disasm/DKC1/Misc_Defines_DKC1.asm'):
        m=re.match(r'!Define_DKC1_NorSpr([0-9A-F]{2})_(\w+) = \$00([0-9A-F]{2})',l)
        if m: names[int(m.group(3),16)]=m.group(2)
    print('cam %04X 1929=%04X 579=%04X unido %d DKst %X 12A5=%04X' % (e.r16(0x1A62), e.r16(0x1929), e.r16(0x579), e.r16(0x4F0), e.r16(0x102B), e.r16(0x12A7)), [(names.get(e.r16(0xD45+2*s),'?'),'%04X,%04X st%X'%(e.r16(0xB19+2*s),e.r16(0xBC1+2*s),e.r16(0x1029+2*s))) for s in range(3,26) if e.r16(0xD45+2*s)])
    print('NO TERMINO: DK %04X st%02X Di %04X st%02X' % (e.r16(0xB1B), e.r16(0x102B), e.r16(0xB1D), e.r16(0x102D)))
