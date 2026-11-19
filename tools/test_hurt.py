"""Escenarios de golpe al companero. uso: python tools/test_hurt.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]
ENEM = {0x04, 0x05, 0x06, 0x4D, 0x4E, 0x48, 0x1A, 0x19, 0x29, 0x2F}

def info(e):
    return 'f%4d DK %04X st%02X | Di %04X st%02X | lider %X 579=%04X 1929=%X resp %3d vidas %d' % (
        e.frames, e.r16(0xB1B), e.r16(0x102B), e.r16(0xB1D), e.r16(0x102D), e.r16(0x56F),
        e.r16(0x579), e.r16(0x1929), e.r16(0x4F4), e.r16(0x575))

def run(title, plan, every=20, kill_enemies_after_hit=False):
    print('===', title)
    e = Emu(rom); e.load_state(open('work/1p_twokongs.state', 'rb').read())
    hit = False
    for p1, p2, n in plan:
        e.set_buttons(1, *p1.split('+')) if p1 else e.set_buttons(1)
        e.set_buttons(2, *p2.split('+')) if p2 else e.set_buttons(2)
        for i in range(n):
            e.run(1)
            if e.r16(0x102D) == 0x0D or e.r16(0x102B) == 0x0D:
                hit = True
            if hit and kill_enemies_after_hit:
                for s in range(3, 26):
                    if e.r16(0xD45 + 2*s) in ENEM: e.w16(0xD45 + 2*s, 0)
            if e.frames % every == 0:
                print('  %-6s %-6s %s' % (p1, p2, info(e)))
    return e

# 1) Golpean a Diddy (P2). DK debe seguir normal; Diddy huye y reaparece a los ~3 s
run('Golpe al companero (Diddy), luego sin enemigos', [('RIGHT', 'RIGHT', 40), ('', 'RIGHT', 60), ('', 'UP', 330), ('LEFT', 'RIGHT', 40)], 25, True)
# 2) Golpean a Diddy y despues a DK mientras Diddy huye: DK solo -> pierde vida (como el original)
run('Golpe al companero y luego al lider', [('RIGHT', 'RIGHT', 40), ('', 'RIGHT', 60), ('', 'UP', 200)], 25)
# 3) Golpe al lider (DK) con P2 jugando: traspaso normal, DK reaparece
run('Golpe al lider (DK)', [('RIGHT', 'LEFT', 10), ('RIGHT', 'UP', 100), ('', 'UP', 280)], 25, True)
