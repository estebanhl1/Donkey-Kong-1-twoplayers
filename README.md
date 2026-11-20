# DKC1 – 2 jugadores simultáneos (prototipo)

Parche para *Donkey Kong Country* (SNES, USA 1.0, MD5 `30c5f292ff4cbbfcc00fd8fa96c2de3b`)
que permite que el **control 2 maneje al Kong compañero** al mismo tiempo que el control 1 maneja al líder.

## Cómo jugar
1. Abrir `Donkey Kong Country 2P (prototipo).sfc` en un emulador con 2 controles configurados
   (por ejemplo Snes9x: `flatpak install flathub com.snes9x.Snes9x`).
   También se puede aplicar `dkc_2p.ips` a tu ROM original.
   Al encender aparece una pantalla con la dedicatoria y el link del repo: cualquier botón sigue
   (o sola a los ~20 s). Está en `patch/splash.asm`.
2. Elegir **"Two player team"** en el menú: es el modo **co-op**.
   - "One player" y "Two player contest" quedan **exactamente como el juego original**.
3. Al empezar cada nivel, Diddy aparece solo a los pocos segundos (no hace falta el barril DK). Desde ahí:
   - El **P2 se une apretando cualquier botón**. Con el P2 unido: **control 1 = DK**, **control 2 = Diddy**.
     La cámara sigue el punto medio de los dos Kongs (si se separan, el borde de pantalla los mantiene juntos).
     Cualquiera de los dos puede pausar y quitar la pausa con Start.
   - **Botón A:** con los dos Kongs presentes, cualquiera de los dos jugadores aprieta A y **se intercambian
     los personajes** (el que tenía a DK pasa a Diddy y viceversa). Nadie se mueve de lugar.
   - **Indicador:** por ~2 s (al unirse el P2, al apretar A o al cambiar el líder) aparece un **1** o un **2**
     sobre cada Kong (qué jugador lo maneja) y una **banana girando** sobre el líder ("el que manda").
   - **Vagonetas:** el B de cualquiera de los dos jugadores hace saltar el carro.
   - Si el P2 no toca el control por ~4 s, se "va" y el juego vuelve a ser el original
     (P1 maneja al líder, el compañero lo sigue solo, A intercambia).
   - Con el P2 unido, el Kong del P2 también pelea (pisar o rodar sobre enemigos), recibe golpes y recoge
     racimos y letras K-O-N-G. Si golpean a un Kong, huye y reaparece junto al otro a los ~3 s.
     Si golpean al que queda solo, se pierde una vida, como en el original.
   - **Animales:** con el P2 unido, cada caja trae dos animales y cada uno monta el suyo.
   - **Cualquiera de los dos puede** colgarse de cuerdas y lianas, entrar a barriles cañón y de bonus, romper
     paredes de bonus y salir por la puerta del final: el que lo toca pasa a ser el "líder" y el otro lo sigue
     (sube detrás a la cuerda, entra con él al barril, sale con él del nivel), como en el juego original.
   - Si el Kong de un jugador cae a un hoyo y el otro sigue en pie, **no se pierde vida**: reaparece a los ~3 s.

## Estado del prototipo
Funciona:
- Movimiento independiente del compañero con la lógica original del juego.
- La cámara sigue solo al líder; el compañero no puede salir por los bordes de la pantalla.
- Si el compañero cae a un hoyo o queda muy lejos en vertical, reaparece junto al líder (sin perder vida).

Limitaciones conocidas (próximas etapas):
- En las vagonetas el Kong del P2 va escondido dentro de la vagoneta, como en el original; ahí el P2 no controla nada.
- Probado en 40 niveles de todos los mundos (`tools/survey.py`). Ver limitaciones conocidas en `ROADMAP.md`.
- **Teclado:** si juegan los dos en un mismo teclado y "correr + saltar" anula una dirección, es ghosting del teclado
  (no del juego). Usar joysticks USB o cambiar las teclas de cada jugador en el emulador.

## Preparar el entorno (desde cero)
El repo no incluye la ROM, el desensamblado ni las herramientas descargadas. Para rearmarlo:
```bash
# 1. ROM original USA 1.0 (MD5 30c5f292ff4cbbfcc00fd8fa96c2de3b) en roms/dkc_orig.sfc
mkdir -p roms work && cp "/ruta/a/Donkey Kong Country (USA).sfc" roms/dkc_orig.sfc

# 2. Desensamblado (referencia)
git clone --depth 1 https://github.com/Yoshifanatic1/Donkey-Kong-Country-1-Disassembly.git disasm

# 3. asar 1.91 (ensamblador) compilado desde el código fuente
python3 -m venv tools/venv && tools/venv/bin/pip install cmake pillow numpy
git clone --depth 1 --branch v1.91 https://github.com/RPGHacker/asar.git tools/asar_src
tools/venv/bin/cmake -S tools/asar_src/src -B tools/asar_src/build -DCMAKE_BUILD_TYPE=Release
tools/venv/bin/cmake --build tools/asar_src/build -j8
cp tools/asar_src/build/asar/bin/asar tools/asar

# 4. Núcleos libretro para las pruebas (snes9x; bsnes opcional)
for c in snes9x bsnes; do
  curl -sLO --output-dir tools https://buildbot.libretro.com/nightly/linux/x86_64/latest/${c}_libretro.so.zip
  unzip -o tools/${c}_libretro.so.zip -d tools
done

# 5. Compilar el parche y generar los savestates base de las pruebas
./build.sh
tools/venv/bin/python tools/make_states.py            # work/1p_start, work/1p_twokongs
MODE=team tools/venv/bin/python tools/make_states.py  # work/team_*
```
Algunas pruebas usan savestates extra (`work/spr_*`, `work/lvl_*`): se regeneran con `tools/warp.py` y `tools/find_sprites.py`.

## Desarrollo
- `patch/two_player.asm` – el parche (asar). `./build.sh` genera `roms/dkc_2p.sfc` y `dkc_2p.ips`.
- `disasm/` – desensamblado de DKC1 (Yoshifanatic1), usado como referencia.
- `tools/emu.py` – frontend libretro (snes9x) sin ventana para pruebas automáticas.
- `tools/scenario.py` – corre escenarios con botones de P1/P2 y guarda capturas.
- `tools/make_states.py` – genera savestates de prueba en `work/` (`MODE=team` para el modo co-op).
- `tools/regresion.sh` – **batería de regresión** (15 pruebas, ~25 s; `--completo` agrega 40 niveles). Usa `COOP=1`.
- Los scripts de prueba aceptan `COOP=1` (forzar modo co-op) y `CORE=bsnes|snes9x` (núcleo libretro).

Mapa de memoria completo: `docs/MAPA_MEMORIA.md`. Datos clave de RAM: slot de DK = índice 2, Diddy = índice 4; estado del Kong en `$1029,x`
(0 = controlado en suelo, 1 = aire, 2/5 = siguiendo al líder, 0x0C = ausente);
`$056F` = Kong líder (1 DK, 2 Diddy); botones por jugador en `$0500/$0502` (held) y `$0504/$0506` (pressed).
