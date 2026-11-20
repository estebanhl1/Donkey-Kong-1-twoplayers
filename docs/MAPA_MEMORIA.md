# Mapa de memoria – DKC1 (USA 1.0) para el hack de 2 jugadores

Lo que descubrimos investigando (desensamblado en `disasm/` + pruebas con `tools/emu.py`).
**Actualizar este archivo cada vez que confirmemos algo nuevo.**
Leyenda: ✅ confirmado en pruebas · 📖 sacado del desensamblado, sin probar · ❓ suposición

ROM: HiROM + FastROM, 4 MB, sin header. El código corre en los bancos `$80-$BF`; los datos están en `$C0-$FF`
(`$BFxxxx` = `$FFxxxx`, offset en el archivo = dirección & `$3FFFFF`).

---

## 1. RAM: variables globales

| Dirección | Tamaño | Qué es | |
|---|---|---|---|
| `$28` | w | contador de frames ❓ | 📖 |
| `$32` | w | tipo/modo de nivel ❓ (usado en Kong main: `CMP #3`, `CMP #5`) | 📖 |
| `$42` | w | modo de juego: 0 = One player, 1 = Two player team, 2 = contest | ✅ |
| `$44` | w | jugador actual (0/1) en los modos de 2P. En team se recalcula desde `$056F` | ✅ |
| `$82` | w | (DP) índice del sprite que se está procesando ("CurrentIndex") | ✅ |
| `$84` | w | (DP) tipo de Kong que se procesa: 0 = DK, 2 = Diddy | ✅ |
| `$86`, `$88` | w | (DP) temporales de índice de sprite | 📖 |
| `$7E`, `$80` | w | (DP) botones held/pressed del Kong que se procesa (los llena `CODE_BFB27C`) | ✅ |
| `$0500` / `$0502` | w | botones **mantenidos** control 1 / control 2 | ✅ |
| `$0504` / `$0506` | w | botones **recién apretados** control 1 / control 2 | ✅ |
| `$050E` / `$0510` | w | botones held/pressed "actuales" (menús y otros; **no** los usa la lógica del Kong) | ✅ |
| `$0512,y` | w×2 | por Kong (y = `$84`): índice del animal/vagoneta montado | 📖 |
| `$0516`, `$0518` | w | sprite ID del animal montado | 📖 |
| `$0535` | w | flag de debug de movimiento libre | 📖 |
| `$056F` | w | **Kong líder**: 1 = DK, 2 = Diddy (0 en algunos contextos especiales) | ✅ |
| `$0571-$0574` | b×4 | fichas de animales (Winky, Expresso, Rambi, Enguarde) | 📖 |
| `$0575` | w | vidas | ✅ |
| `$0579` | w | flags. **bit 0 = hay compañero** (sigue en 1 aunque esté escondido en la vagoneta), bit 1 = golpe en curso ❓, bit 3 = lanzado por barril cañón ❓, bit 7 (`$80`) = en vagoneta, bit `$400` = barril DK en curso ❓ | ✅ (bits 0 y 7) |
| `$057B` | w | bananas | 📖 |
| `$057F` | w | letras K-O-N-G | 📖 |
| `$1923` | w | índice del Kong líder (cache de `CODE_809B9C`) | 📖 |
| `$1929` | w | **congelamiento**: bit 0 = cámara quieta; si `AND #$1A` ≠ 0 el bucle de sprites procesa solo Kongs, barril DK y efectos (enemigos congelados). Negativo = parada de golpe (se incrementa cada frame). Golpe al líder = 3, salida de barril DK = 9, pisotón = `$FFFE` | ✅ |
| `$1A4C` | w | cámara Y ❓ | 📖 |
| `$1A62` | w | **cámara X** (con el P2 unido sigue el punto medio de los dos Kongs) (borde izquierdo de la pantalla en coordenadas del nivel). **Puede ser "negativa"** (p.ej. `$FFEE` al inicio de un nivel): comparar siempre la posición relativa con signo | ✅ |
| `$1A69` | w | anticipación horizontal de la cámara; la escribe **cada** Kong según su velocidad | ✅ |
| `$1AFD`, `$1AFF`, `$1B01` | w | estado de cuerdas/lianas (**global, no por Kong**: posible conflicto en 2P) | 📖 |
| `$1B21` | w | Y máxima alcanzada ❓ | 📖 |
| `$1E2B` | w | evento pendiente para el Kong ❓ | 📖 |

### Datos por Kong (índice y = `$84`: 0 = DK, 2 = Diddy) 📖
`$1699,y` flags · `$16AD,y` animación · `$16B9,y`/`$16BD,y` posición guardada X/Y ·
`$16C1,y` velocidad · `$16E9,y`/`$16ED,y` botones pressed/held del Kong · `$16FD,y` ❓

---

## 2. RAM: tablas de sprites

26 slots. **Índice = slot × 2** (0, 2, 4, … `$32`). Cada tabla ocupa `$34` bytes.
- **Slot 1 (índice 2) = Donkey Kong. Slot 2 (índice 4) = Diddy.** Siempre existen en los niveles, aunque estén ausentes. ✅
- Índice del compañero = índice del líder `EOR #6`. Índice del líder = `$056F × 2`. ✅

