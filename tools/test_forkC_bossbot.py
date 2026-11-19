"""Bot de jefe: un Kong salta hacia el jefe cuando esta cerca (sin teletransportes).
uso: test_forkC_bossbot.py ROM NOMBRE ENTRADA_HEX MODO(dk_lider|diddy_lider|diddy_p2) [frames]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, name, ent, mode = sys.argv[1], sys.argv[2], int(sys.argv[3], 16), sys.argv[4]
N = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
e = Emu(rom); e.load_state(open('work/lvl_B_%s.state' % name, 'rb').read())
if mode == 'diddy_lider':
    e.w16(0x56F, 2); e.w16(0x102B, 0x0C); e.w16(0x579, e.r16(0x579) & 0xFFFE); e.w16(0x4F0, 0)
    idx, pad, other_pad = 4, 1, 2
elif mode == 'dk_lider':
    e.w16(0x4F0, 0); idx, pad, other_pad = 2, 1, 2
else:
    e.w16(0x4F0, 1); idx, pad, other_pad = 4, 2, 1
hp = []; fin = None; hurt = 0; prev = None; trace = []; stomps = 0; vulf = 0
for f in range(N):
    b = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x70]
    if os.environ.get('ENEMIES'):
        en = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) not in (0, 0x70, 0x6C, 0x17, 0x0F, 0x3B, 0x69) and e.r16(0x11A1 + 2*s)]
        tgt = en if en else b
    else:
        tgt = b
    btn = []
    if tgt:
        s = tgt[0]; bx = e.r16(0xB19 + 2*s); kx = e.r16(0xB19 + idx)
        d = ((bx - kx + 0x8000) & 0xFFFF) - 0x8000
        if abs(d) > 0x50: btn = ['RIGHT' if d > 0 else 'LEFT']
        elif e.r16(0x1029 + idx) == 0 and f % 4 == 0: btn = ['B', 'RIGHT' if d > 0 else 'LEFT']
        elif e.r16(0x1029 + idx) == 1: btn = ['B', 'RIGHT' if d > 0 else 'LEFT']
        if b: hp.append(e.r16(0x14F9 + 2*b[0]))
        if b and e.r16(0x15C9 + 2*b[0]) == idx: stomps += 1; e.w16(0x15C9 + 2*b[0], 0)
        if any(e.r16(0x11A1 + 2*x) for x in b): vulf += 1
        sig = (e.r16(0x152D + 2*s), e.r16(0x11A1 + 2*s))
        if sig != prev: trace.append('f%d:%X/%X' % (f, sig[0], sig[1])); prev = sig
    e.set_buttons(pad, *btn)
    obtn = []
    if mode == 'diddy_p2' and b:          # el P1 (DK, lider) acompana a distancia para que la camara siga la pelea
        s0 = b[0]; d2 = ((e.r16(0xB19 + 2*s0) - 0x70 - e.r16(0xB1B) + 0x8000) & 0xFFFF) - 0x8000
        if abs(d2) > 0x20: obtn = ['RIGHT' if d2 > 0 else 'LEFT']
    e.set_buttons(other_pad, *obtn)
    e.run(1)
    if mode == 'diddy_p2': e.w16(0x4F0, 1)     # el P2 sigue unido aunque el bot no apriete
    for k in (2, 4):
        if e.r16(0x1595 + k): hurt += 1
        e.w16(0x1595 + k, 0)          # invulnerables para medir solo el dano al jefe
    if not os.environ.get('TANGIBLE'): e.w16(0x11A1 + (idx ^ 6), 0)      # el Kong que no ataca: intocable
    if e.r16(0x3E) != ent: fin = f; break
hps = sorted(set(hp), reverse=True)
print('%-14s %-12s vida jefe %s -> %s  %s  (golpes evitados %d, pisotones registrados %d, frames vulnerable %d)' % (name, mode, hps[0] if hps else '-', hp[-1] if hp else '-',
      ('TERMINA f%d' % fin) if fin else 'sin terminar', hurt, stomps, vulf))

if os.environ.get('TRACE'): print('   152D/11A1:', ' '.join(trace[:40]))
