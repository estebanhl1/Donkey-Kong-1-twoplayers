"""Pruebas de los arreglos v1.2 (bugs reportados jugando). uso: COOP=1 test_v12.py ROM
Imprime una linea 'OK/FALLA nombre' por caso."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom = sys.argv[1]


def load(state):
    e = Emu(rom); e.load_state(open(state, 'rb').read()); e.w16(0x42, 1); e.w16(0x4F0, 1)
    return e


def report(name, ok, extra=''):
    print('%s %s %s' % ('OK' if ok else 'FALLA', name, extra))


def no_hits(e):
    for k in (2, 4):
        if e.r16(0x1029 + k) not in (0x0D, 0x09, 0x54, 0x0C, 0x0E, 0x0A): e.w16(0x1595 + k, 0)


# 1) Morir con un solo Kong justo antes de que reaparezca el otro: no se congela en el barril estrella
e = load('work/spr_JHmain_4A.state')
s = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x4A][0]
bx, by = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
for k in (2, 4):
    e.w16(0xB19 + k, bx - (0x30 if k == 2 else 0x40)); e.w16(0xBC1 + k, by + 0x10); e.w16(0x1029 + k, 1)
for f in range(20):
    e.w16(0x1A62, bx - 0x80); e.set_buttons(2, 'UP'); e.run(1); no_hits(e)
e.w16(0xB1B, bx); e.w16(0xBC3, by + 0x30); e.w16(0x102B, 1); e.w16(0xEF3, 0xFC00)
for f in range(60):
    e.set_buttons(2, 'UP'); e.run(1); no_hits(e)
e.w16(0x575, 5)
e.w16(0x102D, 0x0C); e.w16(0x579, e.r16(0x579) & 0xFFFE)
e.w16(0xBC3, 0xFF80); e.w16(0x102B, 1); e.w16(0x4F4, 178)
back = None
for f in range(1200):
    e.set_buttons(1, *(['A'] if 200 < f < 600 and f % 30 < 3 else [])); e.set_buttons(2, 'RIGHT'); e.run(1)
    if f > 300 and back is None and e.r16(0x579) & 1 and e.r16(0x102B) == 0 and e.r16(0x1929) == 0: back = f
report('reaparecer_en_checkpoint', back is not None, '(frame %s)' % back)

# 2) El companero cae a un hoyo: no se pierde vida y vuelve
e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(10); e.set_buttons(2)
l0 = e.r16(0x575); e.w16(0xBC5, 0xFFC8); e.w16(0x102D, 1); e.run(400)
report('hoyo_sin_perder_vida', l0 == e.r16(0x575) and e.r16(0x579) & 1 == 1 and e.r16(0x102D) == 0,
       '(vidas %d -> %d)' % (l0, e.r16(0x575)))

# 3) Estado 1 apoyado en el suelo ("patinando"): aterriza
e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(10); e.set_buttons(2)
e.w16(0x102D, 1); e.run(6)
report('no_queda_patinando', e.r16(0x102D) == 0, '(estado %02X)' % e.r16(0x102D))

# 4) El P2 se cuelga solo de la cuerda vertical (traspaso de lider)
e = load('work/spr_RopeyRampage_30.state')
r = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x30][0]; rx, ry = e.r16(0xB19 + 2*r), e.r16(0xBC1 + 2*r)
e.w16(0xB1B, rx - 0x60); e.set_buttons(2, 'UP'); e.run(30); e.set_buttons(2)
e.w16(0xB1D, rx); e.w16(0xBC5, ry + 0x20); e.w16(0x102D, 1); e.w16(0xEF5, 0); e.w16(0xE8D, 0)
e.run(30)
report('p2_cuerda_sola', e.r16(0x56F) == 2 and e.r16(0x102D) == 0x25, '(lider %d, Diddy %02X)' % (e.r16(0x56F), e.r16(0x102D)))

# 5) El P2 entra solo a un barril de bonus
e = load('work/warpbarrel_ReptileRumble.state')
c = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x38 and e.r16(0x145D + 2*s) & 0x80][0]
cx, cy = e.r16(0xB19 + 2*c), e.r16(0xBC1 + 2*c); ent0 = e.r16(0x3E)
for f in range(400):
    if f == 5:
        e.w16(0xB1B, cx - 0x30); e.w16(0xBC3, cy + 0x20); e.w16(0x102B, 1); e.w16(0xEF3, 0xFE00)
        e.w16(0xB1D, cx); e.w16(0xBC5, cy + 0x20); e.w16(0x102D, 1); e.w16(0xEF5, 0xFE00)
    e.set_buttons(2, 'UP'); e.run(1); no_hits(e)
report('p2_barril_bonus', e.r16(0x3E) != ent0 and e.r16(0x579) & 1 == 1, '(entrada %X -> %X)' % (ent0, e.r16(0x3E)))

# 6) El P2 sale solo por la puerta (casa de DK)
e = load('work/lvl_DKHouse.state'); ent0 = e.r16(0x3E)
e.w16(0xB1B, 0x60); e.w16(0xB1D, 0xB0)
for f in range(200):
    e.set_buttons(2, *(['RIGHT'] if f > 20 else ['UP'])); e.run(1)
report('p2_puerta_salida', e.r16(0x3E) != ent0, '(entrada %X -> %X)' % (ent0, e.r16(0x3E)))

# 7) A intercambia los personajes entre jugadores
e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(10); e.set_buttons(2)
e.set_buttons(1, 'A'); e.run(3); e.set_buttons(1); e.run(30)
di = e.r16(0xB1D); dk = e.r16(0xB1B)
e.set_buttons(1, 'RIGHT'); e.run(30); e.set_buttons(1)
moved = (e.r16(0xB1D) - di) & 0xFFFF, (e.r16(0xB1B) - dk) & 0xFFFF
report('a_intercambia', e.r16(0x4C4) == 1 and 0 < moved[0] < 0x100 and moved[1] == 0,
       '(intercambio %d, P1 mueve Diddy %d / DK %d)' % (e.r16(0x4C4), moved[0], moved[1]))

# 8) Etapa de bonus de animales (Rambi): no aparece el otro Kong (como en el original)
from warp import warp
e = warp(rom, 0xD2, frames_after=0); e.w16(0x4F0, 1)
extra = False
for f in range(600):
    e.set_buttons(1, 'RIGHT', *(['B'] if f % 50 < 8 else [])); e.set_buttons(2, *(['UP'] if f % 40 < 5 else []))
    e.run(1)
    if e.r16(0x579) & 1: extra = True
report('bonus_animales_sin_kong_extra', not extra and e.r16(0x3E) == 0xD2)

# 9) Si muere el Kong de un jugador, vuelve a los ~3 s aunque el lider este ocupado un rato (agachado)
e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(5)
e.w16(0x102D, 0x0C); e.w16(0x579, e.r16(0x579) & 0xFFFE)
t = None
for f in range(400):
    e.set_buttons(1, *(['DOWN'] if 60 < f < 150 else [])); e.set_buttons(2, 'UP'); e.run(1)
    if e.r16(0x579) & 1: t = f; break
report('reaparece_a_tiempo', t is not None and t <= 190, '(frame %s)' % t)

# 10) DK tambien junta bananas sueltas (antes solo contaba la caja de Diddy)
e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(5); e.set_buttons(2)
e.w16(0x56F, 2)   # Diddy lider, DK companero: DK camina solo
b0 = e.r16(0x57B)
for f in range(500):
    e.set_buttons(1, 'RIGHT', *(['B'] if f % 40 < 10 else [])); e.set_buttons(2, *([] if f % 50 else ['UP'])); e.run(1)
    for k in (2, 4): e.w16(0x1595 + k, 0)
report('dk_junta_bananas', e.r16(0x57B) > b0, '(bananas +%d)' % (e.r16(0x57B) - b0))

# 11) Cae el LIDER a un hoyo con el otro en el suelo: no se arrastra al otro ni se pierde vida
ok = True
for lead in (1, 2):
    e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(10); e.set_buttons(2)
    e.w16(0x56F, lead); e.run(2)
    L = lead * 2; P = 6 - L; l0 = e.r16(0x575)
    e.w16(0xBC1 + L, 0x0020); e.w16(0x1029 + L, 1); e.w16(0xEF1 + L, 0xFC00)
    for f in range(400):
        e.set_buttons(2, *(['UP'] if f % 30 < 3 else [])); e.run(1)
        if e.r16(0xBC1 + P) & 0x8000: ok = False
    if e.r16(0x575) != l0 or not e.r16(0x579) & 1: ok = False
report('lider_cae_sin_perder_vida', ok)

# 12) Indicador: al intercambiar con A aparecen "1"/"2" (tiles $67/$68) y la banana del lider en el OAM
e = load('work/1p_twokongs.state'); e.set_buttons(2, 'UP'); e.run(5); e.set_buttons(2); e.run(150)
e.set_buttons(1, 'A'); e.run(3); e.set_buttons(1); e.run(5)
tiles = [e.ram[0x202 + 4*i] | (e.ram[0x203 + 4*i] & 1) << 8 for i in range(128)]
report('indicador_1p_2p', 0x67 in tiles and 0x68 in tiles and any(0x1E0 <= t <= 0x1EE for t in tiles))
# 13) Vagoneta: el B del P2 tambien hace saltar el carro
e = load('work/lvl_MineCartMadness.state'); dropped = False
for f in range(1400):
    cart = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x51]
    if not dropped and cart and e.r16(0xB1B) > 0x270:
        s = cart[0]; e.w16(0xB1B, e.r16(0xB19 + 2*s)); e.w16(0xBC3, e.r16(0xBC1 + 2*s) + 0x18); e.w16(0x102B, 1); e.w16(0xEF3, 0xFE00); dropped = True
    e.set_buttons(1, *(['RIGHT'] + (['B'] if f % 24 < 10 else []) if not dropped else []))
    e.set_buttons(2, *(['UP'] if f % 20 < 2 else [])); e.run(1)
    if dropped and e.r16(0x102B) == 0x2E: break
e.run(20); jumped = False
for f in range(30):
    e.set_buttons(1); e.set_buttons(2, *(['B'] if f < 4 else [])); e.run(1)
    if e.r16(0x102B) == 0x2F: jumped = True
report('vagoneta_salta_con_p2', jumped)

# 14) Bajarse y volver a subirse a los animales no crea animales de mas (como mucho 2)
e = load('work/anim2.state'); e.set_buttons(2, 'UP'); e.run(10); e.set_buttons(2)
mx = 0
for cycle in range(3):
    e.set_buttons(1, 'A'); e.set_buttons(2, 'A'); e.run(3); e.set_buttons(1); e.set_buttons(2); e.run(60)
    free = [s for s in range(3, 26) if 9 <= e.r16(0xD45 + 2*s) <= 0xC and e.r16(0x1029 + 2*s) == 0]
    if free:
        s = free[0]; e.w16(0xB1B, e.r16(0xB19 + 2*s)); e.w16(0xBC3, e.r16(0xBC1 + 2*s) + 0x28); e.w16(0x102B, 1); e.w16(0xEF3, 0xFC00)
    for f in range(120):
        e.set_buttons(2, 'UP'); e.run(1)
        mx = max(mx, len([s for s in range(3, 26) if 9 <= e.r16(0xD45 + 2*s) <= 0xC]))
    e.set_buttons(2)
report('animales_sin_duplicar', mx <= 2, '(maximo %d)' % mx)

# 15) Etapa de animales: un solo animal; con A pasa de un jugador al otro (salta con el B del que lo tiene)
e = warp(rom, 0xD2, frames_after=0)
e.set_buttons(2, 'UP'); e.run(5); e.set_buttons(2); e.run(100)
def salta(pad):
    snap = e.save_state(); j = False
    for f in range(20):
        e.set_buttons(pad, *(['B'] if f < 4 else [])); e.run(1)
        if e.r16(0x102B) == 0x15: j = True
    e.set_buttons(pad); e.load_state(snap); return j
a = (salta(1), salta(2))
e.set_buttons(1, 'A'); e.run(3); e.set_buttons(1); e.run(30)
b = (salta(1), salta(2))
report('bonus_animales_turnarse', a == (True, False) and b == (False, True), '(antes %s, despues de A %s)' % (a, b))