| Tabla | Qué es | |
|---|---|---|
| `$0B19,x` | posición X | ✅ |
| `$0BC1,x` | posición Y — **crece hacia ARRIBA** (saltar sube Y; velocidad Y negativa = caer; bajo el fondo del nivel da valores ~`$FExx`) | ✅ |
| `$0D45,x` | ID de sprite (1 = DK, 2 = Diddy, `$26` = barril DK, `$4D` = Gnawty, `$05` = Kritter…; ver `disasm/DKC1/Misc_Defines_DKC1.asm`) | ✅ |
| `$0E89,x` | velocidad X | ✅ |
| `$0EF1,x` | velocidad Y | ✅ |
| `$1029,x` | **estado** (máquina de estados; para Kongs ver la sección 3) | ✅ |
| `$10D1,x` | ID de animación (DK `$01-$68`, Diddy `$69-…`) | ✅ |
| `$0B8D,x` | prioridad/orden de dibujo (OAM Z) | 📖 |
| `$0C69,x` | atributos YXPPCCCT | 📖 |
| `$0D11,x` / `$0AE5,x` | pose actual / mostrada | 📖 |
| `$12A5,x` | flags de colisión con el suelo (bit 0 = en el suelo ❓) | 📖 |
| `$11A1,x` | máscara de colisión ("qué puede tocar"); los Kongs tienen `$00C1` (líder y compañero) | ✅ |
| `$1595,x` | **"recibió golpe"**: en un Kong, el enemigo lo pone en 1 (`CODE_BFC745`) y el Kong llama a la rutina de golpe; en un enemigo, el Kong lo pone en 1 al pisarlo o rodarle encima y el enemigo muere | ✅ |
| `$1375,x` | temporizador general (en `$0E`, la espera antes del traspaso = `$24`) | 📖 |
| `$0DB9,x` / `$0E21,x` | subpíxel X / Y ❓ | 📖 |

---

## 3. Estados de los Kongs (`$1029,x`)
Tabla de saltos en `DATA_BF84C5` (`$BF84C5`), un `dw` por estado.

| Estado | Significado | |
|---|---|---|
| `$00` | **controlado, en el suelo** | ✅ |
| `$01` | controlado, en el aire | ✅ |
| `$02` | compañero caminando detrás del líder | ✅ |
| `$03`, `$04` | compañero tomando el liderazgo o pasando atrás (intercambio con A) | ✅ |
| `$05` | compañero parado detrás del líder | ✅ |
| `$09` | Kong golpeado que huye | ✅ |
| `$0A` | compañero que pasa a ser líder tras el golpe | ✅ |
| `$0B` | muerto o cayendo al morir | ✅ |
| `$0C` | **ausente** (no está en el nivel); su rutina es solo RTL | ✅ |
| `$0D` / `$0E` | líder golpeado / compañero reaccionando | ✅ |
| `$11` | golpe/rebote ❓ | ✅ (visto) |
| `$12`, `$13` | cuerdas / lianas ❓ | ✅ (vistos) |
| `$14` | **montando un animal (suelo)** — lee botones; `$0512,y` = índice del animal | ✅ |
| `$15` | montando un animal (en el aire) | ✅ |
| `$16` | subiéndose a un animal (animación) | ✅ |
| `$1F` → `$20` → `$24` | embistió una **pared de bonus** (sprite `$14`): avanza recto y espera el cambio de cuarto | ✅ |
| `$46`, `$47`, `$48`, `$32` | entrando o saliendo de un cuarto (bonus o nivel) | ✅ (vistos) |
| `$23` | saliendo de un barril DK (lo pone `CODE_BFC9CA`) | ✅ |
| `$25` | visto en Slipslide Ride (hielo/pendiente) ❓ | ✅ (visto) |
| `$29` | **entrando a un barril cañón** (lo pone el barril, `$BFE41B`) | ✅ |
| `$28` | dentro del barril cañón **y también volando** tras el disparo (hasta aterrizar) | ✅ |
| `$35` | compañero **dentro del mismo barril** que el líder (lo pone el estado `$02` en `CODE_BF8A22`) | ✅ |
| `$33` / `$34` | compañero subiendo a una cuerda tras el líder (líder en `$26` / `$25`) | 📖 |
| `$2E` | **en la vagoneta** (enciende el bit `$80` de `$0579`); el compañero va escondido en `$0C` | ✅ |
| `$2F` | **saltando con la vagoneta**; el compañero aparece en `$02` y salta con él | ✅ |
| `$3B` | cayendo a un hoyo / fuera del nivel (muerte) | ✅ |
| `$40` | en el aire tras salir de la vagoneta (controlado) | ✅ |
| `$30` | **montando a Enguarde** (`$4C` subiéndose); Enguarde montado = estado 4 | ✅ |
| `$2B` | **nadando, controlado** (lee botones con `CODE_BFB27C`, handler `$0F`) — `CODE_BF9763` | ✅ |
| `$32` | visto en Vulture Culture / Torchlight / Trick Track Trek ❓ | ✅ (visto) |
| `$36` | **nadando detrás del líder** (compañero en el agua) — `CODE_BF9A7D` | ✅ |
| `$3B` | fuera del nivel / caída ❓ | ✅ (visto) |
| `$53` | **esperando que el jugador apriete un botón** (modo 2P team/contest, Kong parpadeando) | ✅ |
| `$54` | huyendo, fase final ❓ | ✅ (visto) |

---

## 4. ROM: rutinas importantes

