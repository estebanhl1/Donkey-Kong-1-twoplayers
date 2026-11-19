#!/bin/bash
# Genera roms/dkc_2p.sfc aplicando patch/two_player.asm a una copia de la ROM original.
set -e
cd "$(dirname "$0")"
cp roms/dkc_orig.sfc roms/dkc_2p.sfc
tools/asar --fix-checksum=on patch/two_player.asm roms/dkc_2p.sfc
echo "OK -> roms/dkc_2p.sfc"
tools/venv/bin/python tools/make_ips.py roms/dkc_orig.sfc roms/dkc_2p.sfc dkc_2p.ips
