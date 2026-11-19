"""El P2 carga un barril y corre: ¿se sale de la pantalla? uso: test_forkD_carry.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
e = Emu(rom); e.load_state(open('work/lvl_JHmain.state', 'rb').read()); e.w16(0x4F0, 1)
B = {0x23, 0x26, 0x27}
for t in range(400):   # ambos avanzan hasta que aparezca un barril
    e.set_buttons(1, 'RIGHT'); e.set_buttons(2, 'RIGHT'); e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    b = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) in B]
    if b: break
s = b[0]; bx, by = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
print('barril %02X en %04X,%04X' % (e.r16(0xD45 + 2*s), bx, by))
e.w16(0xB1D, bx - 0x10); e.w16(0xBC5, by + 4); e.w16(0x102D, 0)
pass
worst = 0; sts = set()
for t in range(500):
    e.set_buttons(1)
    e.set_buttons(2, 'RIGHT', 'Y')
    e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    rel = ((e.r16(0xB1D) - e.r16(0x1A62) + 0x8000) & 0xFFFF) - 0x8000
    worst = max(worst, rel); sts.add(e.r16(0x102D))
    if os.environ.get('TRAZA') and t % 20 == 0: print('  t%3d Di %04X,%04X st%02X rel %d | DK %04X,%04X st%02X cam %04X 579=%04X' % (t, e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D), rel, e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), e.r16(0x1A62), e.r16(0x579)))
print('estados de Diddy vistos', sorted('%02X' % x for x in sts), '| maximo X en pantalla de Diddy: %d (pantalla = 256)' % worst)