| Dirección | Qué hace | |
|---|---|---|
| `$80A257` | lee los controles: llena `$0500-$0506` y luego `$050E/$0510` según `$42/$44` | 📖 |
| `$809B9C` (JSL) / `$809BA0` (JSR) | devuelve en Y el índice del Kong líder. **~95 llamadas**: es la clave de "enemigos solo vs líder" | 📖 |
| `$BF8159` / `$BF8171` | bucle principal de sprites: `JMP (DATA_BF8177,x)` con x = ID × 4 | ✅ |
| `$BF8177` | tabla de rutinas de sprite (4 bytes por ID: `dw rutina, flags`). DK en `$BF817B`, Diddy en `$BF817F` | ✅ |
| `$BF849F` / `$BF84A6` | entrada original de Diddy / DK (ponen `$84`) → **cuerpo común `$BF84A8`** (termina en RTL) | ✅ |
| `$BF84C5` | tabla de estados del Kong | ✅ |
| `$BF874A` | estado 0 (controlado en el suelo) | ✅ |
| `$BF8DEA` | estado `$0A` (el compañero toma el liderazgo) | 📖 |
| `$BFB27C` | procesa botones del Kong: elige el control con `$44` en `$BFB2C7` (`LDA $44 / ASL / TAY`) y despacha según `$180F` | ✅ |
| `$BBA4C8` (JSL, A = n.º de caja) | arma la caja de colisión del sprite actual en `$A6-$AC` | 📖 |
| `$BBA564` (JSR) | índice del líder (`$056F × 2`, 2 por defecto) | ✅ |
| `$BBA574` (JSL, A = máscara) | **"¿toca al jugador?"** (**parcheada**: con el P2 unido acepta a ambos Kongs). Original: recorre desde el líder hacia abajo y solo acepta al **líder**. La usan **30 llamadas** (objetos y enemigos). Carry = toca, `$88` = índice del Kong | ✅ |
| `$BBA58D` (JSL) | igual, pero revisa los sprites `$02`-`$1C` (14 llamadas) | ✅ |
| `$BBA64A` (JSL, A = máscara, Y = caja) | "¿toca al jugador?" con caja fija `DATA_BBA534`: **neumáticos** (máscara `$80`) y **plataformas** (`$40`). Original: solo el líder. **Parcheada**: líder primero y, si no toca, el compañero | ✅ |
| `$BBA663` (JSL) | igual, pero revisa todos los sprites (plataformas de riel `$58`: ya llevaban a los dos Kongs en el original) | ✅ |
| `$BF888E` / `$BF88AD` | montar un animal (lado del Kong). **Parcheado en `$BF88AD`**: no se puede montar un animal que tiene otro jinete | ✅ |
| `$B88429` | salir de un cuarto hacia un bonus: si el líder va montado, guarda el animal (`$055D = $0516`). **Parcheado**: también recuerda el animal del P2 | ✅ |
| `$80838C` | carga de un cuarto: si viene de un bonus (bit `$40` de `$1E15`) devuelve el animal al líder; si no, borra `$0512`/`$0514`. **Parcheado**: devolución también al P2 | ✅ |
| `$8085B7` / `$80855D` | preparan al líder (con animal si `$0512` ≠ 0) y al compañero (siempre a pie) al empezar un cuarto | 📖 |
| `$BBA594` | bucle de choque: sprite x con `($B8 AND $11A1,x) != 0` y cajas superpuestas | ✅ |
| `$BFA17E` (JSR) | **rutina de golpe al Kong** (ver 6a) | ✅ |
| `$BFA712` / `$BFA75D` | pisotón del Kong | ✅ |
| `$BFC703` / `$BFC745` | choque enemigo→Kong / marcar golpe al Kong | ✅ |
| `$BFC9CA` (JSR) | **saca al Kong que falta** en la posición del sprite `$82` (barril DK): estado `$23`, pone el bit 0 de `$0579` | ✅ |
| `$BFCE93` | rutina del barril DK/TNT | 📖 |
| `$BF849E` | un `RTL` suelto (útil para llamar rutinas JSR del banco BF desde otro banco) | ✅ |
| `$BE80A4` | asigna una animación al sprite actual | 📖 |

---

## 5. Espacio libre

### ROM
| Rango | Tamaño | Uso |
|---|---|---|
| `$CA6C61-$CA7FFF` | 5023 B (todo en `$00`) | **nuestro código** desde `$CA7000` (v0.9 termina ~`$CA7900`) |
| `$CEFF50`, `$D2FE8C` | 176 B, 372 B | libre (`%FREE_BYTES` del desensamblado) |
| banco `$BF8000-$BFFFFF` | **0 B libres** | usar trampolines (JML) hacia `$CA` |

Más espacio: buscar `%FREE_BYTES` en `disasm/DKC1/Routine_Macros_DKC1.asm`.

