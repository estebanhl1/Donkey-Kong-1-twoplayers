"""Prueba basica del co-op desde cero (sin savestates), para cualquier nucleo.
uso: CORE=bsnes python tools/test_cores.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ.pop('COOP', None)
from emu import Emu
rom = sys.argv[1]
core = os.environ.get('CORE', 'snes9x')
ok = []
def check(name, cond, extra=''):
    ok.append(cond); print('  [%s] %s %s' % ('OK' if cond else 'FALLA', name, extra))

def boot_team(entrance=None):
    e = Emu(rom); e.run(600)
    for i in range(6): e.tap(1, 'START', hold=3, after=120)
    e.tap(1, 'DOWN', hold=3, after=30); e.tap(1, 'DOWN', hold=3, after=30)
    e.tap(1, 'START', hold=3, after=150)
    ids = lambda: [e.r16(0xD45 + 2*s) for s in range(26)]
    patched = entrance is None
    for n in range(40):
        e.tap(1, 'A', hold=3, after=1)
        for k in range(60):
            e.run(1)
            if not patched and e.r16(0x3E) == 0x16 and e.r16(0x40) == 0x16:
                e.w16(0x3E, entrance); e.w16(0x40, entrance); patched = True
            if 1 in ids(): break
        if 1 in ids(): break
    return e

print('== nucleo', core)
e = boot_team()
check('modo Two player team', e.r16(0x42) == 1)
t = None
for f in range(500):
    e.run(1)
    if t is None and e.r16(0x579) & 1 and e.r16(0x102D) in (0x23, 0, 2, 5): t = f
check('Diddy aparece solo (empezar con los dos)', t is not None, '(frame %s)' % t)
e.set_buttons(2, 'LEFT'); e.set_buttons(1, 'RIGHT'); e.run(60)
dk, di = e.r16(0xB1B), e.r16(0xB1D)
check('P2 se une y mueve a Diddy por separado', e.r16(0x4F0) == 1 and di < dk - 0x30, 'DK %04X Diddy %04X' % (dk, di))
cam = e.r16(0x1A62); sdk = (dk - cam) & 0xFFFF; sdi = (di - cam) & 0xFFFF
check('camara compartida: los dos en pantalla', sdk < 256 and sdi < 256, 'DK x%d Diddy x%d' % (sdk, sdi))
e.set_buttons(2, 'UP'); e.set_buttons(1, 'RIGHT')
seen = set(); back = False
for f in range(700):
    e.run(1); seen |= {e.r16(0x102B), e.r16(0x102D)}
    if 0x0C in seen and e.r16(0x579) & 1 and e.r16(0x102B) in (0, 1, 0x23) and e.r16(0x102D) in (0, 1): back = True
    if f == 150: e.set_buttons(1)
check('golpe sin espera de turno (0x53/0x56)', not (seen & {0x53, 0x56}))
check('Kong golpeado reaparece', back or 0x0C not in seen, '(golpe visto: %s)' % (0x0C in seen))
for ent, name, stc in ((0xBF, 'Coral Capers (agua)', 0x2B), (0x17, 'Barrel Cannon Canyon', None)):
    e = boot_team(ent)
    e.set_buttons(2, 'UP')
    for i in range(420):
        if e.r16(0x579) & 1 == 0 and e.r16(0x4F4) < 170: e.w16(0x4F4, 170)
        e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)         # sin enemigos molestando
    st = e.r16(0x102D)
    x0 = e.r16(0xB1D); e.set_buttons(2, 'RIGHT')
    for i in range(40):
        e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
    x1 = e.r16(0xB1D)
    check('%s: 2 Kongs y P2 mueve' % name, e.r16(0x579) & 1 == 1 and x1 != x0, 'Diddy st%02X x %04X->%04X' % (st, x0, x1))
print('RESULTADO %s: %d/%d' % (core, sum(ok), len(ok)))
