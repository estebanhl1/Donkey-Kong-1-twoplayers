"""Jefes: dejar caer repetidamente a un Kong sobre el jefe y ver si la pelea termina.
uso: test_forkC_boss.py ROM NOMBRE QUIEN(dk|diddy) [frames]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, name, who = sys.argv[1:4]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 3000
idx = 2 if who == 'dk' else 4
e = Emu(rom); e.load_state(open('work/lvl_B_%s.state' % name, 'rb').read())
e.w16(0x4F0, 1)
def bosses(): return [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x70]
ent0 = e.r16(0x3E); drops = 0; hits = 0; last_b = None; events = []
lives0 = e.r16(0x575)
for f in range(N):
    b = bosses()
    vul = [x for x in b if e.r16(0x11A1 + 2*x) != 0]
    if f % 30 == 0 and vul and e.r16(0x1029 + idx) in (0, 1):
        s = vul[0]
        bx, by = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
        e.w16(0xB19 + idx, bx); e.w16(0xBC1 + idx, by + 0x38)
        e.w16(0x1029 + idx, 1); e.w16(0xEF1 + idx, 0xFC00); drops += 1
        other = idx ^ 6
        if e.r16(0x1029 + other) in (0, 1): e.w16(0xB19 + other, bx - 0x50)
    e.set_buttons(1); e.set_buttons(2, 'UP')
    e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
    b = bosses()
    sig = tuple((e.r16(0x1029 + 2*s), e.r16(0x14F9 + 2*s)) for s in b)
    if b and last_b and sig != last_b:
        events.append('f%d %s' % (f, ' '.join('st%X/vida%X' % x for x in sig)))
    last_b = sig
    if e.r16(0x3E) != ent0 or e.r16(0x102B) == 0x63 or e.r16(0x102D) == 0x63:
        print('%-14s %-5s FIN en f%d (entrada %02X->%02X, DK st%02X Di st%02X)' % (name, who, f, ent0, e.r16(0x3E), e.r16(0x102B), e.r16(0x102D)))
        break
else:
    print('%-14s %-5s sin terminar tras %d frames (caidas %d)' % (name, who, N, drops))
print('   lider %X vidas %d->%d, Kongs st %02X/%02X, cambios del jefe: %d; primeros: %s' % (
    e.r16(0x56F), lives0, e.r16(0x575), e.r16(0x102B), e.r16(0x102D), len(events), '; '.join(events[:6])))