### RAM
| Rango | Uso |
|---|---|
| `$0420-$04FF` | **libre**: justo después del buffer OAM (`$0200-$041F`); ninguna instrucción lo referencia y nunca cambió en las pruebas |
| `$04F0` | ⟵ nuestro: P2 unido (0/1) |
| `$04F2` | ⟵ nuestro: frames sin input del P2 |
| `$04F4` | ⟵ nuestro: contador de reaparición |
| `$04EC` | ⟵ nuestro: animal (ID) que montaba el P2 al entrar al último bonus |
| `$04EE` | ⟵ nuestro: devolución del animal del P2 pendiente |
| `$04F6` | ⟵ nuestro: tiempo máximo para la devolución (frames) |
| `$04FC` / `$04FE` | ⟵ nuestro: X/Y del líder guardadas mientras se calcula la cámara compartida |
| `$04D2` | ⟵ nuestro: control 2 leído del hardware el frame anterior (pausa) |
| `$04F8` | ⟵ nuestro: `TouchMode` de `CODE_BBA64A` (0 normal, 1 solo líder, 2 solo compañero) |
| `$04C0` | ⟵ nuestro: `$5A` mientras se muestra la pantalla inicial (`patch/splash.asm`; los tests la saltan) |
| `$04C4` | ⟵ nuestro: personajes intercambiados con A (0: P1 = DK / P2 = Diddy; 1: al revés) |
| `$04C6` | ⟵ nuestro: espera entre dos intercambios con A (20 frames) |
| `$04C8` | ⟵ nuestro: frames seguidos con el líder en el suelo (no en el aire / cuerda / barril) |
| `$04CA` | ⟵ nuestro: frames con el compañero en estado 1 pero apoyado en el suelo |
| `$04A0`-`$04A7` | ⟵ nuestro: caja de Diddy mientras se revisan las bananas con la de DK |
| `$04B0`-`$04B7` | ⟵ nuestro: caja de colisión de DK (`$C5`-`$CC`) guardada antes de procesar a Diddy |
| `$04BA` / `$04BC` | ⟵ nuestro: caja de DK válida este frame / alternancia de la caja para bananas |
| `$04BE` / `$04C2` | ⟵ nuestro: frames del indicador 1/2 / líder del frame anterior (para mostrarlo al cambiar) |
| `$04CC` | ⟵ nuestro: frames con el compañero siguiendo al líder (estado 2); a los 90 recupera el control |
| `$04FA` | ⟵ nuestro: `$1E2B` guardado mientras se procesa al compañero |
| `$04D8-$04DD` | ⟵ nuestro: copias de `$1AFD`/`$1AFF`/`$1B01` mientras se procesa al compañero |
| `$04E0-$04EB` | ⟵ nuestro: copias temporales mientras se procesa al compañero (cámara, índice, estado, `$1375`, `$11A1` del líder y `$1929`) |

**No usar** (parecen libres pero no lo están):
- `$7E2000-$7EFFFF`: buffers (descompresión en `$7E79FC`, tablas HDMA/BG hasta `$7EFFxx`). Que en Jungle Hijinxs no se toquen no significa que estén libres en otros niveles.
- `$7F0000-…`: datos de nivel (refs. explícitas hasta `$7F37D5` y también `$7FFFE0`).
- `$0100-$01FF`: pila (S = `$01FF`; a veces `$02FE`).
- El desensamblado cambia el DP (`TCD`) a la base de una tabla de sprites en los scripts de aparición (`$B58064`), no a otras zonas.

---

## 6. Comportamientos del juego útiles
- Siempre se parte **solo con DK**; Diddy está en el primer barril DK de Jungle Hijinxs (x ≈ `$0275`).
- Los enemigos solo chocan con el líder (el compañero los atraviesa). ✅
- Golpe al líder con compañero presente: el líder huye (`$09`→`$54`→`$0C`), el compañero pasa a líder y `$056F` cambia; perder un Kong **no** cuesta vida. ✅
- El intercambio con A solo funciona si el compañero está en un estado de "seguir" (`$02`/`$05`). ✅
- Modo team (`$42` = 1): al cambiar de turno, el Kong queda en `$53` hasta que el jugador apriete algo. ✅

## 6a. Golpes (verificado 2026-11-19)
1. El **enemigo** (por ejemplo `CODE_BFC703`) usa `CODE_BBA574` para ver si toca a un Kong.
   Si el Kong está en el suelo, o viene de lado o de abajo, le pone `$1595` en 1 (`CODE_BFC745`). Si cae desde arriba, no hace nada.
2. El **Kong** ve su `$1595` y llama a `CODE_BFA17E`:
   - **con compañero** (bit 0 de `$0579`): el golpeado pasa a `$0D`, `$1929 = 3` y **fuerza al otro a `$0E`**;
   - **solo**: pasa a `$11` y luego `$0B` (muere, se pierde una vida).
3. El otro, en `$0E` (espera de `$24` frames), pasa a `$0A`. En `$0A` (`CODE_BF8DEA` → `CODE_BF8E48`) toma el liderazgo: invierte `$056F` con `EOR #3`, apaga el bit 0 de `$0579` y pone `$1929 = 0`.
4. El golpeado: `$0D` → `$09` (huye) → `$54` → `$0C` (ausente).
- **Pisotón** (lado del Kong): `CODE_BFA712`/`CODE_BFA75D` se llaman desde los estados 0 y 1. Revisan con `CODE_BBA58D` (máscara 3) los sprites de índice ≥ 6 que toca el Kong, les ponen `$1595 = 1` y el Kong rebota. **Funciona igual para el compañero.** ✅
- **Rodar** también mata para el compañero. ✅
- **Nuestro parche:** `CODE_BBA574` acepta a ambos Kongs si el P2 está unido. Si golpean al compañero, deshacemos el `$0E` forzado al líder y el `$1929`, y apagamos el bit 0 de `$0579`.
  El compañero huye y reaparece. Si golpean al líder mientras el compañero huye, el líder muere, igual que en el original.

## 6a-bis. Vagonetas (verificado 2026-11-19)
- El juego esconde solo al compañero (`$0C`) cuando el líder sube a la vagoneta (`$2E`), aunque el P2 lo controle, y mantiene el bit 0 de `$0579`.
- En cada salto (`$2F`) el compañero aparece en `$02` y salta con el líder. **Hay que dejarlo con su lógica original.**
  Si se convierte en "controlado", o si cuenta para los choques, cae en la vagoneta en lugar del líder y el líder muere.
- Tras perder una vida en la vagoneta, el nivel se reinicia con **los dos Kongs**, igual en el original que en el parche.
- **Regla del parche:** si el líder está en `$2E`/`$2F`, el compañero usa la rutina original y no cuenta para los choques
  (`P2_PartnerIsPlayer`: tampoco cuenta si está en `$02`, `$05`, `$06`, `$0C` o `$36`).
- **No apagar** el bit 0 de `$0579` solo porque el compañero esté en `$0C`: en la vagoneta está escondido, no ausente (era un error de la v0.3).

