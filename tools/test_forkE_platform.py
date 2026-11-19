"""Plataforma $39 (BBA64A mascara $40): ¿arrastra a cada Kong? uso: test_forkE_platform.py ROM STATE"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import Emu
rom, state = sys.argv[1], sys.argv[2]
for case in ('solo DK', 'solo Diddy', 'los dos'):
    e = Emu(rom); e.load_state(open(state, 'rb').read()); e.w16(0x4F0, 1)
    s = [s for s in range(3, 26) if e.r16(0xD45 + 2*s) == 0x39][0]
    px, py = e.r16(0xB19 + 2*s), e.r16(0xBC1 + 2*s)
    on = {'solo DK': [2], 'solo Diddy': [4], 'los dos': [2, 4]}[case]
    if case == 'solo Diddy':   # DK en el suelo cerca, para que la camara muestre la plataforma
        e.w16(0xB1B, px - 0x60); e.w16(0xBC3, 0x0070); e.w16(0x102B, 1); e.w16(0x1A62, px - 0x90)
    e.w16(0x1A62, px - 0x90)
    for k in (2, 4):
        if k in on:
            e.w16(0xB19 + k, px - 6 + (k - 2) * 6); e.w16(0xBC1 + k, py + 0x18); e.w16(0x1029 + k, 1); e.w16(0xEF1 + k, 0xFE00)
    out = []
    for f in range(200):
        e.set_buttons(1); e.set_buttons(2, 'UP'); e.run(1)
        for k in (2, 4): e.w16(0x1595 + k, 0)
        if f in (20, 100, 199):
            dp = [(e.r16(0xB19 + k) - e.r16(0xB19 + 2*s)) & 0xFFFF for k in (2, 4)]
            out.append('f%3d plat %04X,%04X | DK %04X,%04X st%02X (dx %+d) | Di %04X,%04X st%02X (dx %+d)' % (
                f, e.r16(0xB19+2*s), e.r16(0xBC1+2*s), e.r16(0xB1B), e.r16(0xBC3), e.r16(0x102B), (dp[0]+0x8000 & 0xFFFF)-0x8000,
                e.r16(0xB1D), e.r16(0xBC5), e.r16(0x102D), (dp[1]+0x8000 & 0xFFFF)-0x8000))
    print(case); [print('   ', o) for o in out]
