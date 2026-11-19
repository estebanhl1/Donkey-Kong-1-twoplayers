"""Genera patch/splash_font.asm: fuente 8x8 de 1 bit (ASCII $20-$7F) para la pantalla inicial.
Origen: cp850-8x8 de kbd (fuentes de consola de Linux). El caracter $7F se reemplaza por un corazon.
uso: python3 tools/make_font.py [/usr/lib/kbd/consolefonts/cp850-8x8.psfu.gz]"""
import gzip, struct, sys, os
src = sys.argv[1] if len(sys.argv) > 1 else '/usr/lib/kbd/consolefonts/cp850-8x8.psfu.gz'
d = gzip.open(src).read()
assert d[:4] == b'\x72\xb5\x4a\x86', 'se espera PSF2'
hs = struct.unpack('<I', d[8:12])[0]
g = d[hs:hs + 256 * 8]
glyph = lambda c: g[c * 8:c * 8 + 8]
out = ['; Generado por tools/make_font.py (fuente cp850-8x8 de kbd). Un byte por fila, ASCII $20-$7F.',
       'SplashFont:']
for c in range(0x20, 0x80):
    rows = glyph(3 if c == 0x7F else c)          # $7F -> corazon (caracter 3 de cp850)
    label = repr(chr(c)) if c < 0x7F else 'corazon'
    out.append('\tdb ' + ','.join('$%02X' % r for r in rows) + '    ; ' + label)
open(os.path.join(os.path.dirname(__file__), '..', 'patch', 'splash_font.asm'), 'w').write('\n'.join(out) + '\n')
print('OK patch/splash_font.asm')