## 6a-ter. Animales (verificado 2026-11-19)
- Los 4 animales (`$09` Rambi, `$0A` Expresso, `$0B` Winky, `$0C` Enguarde) comparten la rutina `$BFCABF`.
  Estado del animal: 0 = libre, 1 = montado (sigue al jinete `$1375,x` con `CODE_BFC8CB`), 2 = huyendo tras un golpe.
- **Montar** (lado del Kong, estado 1): `CODE_BF888E` revisa con `CODE_BBA58D` (máscara 8) el animal que toca. Pone `$0512,y` (y = `$84`) = índice del animal,
  `$1375` del animal = índice del Kong, `$1595` del animal = 8 (→ estado 1) y el Kong pasa a `$16`, luego a `$14`.
  **Una segunda señal `$1595 = 8` a un animal ya montado lo baja** (estado 0). Pasa si el Kong "se monta dos veces", por ejemplo al tomar el liderazgo.
- **Caja de animal** (sprite `$18`): al abrirse, `CODE_BED058` lee el tipo en `$1375` de la caja (0 Rambi, 1 Expresso, 2 Winky, 3 Enguarde, 4+ Squawks)
  y crea el animal con `LDY #guion : JSL CODE_B5804C` (llamadas en `$BED080` Enguarde, `$BED08C` Rambi, `$BED098` Expresso, `$BED0A4` Winky, `$BED06D` Squawks).
- **Creación de sprites:** `CODE_B5804C` = sprite nuevo en un slot **bajo** (`$02`-`$1C`, con video). `CODE_B5802F` = sprite nuevo en un slot **alto** (`$1E`-`$32`, efectos).
  ⚠ `CODE_BBA58D` empieza en `$88 = $1E`, así que **no ve los slots altos**: un animal creado ahí no se puede montar.
- En el original el compañero **sigue a pie** al líder montado. Al cambiar de cuarto el juego devuelve el animal **solo al líder**.
- **Parche:** con el P2 unido, la caja crea 2 animales (el segundo 0x28 px a la derecha). Cada Kong monta el suyo.
  Si golpean al jinete del P2, se cae y su animal huye, sin traspaso.
  Reparaciones: `P2_CheckPartnerAnimal` borra un `$0514` que ya no apunta a un animal propio, y `P2_RepairRide` vuelve a montar un animal que quedó "libre" con su jinete en `$14`.
  Las paredes de bonus (sprite `$14`) y las vagonetas (`$51`) solo responden al líder.
  **v1.0.1:** en co-op la caja crea siempre 2 animales (aunque el P2 no esté tocando el control). Si el P2 juega, su Kong cae sobre el segundo y lo monta.
  Si el P2 se une, o el líder se sube a un animal (`P2_LeadMountWatch`, `$04D4`) con el Kong del P2 a pie, se le da uno igual (`P2_JoinGiveAnimal` → devolución).
  **Nadie monta un animal ajeno**: filtro en `$BF88AD`. Antes DK podía caer sobre el Rambi de Diddy y quitárselo.
  **Devolución tras un bonus:** al entrar se recuerda el animal del P2 (`$04EC`). En cada cuarto que viene de un bonus, se crea ese animal debajo del Kong del P2 y se lo deja caer encima: lo monta el propio juego.
  Los guiones de animal libre (banco `$B5`): Rambi `$87E1`, Expresso `$8805`, Winky `$87F3`, Enguarde `$87C7`.

## 6a-cuater. Barriles cañón (verificado 2026-11-19)
- Sprite `$38`. Detecta al Kong con `CODE_BFE9BC` → `CODE_BBA574` (máscara `$41`). Propiedades en `$145D,x`: los bits `$3000` marcan barriles **solo DK / solo Diddy**.
- **Original:** el líder entra (`$29` → `$28`). El compañero, siguiéndolo (`$02`), al llegar cerca pasa a `$35` (dentro del mismo barril; `CODE_BCB872` prepara su rastro).
  Al disparo vuelve a `$02` y sigue al líder por el aire.
- **Parche:** los barriles normales solo los activa el líder; el compañero no puede entrar solo.
  Con el líder en `$29`/`$28` el compañero usa su lógica original. Si estaba suelto, `P2_FollowIntoCannon` lo mete al barril (`$35`), o lo pone en `$02` si el líder ya va volando.
  Al aterrizar, el P2 recupera el control. Los barriles con marca de Kong (`$3000`) aceptan a los dos.

## 6b. Objetos y choques (verificado 2026-11-19)
- **Bananas sueltas** (v1.2.2, corregido): las dibuja y recoge `CODE_B8B89F` (llamada en `$B8B524`), una vez por frame,
  con la caja de colisión que dejó en `$C5`-`$CC` el **último Kong procesado** (Diddy va después de DK). Con los dos Kongs
  controlados, solo contaba Diddy: DK nunca juntaba bananas. **Parche:** al entrar Diddy se guarda la caja de DK (`$04B0`)
  y `P2_Bananas` usa en frames alternados la de Diddy y la de DK (`$04BC`). No se puede llamar dos veces: también dibuja.
- **Objetos que son sprites** (racimo `$15`, letra KONG `$16`, globo `$34`, ficha `$45`): solo el líder, porque `CODE_BBA574` acepta solo al líder. ✅
- Con el parche v0.3 (`CODE_BBA574` acepta a ambos Kongs si el P2 está unido) el compañero recoge racimos y letras ✅. Para el golpe, ver 6a.

