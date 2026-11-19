"""Prueba si el companero (y como control, el lider) recoge objetos.
uso: python tools/test_pickups.py ROM STATE [frames_avance]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu

ITEMS = {0x15: 'racimo bananas', 0x16: 'letra KONG', 0x34: 'globo vida', 0x45: 'ficha animal'}
rom, state = sys.argv[1], sys.argv[2]
adv = int(sys.argv[3]) if len(sys.argv) > 3 else 0

def counters(e):
    return dict(bananas=e.r16(0x57B), kong=e.r16(0x57F), vidas=e.r16(0x575),
                fichas=bytes(e.ram[0x571:0x575]).hex())

def find_items(e):
    return [(s, e.r16(0xD45 + 2*s)) for s in range(3, 26) if e.r16(0xD45 + 2*s) in ITEMS]

base = Emu(rom); base.load_state(open(state, 'rb').read())
base.set_buttons(2, 'UP'); base.run(2)
seen = set()
# avanzar con el lider buscando objetos
for step in range(max(1, adv // 20)):
    for slot, sid in find_items(base):
        x, y = base.r16(0xB19 + 2*slot), base.r16(0xBC1 + 2*slot)
        key = (sid, x, y)
        if key in seen: continue
        seen.add(key)
        snap = base.save_state()
        res = {}
        for who, idx in (('companero', None), ('lider', None)):
            e = Emu.__new__(Emu); e = base  # reutiliza la instancia
            e.load_state(snap)
            lead = e.r16(0x56F) * 2; partner = lead ^ 6
            if who == 'companero' and not (e.r16(0x579) & 1):
                res[who] = 'sin companero'; continue
            i = partner if who == 'companero' else lead
            c0 = counters(e)
            for f in range(4):
                if who == 'companero':      # el lider cerca (para que la camara lo muestre) pero sin tocarlo
                    e.w16(0xB19 + lead, (x - 0x50) & 0xFFFF); e.w16(0xBC1 + lead, y)
                e.w16(0xB19 + i, x); e.w16(0xBC1 + i, y)
                e.w16(0x1A62, (x - 0x80) & 0xFFFF)   # camara centrada en el objeto
                e.set_buttons(2, 'UP'); e.run(1)
            e.run(10)
            gone = e.r16(0xD45 + 2*slot) != sid or (e.r16(0xB19 + 2*slot), e.r16(0xBC1 + 2*slot)) != (x, y)
            c1 = counters(e)
            diff = {k: (c0[k], c1[k]) for k in c0 if c0[k] != c1[k]}
            res[who] = ('RECOGE ' + str(diff)) if (diff or gone) else 'no'
        base.load_state(snap)
        print('%-15s en %04X,%04X -> companero: %s | lider: %s' % (ITEMS[sid], x, y, res['companero'], res['lider']))
    base.set_buttons(1, 'RIGHT'); base.set_buttons(2, 'UP')
    base.run(20)
    if base.r16(0x102B + 0) in (0x0B,): break
