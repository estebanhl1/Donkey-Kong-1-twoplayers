# Roadmap – DKC1 2 jugadores simultáneos

Esfuerzo: **S** = horas · **M** = 1–3 días · **L** = una semana o más (tardes).
Estado: ✅ hecho · ⬜ pendiente · ❓ hay que verificar cómo se comporta hoy

## Hecho (v1.0)
- ✅ El control 2 maneja al compañero con la física original
- ✅ Cámara: con el P2 jugando sigue el punto medio de los dos (horizontal y vertical); solo, sigue al líder como el original
- ✅ El compañero no sale por los bordes de la pantalla
- ✅ El compañero reaparece junto al líder si cae a un hoyo o queda lejos en vertical
- ✅ 1.1 El P2 se une con cualquier botón y se va tras ~4 s sin input (el juego vuelve a ser el original)
- ✅ 1.5 Control fijo con el P2 unido: P1 = DK, P2 = Diddy
- ✅ 1.6 Con el P2 unido, el Kong que falta reaparece junto al líder a los ~3 s
- ✅ 1.2 El compañero mata enemigos (pisotón y rodar)
- ✅ 1.3 Los enemigos golpean al compañero: huye y reaparece a los ~3 s, sin afectar al líder
- ✅ 1.4 El compañero recoge racimos y letras K-O-N-G (y en principio globos y fichas, que usan la misma rutina)
- ✅ 3.1 Agua: el P2 nada con su Kong
- ✅ 2.6 Animales: con el P2 unido cada caja trae **dos** animales y cada Kong monta el suyo (Rambi, Expresso y Winky probados; Enguarde sin probar)
- ✅ Arreglo: el Kong del P2 vuelve aunque el P2 no toque el control mientras espera; reaparece aunque el líder salte o vaya montado; ya no se sube solo a una vagoneta ni abre bonus
- ✅ v0.6: DK ya no le quita el animal a Diddy; el P2 recupera su animal dentro del bonus y al volver; el P2 rebota en los neumáticos
- ✅ 2.2 Barriles cañón: el Kong del P2 viaja dentro del barril con el líder (como en el original); no puede entrar solo a un barril
- ✅ v0.8 (etapas 2 y 3 completas):
  - 2.1 Barriles lanzables, TNT, Steel Keg, barril DK: funcionan con el P2 sin cambios
  - 2.3 Cuerdas: el compañero ya no le suelta la cuerda al líder; sube detrás como en el original (el P2 no puede colgarse solo)
  - 2.4 / 2.7 Plataformas: tambor de aceite, barril generador y ascensor llevan a los dos Kongs
  - 2.5 Salida de nivel: el compañero sigue al líder; el evento de victoria es siempre del líder; con barril cargado no sale de pantalla
  - 2.6b Enguarde: dos Enguardes, cada uno con su jinete (probado forzando la caja; falta en un nivel de agua real)
  - 2.8 Barriles a bonus: el compañero entra y vuelve con el líder
  - 3.3 Oscuridad, semáforos, hielo y checkpoint: funcionan
  - 3.4 Jefes: el P2 daña a los 7; arreglado Very/Really Gnawty (pisotón del P2 no contaba)
- ✅ v0.9 (etapa 4):
  - 4.1 Cámara compartida (punto medio en X e Y); los dos quedan siempre en pantalla
  - 4.2 Indicador del P2: no hizo falta; con la cámara compartida, el borde y el rescate, el Kong del P2 siempre queda a la vista
  - 4.3 Botón A: no intercambia con el P2 jugando (bajarse del animal sigue igual). Pausa: cualquiera de los dos pausa y quita la pausa
  - 4.4 Ralentización: medida, el parche agrega menos del 1 % frente al original
- ✅ v1.0 (etapa 5):
  - 5.1 El co-op se activa eligiendo **"Two player team"**; "One player" y "contest" quedan idénticos al original (verificado frame a frame)
  - 5.2 En co-op, Diddy aparece solo al empezar cada nivel y tras perder una vida (no hace falta el barril DK)
  - 5.3 Probado en snes9x y bsnes (imágenes idénticas cuadro a cuadro); Mesen-S no corre en el frontend de pruebas
  - 5.4 `tools/regresion.sh`: batería de regresión en un comando
- ✅ v1.0.1: en co-op siempre salen 2 animales; el Kong del P2 se sube solo al suyo (también si el P2 se une tarde o DK monta después)
- ✅ 3.2 Vagonetas: el compañero va escondido y salta con el líder, como en el original; el reinicio tras perder una vida es correcto

- ✅ v1.1: pantalla inicial con dedicatoria y link del repo (`patch/splash.asm`)
- ✅ v1.2 (bugs reportados jugando, 2026-11-19):
  - Juego congelado al reaparecer en el barril estrella tras morir con un solo Kong (el contador de reaparición no se reiniciaba al morir)
  - Kong del P2 "patinando" (pose de caída, deslizándose sin poder saltar): quedaba en estado 1 apoyado en el suelo; ahora se aterriza
  - Al soltarse el líder de una cuerda, el Kong del P2 caía al hoyo: ahora lo sigue hasta que aterrizan
  - El P2 puede colgarse solo de cuerdas/lianas, entrar solo a barriles cañón y de bonus, romper paredes de bonus y salir por la puerta del final (traspaso de líder)
  - A intercambia los personajes entre los jugadores
  - Que el compañero caiga a un hoyo ya no cuesta una vida
- ✅ v1.2.1: en las etapas de bonus de animales (Rambi, Winky, Expresso, Enguarde) ya no aparece el otro Kong (se ponía lento);
  el Kong que falta vuelve a los ~3 s aunque el líder esté ocupado un rato (antes el contador volvía a cero)
- ✅ v1.2.2: DK también junta bananas sueltas (el juego solo revisaba la caja del último Kong procesado, Diddy)
- ✅ v1.3: si cae el líder a un hoyo, el otro sigue (antes el rescate vertical lo arrastraba al hoyo y se perdía una vida);
  indicador 1/2 + banana del líder; en la vagoneta salta el carro con el B de cualquiera de los dos
- ✅ v1.3.1: bajarse y subirse a los animales ya no crea animales de más (máximo 2); el indicador se dibuja antes que las bananas

## Revisión de mundos (2026-11-19)
40 niveles de los 6 mundos, jefes y Gangplank Galleon (`tools/survey.py`): en todos están los 2 Kongs, el P2 mueve al suyo y nada se congela.

## Limitaciones conocidas
- Mientras un Kong está colgado de una cuerda, el otro sube detrás de él (no puede usar otra cuerda a la vez).
- El que entra primero a un barril cañón se lleva al otro adentro.
- Las vagonetas siguen siendo solo del líder.
- En Torchlight Trouble la luz de Squawks sigue al líder.
- Dumb Drum: los Klumps solo los vence DK (regla del juego original).



## Etapa 5 – Pulido y distribución
| # | Mejora | Esfuerzo |
|---|--------|----------|
| 5.5 | Repo git, con las ROMs fuera del repo | S |