## 6c. Teletransporte a niveles (pruebas)
En el mapa, al elegir Jungle Hijinxs el juego pone `$3E` = `$40` = `$16` y unos 120 frames después carga el nivel.
Si en ese momento se escribe otra entrada en `$3E` y `$40`, se carga ese nivel (`tools/warp.py`).
IDs de entrada: `disasm/DKC1/Misc_Defines_DKC1.asm` (`!Define_DKC1_EntranceID_*`). Principales:
Ropey Rampage `$0C`, Reptile Rumble `$EA`, Coral Capers `$BF`, Barrel Cannon Canyon `$17`, Winky's Walkway `$D9`,
Mine Cart Carnage `$2E`, Bouncy Bonanza `$07`, Stop & Go `$31`, Millstone `$42`, Vulture Culture `$A5`, Tree Top Town `$A4`,
Forest Frenzy `$D0`, Temple Tempest `$43`, Orang-utan Gang `$0D`, Clam City `$DE`, Snow Barrel Blast `$24`, Slipslide `$6D`,
Ice Age Alley `$A7`, Croctopus `$3E`, Torchlight `$14`, Rope Bridge `$CE`, Oil Drum Alley `$40`, Trick Track Trek `$2F`,
Elevator Antics `$18`, Poison Pond `$22`, Mine Cart Madness `$27`, Blackout Basement `$41`, Tanked Up `$30`,
Manic Mincers `$12`, Misty Mine `$0A`, Loopy Lights `$36`, Platform Perils `$2B`.
Jefes: Very Gnawty `$E0`, Necky's Nuts `$E1`, Bumble B `$E5`, Really Gnawty `$E2`, Dumb Drum `$E3`, Necky's Revenge `$E4`, Gangplank Galleon `$68`.

## 6d. Controles y teclado
Si con dos jugadores en **un mismo teclado** "correr + saltar" anula una dirección, es *ghosting* del teclado, no del juego:
en el emulador las combinaciones funcionan para los dos jugadores (verificado 2026-11-19).

## 6e. Barriles lanzables, TNT, Steel Keg, barril DK (verificado 2026-11-19)
- `$16F5,y` (y = `$84`): índice del objeto que sostiene cada Kong. Estados del objeto (`$1029,x`): 0 libre, 1 tomado, 2 lanzado, 3 montado (keg), 4 TNT en el suelo, 5 colgando, 6 lanzándose, 7 soltado, 8 Manky Kong.
- Estados del Kong: `$17` cargando (parado/caminando), `$18` levantando, `$19`/`$1A` en el aire con el objeto.
- `$1271,x` bit 15 en un barril = barril enemigo: `CODE_BFD30D` (`CODE_BBA574`, máscara `$21`) golpea Kongs (`$1595 = $20`). Barril propio: `CODE_BFD2B0` (`CODE_BBA58D`) golpea enemigos de índice ≥ `$06`.
- Montar keg: `CODE_BFCFC3` (`CODE_BBA574`, máscara `$40`). `CODE_BFD2D6` usa al líder pero es código muerto.
- **Todo funciona con el P2 sin cambios.** El barril DK libera al Kong que falta, lo rompa quien lo rompa.

## 6f. Cuerdas y lianas (verificado 2026-11-19)
- `$1AFD`: cuerda vertical disponible. La escribe el sprite `$30` en `CODE_BFEF0C`, **solo para el líder**.
- `$1AFF`: cuerda que se balancea disponible. La escribe `$31` en `CODE_B68000`, solo para el líder.
- `$1B01`: índice de la cuerda agarrada. `CODE_BF881C` pone `$25` (vertical) y `CODE_BF8861` pone `$26` (balanceo).
- `CODE_BF8584` (estados 0/1) **borra las tres al pisar suelo**. Con el P2 eso le soltaba la cuerda al líder.
  **Parche:** se guardan y restauran alrededor del procesamiento del compañero.
- Seguidor (estado 2): líder en `$26` → `$33`; líder en `$25` → `$34`. **Parche:** con el líder colgado, el compañero suelto pasa a `$02` y sube detrás. Desde v1.2 el P2 también puede colgarse solo (traspaso, ver 6f-bis).
- Estado `$22`: agachado.

## 6g. Plataformas (verificado 2026-11-19)
- `SpritePlatform` `$39`: `CODE_BFEBE2` → `CODE_BBA663` (todos los sprites). Lleva a los dos Kongs sin parche.
- Tambor de aceite `$25` y barril generador `$4C`: `CODE_B696D2` → `CODE_BBA64A` + `CODE_B695E8`, un Kong por llamada.
  **Parche:** `P2_StandBoth` hace una pasada por Kong (`$04F8` = `TouchMode`).
- Ascensor `$3D`: `CODE_BFEAD9` (un Kong) en `$BFEA14`. **Parche:** `P2_LiftBoth`; `CODE_BFEADC` es la entrada después del temporizador `CODE_BFEB4D`.
- RTL útil en banco `$B6`: `$B6875E`.

## 6h. Niveles especiales, salida y eventos (verificado 2026-11-19)
- Squawks (`CODE_B6F581`) sigue al líder; las luces de Blackout Basement (`$64`) son globales; el barril semáforo `$63` usa `CODE_BBA574` (el P2 lo activa).
- Barril checkpoint `$4A` (`CODE_B6F696`, `CODE_BBA574`): guarda la entrada de reinicio en `$2E` (`CODE_BCB952`).
- Caminata de salida de nivel o cuarto: `$1B` → `$1D` → `$1E`. La disparan el sprite `$13` o `ExitDoor` `$6A`/`$6B`, solo con el líder. **Parche:** el compañero pasa a seguirlo.
- `$1E2B`: evento para el líder (1 victoria, 2 fracaso, 3 → `$55`, 4 → `$4E`). Lo consume `CODE_BF876C` en el **primer Kong en el suelo**. `GiantBanana` (`$74`) espera la animación de victoria del líder.
  **Parche:** el compañero no lo consume (se guarda en `$04FA` y se restaura).
