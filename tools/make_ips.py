"""Crea un parche IPS con las diferencias entre dos ROMs. uso: make_ips.py orig mod out.ips"""
import sys
a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
out = bytearray(b'PATCH'); i = 0
while i < len(b):
    if a[i] == b[i]:
        i += 1; continue
    j = i
    while j < len(b) and j - i < 0xFFFF and (a[j] != b[j] or (j + 1 < len(b) and a[j+1] != b[j+1])):
        j += 1
    assert i != 0x454F46  # 'EOF'
    out += i.to_bytes(3, 'big') + (j - i).to_bytes(2, 'big') + b[i:j]; i = j
out += b'EOF'
open(sys.argv[3], 'wb').write(out); print(len(out), 'bytes ->', sys.argv[3])