- Barriles hacia otro cuarto: propiedad `$145D` bit `$0080`, destino en `$1561`. Cambio de cuarto en `CODE_B88383`; un bonus va por `CODE_B88429`. El compañero entra con el líder (`$35`) sin parche adicional.

## 6i. Jefes (verificado 2026-11-19)
- Sprite `$70` (CurrentWorldBoss), `CODE_B6D922`. Estados 5/6 Gnawty, 7 Dumb Drum, 8 Bumble B, 9/A Necky, B K. Rool (`$152D` sub-estado). Lo acompaña `$6C` (MinigameController).
- `$15C9,x` de un enemigo: índice del Kong que lo pisó (`CODE_BFA79C`).
- Very/Really Gnawty: vida en `$14F9`. `CODE_B6DB9B` confirmaba el pisotón con la altura del **líder**. **Parche:** `P2_BossStomper` usa `$15C9`.
- Dumb Drum: los Klumps solo los vence DK (regla del juego). Bumble B: barriles. K. Rool: pisotón vía `CODE_BFC6C9`.
- Rebote "enemigo duro": estado del Kong `$0F` (`CODE_BFA803`).

## 6f-bis. Traspaso de líder, hoyos y estado 1 en el suelo (v1.2, verificado 2026-11-19)
- **Traspaso** (`P2_Handoff`): si el compañero jugado por el P2 toca algo que el juego solo atiende al líder,
  se invierte `$056F` (`EOR #3`) y se intercambia la prioridad de dibujo (`$0B8D,x`), como hace `CODE_BF8E48`.
  Solo si los dos están "libres" (0/1, `$2B`, `$14`/`$15`, `$30`, `$17`-`$1A`) y `$1929` = 0.
  Ganchos: `CODE_BBA574` (barril cañón `$38` y pared de bonus `$14`), puerta de salida `$6A` (`$B6C46B`),
  puerta bajo el agua `$6B` (`$B6C3EB`), salida `$13` (`$BFD970`), cuerda vertical (`$BFEF0C`) y liana (`$B68002`).
  Los niveles normales terminan con la puerta `$6A` (probado en Stop & Go, Ropey Rampage, Trick Track Trek).
- Cuerdas: la rutina de la cuerda se corre primero con Y = compañero (si está en el aire y el líder no está colgado).
  ⚠ `CODE_B6FC84` puede volver **sin tocar el acarreo**: hay que entrar con carry = 0 (como deja `CODE_809B9C`).
- Al agarrar la cuerda justo en la punta inferior el Kong se resbala (comportamiento normal del juego).
- **Estado 1 apoyado en el suelo:** si se pone a un Kong en 1 estando ya en el suelo, el juego nunca lo aterriza
  (pose de caída, se desliza, no puede saltar). Le pasaba al compañero (era el "patinando"). En un salto normal
  la combinación estado 1 + bit 0 de `$12A5` dura a lo sumo 1 frame; el parche aterriza al compañero si dura 3.
- **Seguir (estado 2):** el seguidor no actualiza `$12A5`. El parche le devuelve el control (estado 1) recién
  cuando el líder lleva 30 frames sin estar en el aire (`$04C8`), o tras 90 frames siguiendo (`$04CC`, si el líder salta sin parar).
- **Hoyo** (`CODE_BFA6C9`): pone `$3B`, `$1929 = 1` y descuenta una vida (`CODE_B6A856`). **Parche** `P2_PitFall`:
  en co-op, si cae el compañero y el líder no, pasa a `$0C` sin perder vida ni tocar `$1929`.
- **Reaparición:** el contador `$04F4` avanza con el líder libre, se pausa si está ocupado y vuelve a 0 solo si el
  líder muere, desaparece o cambia de cuarto (`P2_LeadGone`). Cumplido el tiempo, saca al Kong con el líder en 0/1/`$2B`/`$14`/`$15`/`$30`.
  En las etapas de bonus de animales (entradas `$D2` Rambi, `$D3` Winky, `$6C` Expresso, `$A6` Enguarde) no se trae al otro Kong:
  el original juega con un solo Kong montado y el otro ausente.
- (v1.2, reemplazado) el contador `$04F4` se reiniciaba si el líder no estaba libre. Antes, si el último Kong moría con el
  contador casi lleno, la reaparición se disparaba durante la salida del barril estrella y el juego se congelaba.

## 6f-ter. v1.3: indicador, vagoneta y caída del líder (verificado 2026-11-19)
- **Indicador** (`P2_BananasAndTags`, `$F2FE60`, espacio libre `$F2FE52-$F2FFFF`): se agrega al buffer de OAM (`$0200`, siguiente
  entrada en `$8E`, tabla alta en `$0400`) después de las bananas sueltas. Dígitos del contador: tile `$66+d` arriba y `$76+d` abajo
  (8×8 cada uno); banana del HUD `$1E0 + ($28/2 & $E)` (16×16). Paleta del HUD en `$0531` (se reserva al cargar el nivel, `CODE_B8B580`).
  Pantalla: X = X − `$088B`; Y = `$4A` − Y − `$0895` (pies del Kong).
- **Vagoneta:** `P2_CartShareB` (desde `P2_SelectPad`) suma el B del otro control al del líder en `$2E`/`$2F`
  (`$0500`/`$0504` = mantenidos/recién apretados del control 1, `+2` control 2). El original trae algo parecido como truco del modo team (`CODE_BFB27C`).
- **Caída del líder:** `P2_KeepNearLead` traía al compañero junto al líder si se separaban más de `$D0` en vertical, en las dos
  direcciones: si el líder caía a un hoyo, arrastraba al otro y se perdía una vida. Ahora no lo hace si el líder está más abajo y en el aire;
  `P2_PitFall` hace el traspaso si cae el líder y el otro está libre.

- **Límite de animales** (`P2_TooManyAnimals`, `$D2FE90`): no se crea un animal para el compañero (devolución, unirse,
  líder que se sube) ni el segundo de una caja si ya hay 2 animales libres o montados (los que huyen, estado 2, no cuentan).
  Si el compañero a pie tiene un animal libre a menos de `$80` px, se lo deja caer encima (`P2_DropOnFreeAnimal`).
  Antes, bajarse y volver a subirse sumaba un animal cada vez.
- **Indicador:** se dibuja ANTES que las bananas sueltas (si no, con muchas bananas el buffer de OAM se llenaba).

## 6j. Cámara, pausa, intercambio y ralentización (verificado 2026-11-19)
- **Cámara:** `CODE_809BEC` decide qué Kong sigue (Y = líder, salvo `$1E29`).
  - `CODE_809CD0` calcula la X objetivo (`$1A5E`) con `XPos,y`, `XSpeed,y`, `$0DB9,y` y la anticipación `$1A69`.
  - `CODE_80A05B` → `CODE_809F9A` calcula la vertical (usa `YPos,y`, `$1631,y`, `$0C35,y` y el bit 3 de `$0579`).
  - `CODE_809C8F` limita la cámara al nivel (`$1B23`/`$1B25`).
  - **Parche** (`$809C43`, `P2_Camera`): con el compañero jugado por el P2 se reemplaza por un momento la X y la Y del líder por el **punto medio** de los dos Kongs.
    Junto con el borde de pantalla del compañero, los dos quedan siempre a la vista. RTL útil en el banco `$80`: `$809B9F`.
- **Intercambio con A:** A del Kong → `CODE_BFB830` (según `$180F`) → `CODE_BFB838`: montado = bajarse; a pie = `CODE_BFBF8E` (intercambio).
  **Parche:** con el P2 unido, `P2_SwapFilter` no intercambia a los Kongs: invierte `$04C4` (qué control maneja
  cada Kong, ver `P2_SelectPad`) y sale por el RTS `$BFB840`. Solo con los dos Kongs presentes.
- **Pausa:** la pone `CODE_BFBEEC` (Start del Kong; bit `$40` de `$0579`) y la quita `CODE_809B15` mirando `$0510`.
  Durante la pausa el juego **no lee el control 2**. **Parche** (`$809B1B`, `P2_PausePressed`): suma el Start recién apretado del P2, leído del hardware (`$421A`; anterior en `$04D2`).
- **Ralentización:** `$28`/`$2A` cuentan vueltas del bucle principal (`CODE_8080AB`).
  Medido en juego normal (`tools/test_lag.py`): el parche agrega menos del 1 % de frames atrasados frente al original.

## 6k. Modos de juego (verificado 2026-11-19)
- `$42`: 0 One player, 1 Two player team, 2 Two player contest. Usos de "team" en el juego original:
  - `CODE_808131` (`$808143`): al perder una vida, cambia de Kong (le toca al otro jugador).
  - `$BF8ED4` / `$BF8F77`: tras tomar el liderazgo en tierra o en agua, el Kong espera parpadeando (`$53`/`$56`) a que su jugador apriete algo; `$1929 = 3`.
  - `CODE_BFB27C` / `$80A2A0`: elige el control según `$056F` (`$44`).
  - `CODE_B89FBC`: íconos de jugador en el HUD.
- **Parche:** team = co-op. `$808143` BNE → BRA, y `$BF8ED9`/`$BF8F7C` BEQ → NOP NOP: sin turnos.
  En los otros modos `P2_UpdateJoin` nunca une al P2, así que el juego es idéntico al original.
  En co-op la reaparición del Kong que falta funciona aunque el P2 no se haya unido (empezar con los dos).
- ⚠ asar ensambló mal `BRA $808150` con `org` en el banco `$80` (salto `$50`). Para saltos cortos en parches de bytes usar `db`.

## 7. Cómo investigar más
- `tools/emu.py`: emulador sin ventana (`e.r16(addr)`, `e.w16`, `e.set_buttons(player, ...)`, savestates, capturas).
- `tools/scenario.py ROM STATE out.png "P1/P2*frames; ..."`: imprime posiciones y estados de los Kongs y enemigos.
- `tools/make_states.py`: regenera `work/1p_start.state` y `work/1p_twokongs.state`.
- `tools/warp.py ROM ID NOMBRE`: savestate `work/lvl_NOMBRE.state` en cualquier nivel, con los 2 Kongs.
- `tools/test_fork*.py`: pruebas de barriles (A), cuerdas (B), jefes (C), niveles especiales y salidas (D), plataformas, bonus y Enguarde (E).
- `tools/regresion.sh [--completo]`: batería de regresión. Variables: `COOP=1` (modo co-op), `CORE=bsnes` (núcleo; bsnes no expone la RAM, ver `tools/test_visual_core.py`).
- `tools/survey.py ROM OUT`: recorre 40 niveles (todos los mundos y jefes) y resume. `tools/test_pickups.py ROM STATE`: prueba quién recoge cada objeto.
- Mesen2 (debugger) no arranca en este Fedora: `std::bad_cast`, choque con la libstdc++ de GCC 16.
