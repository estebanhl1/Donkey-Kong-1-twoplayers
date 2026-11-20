; =============================================================================
; DKC1 (USA 1.0) - 2 jugadores simultaneos  (v1.2)
;
; Co-op: elegir "Two player team". Ver docs/MAPA_MEMORIA.md para las direcciones.
;
; Reglas:
;   - El P2 se "une" apretando cualquier boton. Si no toca el control por
;     !IdleFrames frames, se "va": el juego vuelve a ser el original (P1 maneja
;     al lider, el companero lo sigue solo, A intercambia Kongs).
;   - Con el P2 unido el control es por Kong: P1 = DK, P2 = Diddy. Con A
;     (cualquiera de los dos) se intercambian los personajes.
;   - Con el P2 unido, si falta un Kong, reaparece a los !RespawnFrames frames
;     junto al lider (misma animacion que al salir de un barril DK).
;   - El companero controlado no sale de la pantalla y si queda muy lejos en
;     vertical reaparece en el lider. Si cae a un hoyo no se pierde vida.
;   - Lo que el juego reserva al lider (cuerdas, barriles canon y de bonus,
;     paredes de bonus, puertas de salida): si lo toca el Kong del companero,
;     pasa a ser el lider (traspaso) y el juego sigue normal.
;
; Ensamblar:  ./build.sh   (aplica este archivo sobre una copia de la ROM)
; =============================================================================

hirom

; --- RAM (direct page) -------------------------------------------------------
!CurIndex     = $82          ; indice del sprite que se esta procesando
!KongType     = $84          ; 0 = DK, 2 = Diddy

; --- RAM del juego (absolutas, se usan con DB = $7E o con $7E0000+ largo) -----
!HeldP2       = $0502        ; botones mantenidos control 2
!GameMode     = $0042        ; 0 One player, 1 Two player team (co-op), 2 contest
!PartnerFlags = $0579        ; bit 0 = hay companero
!CurrentKong  = $056F        ; 1 = DK lidera, 2 = Diddy lidera
!SprXPos      = $0B19        ; tablas de sprites, indexadas por indice de sprite
!SprYPos      = $0BC1
!SprXSpeed    = $0E89
!SprYSpeed    = $0EF1
!SprState     = $1029
!SprID        = $0D45
!SprAnimSpeed = $1139
!CannonProps  = $145D        ; propiedades del barril canon (bits $3000: solo DK / solo Diddy)
!SprTimer1375 = $1375        ; temporizador/uso general por sprite (0x0E lo usa de espera)
!SprMask11A1  = $11A1        ; mascara de colision por sprite
!KongFreeze   = $1929        ; bits: 1 = camara quieta, 2/8/$10 = congela enemigos
!SprOnGround  = $12A5        ; bit 0 = pisando suelo
!SprOAMZ      = $0B8D        ; prioridad de dibujo del sprite
!KongEvent    = $1E2B        ; evento para el lider: 1 victoria, 2 fracaso, 3/4 otros
!RopeAvailV   = $1AFD        ; cuerda vertical disponible (la pone la cuerda, solo para el lider)
!RopeAvailS   = $1AFF        ; cuerda que se balancea disponible
!RopeHeld     = $1B01        ; cuerda agarrada (global, no por Kong)
!CameraX      = $1A62        ; borde izquierdo de la camara (coords. del nivel)
!CamLookAhead = $1A69        ; anticipacion de camara segun velocidad del Kong

; --- RAM nueva (zona libre $0420-$04FF, despues del buffer OAM) -------------
!P2Joined     = $04F0        ; 0 = P2 ausente, 1 = P2 jugando
!P2IdleTimer  = $04F2        ; frames sin que el P2 toque el control
!RespawnTimer = $04F4        ; frames esperando para traer al Kong que falta
!SaveCam       = $04E0       ; temporales mientras se procesa al companero
!SaveLeadIdx   = $04E2
!SaveLeadState = $04E4
!SaveLead1375  = $04E6
!SaveLead11A1  = $04E8
!Save1929      = $04EA
!PrevLeadRide  = $04D4       ; 1 = el lider iba montado el frame anterior
!PrevHW2       = $04D2       ; control 2 leido del hardware el frame anterior (pausa)
!SaveRopeV     = $04D8       ; copias de las globales de cuerda (companero)
!SaveRopeS     = $04DA
!SaveRopeHeld  = $04DC
!P2SavedAnimal = $04EC       ; ID del animal que montaba el companero al cambiar de cuarto
!P2GivePending = $04EE       ; 1 = devolverle el animal en el cuarto nuevo
!P2GiveTimeout = $04F6       ; frames maximos esperando para devolverlo
!SaveEvent     = $04FA       ; $1E2B guardado mientras se procesa al companero
!SaveLeadX     = $04FC
!SaveLeadY     = $04FE       ; X del lider guardada mientras se calcula la camara compartida
!P2Swap        = $04C4       ; 1 = personajes intercambiados con A (P1 = Diddy, P2 = DK)
!SwapCooldown  = $04C6       ; frames de espera entre dos intercambios
!StuckAir      = $04CA       ; frames con el companero en estado 1 (aire) pero apoyado en el suelo
!FollowT       = $04CC       ; frames con el companero (P2 unido) siguiendo al lider (estado 2)
!LeadGroundT   = $04C8       ; frames seguidos con el lider en el suelo (estado 0)
!DKBox         = $04B0       ; caja de colision de DK ($C5-$CC) guardada antes de procesar a Diddy (4 palabras)
!OtherBox      = $04A0       ; caja de Diddy mientras se revisan las bananas con la de DK (4 palabras)
!DKBoxValid    = $04BA       ; 1 = !DKBox es de este frame
!BananaToggle  = $04BC       ; alterna la caja usada para las bananas sueltas
!EdgeOnly      = $04D0       ; 1 = este frame solo se dibujan los numeros en el borde (Kong fuera de pantalla)
!TagTimer      = $04BE       ; frames que quedan mostrando "1"/"2" sobre los Kongs
!TouchMode     = $04F8       ; CODE_BBA64A: 0 normal (lider y luego companero), 1 solo lider, 2 solo companero

; --- Ajustes -----------------------------------------------------------------
!EdgeMargin    = 12          ; margen (px) con el borde izq/der de la pantalla
!MaxYDist      = $00D0       ; distancia vertical maxima al lider
!SecondAnimalDX = $0028      ; el segundo animal aparece 0x28 px a la derecha
!IdleFrames    = 240         ; ~4 s sin input -> el P2 se va
!RespawnFrames = 180         ; ~3 s para que reaparezca el Kong que falta

; --- Codigo original que reutilizamos ---------------------------------------
!KongMainBody  = $BF84A8     ; cuerpo comun de DKC1_NorSpr01/02 (termina en RTL)
!ReleaseKong   = $BFC9CA     ; (JSR/RTS) saca al Kong que falta en la pos. del sprite actual
!RTL_InBankBF  = $BF849E
!DATA_RambiBox    = $87E1     ; guiones de aparicion (banco $B5) de cada animal libre
!DATA_ExpressoBox = $8805
!DATA_WinkyBox    = $87F3
!DATA_EnguardeBox = $87C7     ; un RTL dentro del banco BF (DKC1_NorSpr00_None_Main)

; =============================================================================
; Parches en el codigo original
; =============================================================================

; Trampolines (reusa los 9 bytes de las entradas originales de DK/Diddy)
org $BF849F                  ; DKC1_NorSpr02_DiddyKong_Main
	JML P2_DiddyEntry
org $BF84A3
	JML P2_DKEntry
	; $BF84A7: 1 byte sin usar (era parte de STZ $84)

org $BF817B                  ; puntero de DK en la tabla de sprites DATA_BF8177
	dw $84A3

org $BFB2C7                  ; dentro de CODE_BFB27C (lectura de botones del Kong)
	JSL P2_SelectPad             ; 4 bytes, reemplaza LDA $44 / ASL / TAY

org $BBA574                  ; CODE_BBA574 "¿toca al jugador?" (objetos y enemigos)
	JML P2_TouchPlayer

; Camara (CODE_809BEC -> $809C43: PHY / JSR CODE_809CD0 / PLY): con el P2
; jugando, la camara horizontal sigue el punto medio entre los dos Kongs.
org $809C43
	JSL P2_Camera                ; (incluye la llamada vertical CODE_80A05B)
	NOP
	NOP
	NOP
	NOP                          ; $809C48: era JSR CODE_80A05B

; Intercambio de Kongs con A (CODE_BFBF8E): desactivado mientras el P2 juega
; (con control fijo no tiene sentido). Bajarse de un animal con A sigue igual.
org $BFBF8E
	JML P2_SwapFilter            ; reemplaza LDX $82 / LDA $1029,x (5 bytes)
	NOP

; Quitar la pausa (CODE_809B15): tambien con el Start del P2.
org $809B1B
	JSL P2_PausePressed          ; reemplaza LDA $0510 / AND #$3000 (6 bytes)
	NOP
	NOP

; -----------------------------------------------------------------------------
; Modos de juego ($42): 0 One player y 2 Two player contest = juego ORIGINAL
; (el P2 nunca se une). 1 Two player team = CO-OP: se anulan los turnos del
; modo team original.
; -----------------------------------------------------------------------------
org $808143                  ; CODE_808131: al perder una vida, team cambiaba de Kong
	db $80,$0B                   ; BRA CODE_808150 (era BNE) -> nunca
org $BF8ED9                  ; tras tomar el liderazgo (tierra): team esperaba al jugador (0x53)
	NOP
	NOP                          ; (era BEQ) -> nunca
org $BF8F7C                  ; idem en el agua (0x56)
	NOP
	NOP

; Jefes Very/Really Gnawty (CODE_B6DB9B): confirmar el pisoton con la altura del
; Kong que piso ($15C9 del jefe), no con la del lider.
org $B6DB9B
	JSL P2_BossStomper           ; reemplaza JSL CODE_809B9C (Y = Kong a revisar)

org $BBA64A                  ; CODE_BBA64A "¿toca al jugador?" con caja fija en Y
	JML P2_TouchPlayer2          ; (neumaticos, plataformas)

; Objetos donde uno se para (tambor $25, barril generador $4C): una pasada por Kong.
org $B696D2
	JSL P2_StandBoth
	RTS

; Ascensor ($3D): en $BFEA14 (BPL +3 / JSR CODE_BFEAD9) -> una pasada por Kong.
org $BFEA14
	JSL P2_LiftBoth              ; usa los flags del CMP #$01C0 anterior
	NOP

; Caja de animal (CODE_BED058): al abrirse crea el animal con JSL CODE_B5804C
; (slot bajo $02-$1C). Con el P2 unido creamos ademas un SEGUNDO animal igual.
; Ojo: CODE_B5802F usa slots $1E+ que CODE_BBA58D no revisa (no se podria montar).
org $BED080                  ; Enguarde
	JSL P2_SpawnAnimal
org $BED08C                  ; Rambi
	JSL P2_SpawnAnimal
org $BED098                  ; Expresso
	JSL P2_SpawnAnimal
org $BED0A4                  ; Winky
	JSL P2_SpawnAnimal

; Montar (CODE_BF888E -> CODE_BF88AD): no permitir subir a un animal que ya
; tiene otro jinete. Reemplaza LDA $88 / CMP #$0006 (5 bytes); el BMI sigue igual.
org $BF88AD
	JSL P2_MountFilter
	NOP

; Cambio de cuarto (entrar a / volver de un bonus): recordar el animal del P2.
org $B88429                  ; entrar al bonus (el juego guarda el animal del lider)
	JSL P2_BonusEnter
org $80838C                  ; carga de cuarto: LDA $1E15 / AND #$0040 (6 bytes)
	JSL P2_RoomLoad
	NOP
	NOP

; =============================================================================
; Codigo nuevo (espacio libre: $CA6C61-$CA7FFF esta en $00 en la ROM original)
; =============================================================================
org $CA7000
P2_DiddyEntry:
	LDA.w #$0002
	STA.b !KongType
	JSR P2_SaveDKBox
	BRA P2_Common

P2_DKEntry:
	STZ.b !KongType

P2_Common:
	PHB
	PEA $7E7E
	PLB
	PLB                          ; DB = $7E (el original se restaura con PLB)

	JSR P2_IsLead
	BNE .partner

	; ---- Lider: logica global, una vez por frame ----
	JSR P2_PauseShare
	LDX.b !CurIndex
	JSR P2_RepairRide
	JSR P2_UpdateJoin
	JSR P2_LeadAirborne
	BCC +
	STZ.w !LeadGroundT           ; lider en el aire / colgado / en un barril
	BRA ++
+
	LDA.w !LeadGroundT
	CMP.w #$00FF
	BCS ++
	INC.w !LeadGroundT
++
	LDA.w !SwapCooldown
	BEQ +
	DEC.w !SwapCooldown
+
	JSR P2_LeadMountWatch
	JSR P2_UpdateRespawn
	PLB
	JML !KongMainBody            ; rutina original sin cambios

.partner
	LDX.b !CurIndex
	; Nota: NO apagar aqui la marca "hay companero" por estar en 0x0C: en las
	; vagonetas el juego esconde al companero (0x0C) pero sigue "presente".
	; La marca se apaga al golpear al companero (ver .no_hurt).

	JSR P2_CheckPartnerAnimal
	JSR P2_RepairRide

	; Companero cayo fuera del nivel (0x3B) y el lider no: se pierde solo el
	; companero (ausente) y reaparecera como tras un golpe.
	LDA.w !SprState,x
	CMP.w #$003B
	BNE .not_pit
	LDA.w !CurrentKong
	ASL
	TAY
	LDA.w !SprState,y
	CMP.w #$003B
	BEQ .not_pit                 ; el lider tambien cae: muerte normal
	LDA.w #$000C
	STA.w !SprState,x
	STZ.w !SprXSpeed,x
	STZ.w !SprYSpeed,x
	LDA.w !PartnerFlags
	AND.w #$FFFE
	STA.w !PartnerFlags
	PLB
	RTL                          ; este frame no procesar al companero
.not_pit
	LDA.w !P2Joined
	BNE .controlled

	; ---- P2 ausente: comportamiento original (seguir al lider) ----
	LDA.w !SprState,x
	BNE +
	LDA.w #$0005                 ; suelo: controlado (0) -> parado detras del lider (5)
	BRA .set_follow
+
	CMP.w #$002B
	BNE .follow_done
	LDA.w #$0036                 ; agua: nadando (2B) -> nadando detras del lider (36)
.set_follow
	STA.w !SprState,x
.follow_done
	PLB
	JML !KongMainBody

.controlled
	; ---- Lider en la vagoneta: el companero va escondido dentro (0x0C) y solo
	;      aparece para saltar con el (0x02). Dejar el comportamiento original.
	LDA.w !CurrentKong
	ASL
	TAY
	LDA.w !SprState,y
	CMP.w #$002E                 ; lider en la vagoneta
	BEQ .original
	CMP.w #$002F                 ; lider saltando con la vagoneta
	BEQ .original
	CMP.w #$0025                 ; lider colgado de una cuerda vertical
	BEQ .rope
	CMP.w #$0026                 ; lider colgado de una cuerda que se balancea
	BEQ .rope
	CMP.w #$001B                 ; lider saliendo del nivel / cuarto (caminata final)
	BEQ .rope
	CMP.w #$001D
	BEQ .rope
	CMP.w #$001E
	BEQ .rope
	CMP.w #$0029                 ; lider entrando a un barril canon
	BEQ .cannon
	CMP.w #$0028                 ; lider en un barril canon (o volando tras el disparo)
	BNE .player
.cannon
	JSR P2_FollowIntoCannon
	BRA .original
.rope
	LDA.w !SprState,x            ; companero suelto (0/1) -> seguir (2): el juego
	CMP.w #$0002                 ; lo hace subir detras ($33/$34) como en el original
	BCS .original
	LDA.w #$0002
	STA.w !SprState,x
.original
	PLB
	JML !KongMainBody

.player
	JSR P2_GiveBackAnimal
	LDX.b !CurIndex
	; ---- P2 unido: el companero se controla como un jugador ----
	LDA.w !SprState,x
	CMP.w #$0002
	BEQ +
	STZ.w !FollowT
+
	LDA.w !SprState,x
	CMP.w #$0002                 ; caminando detras del lider
	BEQ .follower
	CMP.w #$0005                 ; parado detras del lider
	BEQ .follower
	CMP.w #$0036                 ; agua: nadando detras del lider
	BNE .run
	LDA.w #$002B                 ; -> nadando controlado
	STA.w !SprState,x
	BRA .run
.follower
	; Mientras el lider va en el aire (p.ej. saltando desde una cuerda o tras un
	; barril) el companero lo sigue como en el original. Despues se le devuelve
	; el control en estado 1 (aire, con gravedad): si ya pisa suelo aterriza al
	; frame siguiente. (Antes quedaba en 0 en pleno aire: flotaba/se deslizaba.)
	LDA.w !SprState,x
	CMP.w #$0005                 ; parado detras del lider: control directo
	BEQ .take_control
	INC.w !FollowT
	LDA.w !FollowT               ; como mucho ~1.5 s siguiendo (si el lider salta sin parar)
	CMP.w #90
	BCS +
	LDA.w !LeadGroundT           ; caminando/saltando detras (estado 2): esperar a
	CMP.w #30                    ; que el lider lleve ~0.5 s en el suelo (el companero
	BCS +                        ; recorre su mismo camino con retraso)
	JMP .original
+
	STZ.w !FollowT
	LDA.w #$0001
	STA.w !SprState,x
	BRA .run
.take_control
	STZ.w !SprState,x

.run
	; Guardar lo que la rutina del companero podria pisar del lider/global:
	;  - la camara (el companero no debe moverla)
	;  - si golpean al companero, el juego (CODE_BFA17E) cree que es el lider:
	;    fuerza al otro Kong a 0x0E (traspaso) y congela todo con $1929 = 3.
	LDA.w !CamLookAhead
	STA.w !SaveCam
	LDA.w !RopeAvailV
	STA.w !SaveRopeV
	LDA.w !RopeAvailS
	STA.w !SaveRopeS
	LDA.w !RopeHeld
	STA.w !SaveRopeHeld
	LDA.w !CurrentKong
	ASL
	TAY
	STY.w !SaveLeadIdx
	LDA.w !SprState,y
	STA.w !SaveLeadState
	LDA.w !SprTimer1375,y
	STA.w !SaveLead1375
	LDA.w !SprMask11A1,y
	STA.w !SaveLead11A1
	LDA.w !KongFreeze
	STA.w !Save1929
	LDA.w !KongEvent             ; el evento de fin (victoria/fracaso) es del lider:
	STA.w !SaveEvent             ; el companero no debe "consumirlo" (CODE_BF876C)
	STZ.w !KongEvent

	PLB                          ; DB original para la rutina del juego
	JSL !KongMainBody
	REP #$30
	PHB
	PEA $7E7E
	PLB
	PLB                          ; DB = $7E

	LDA.w !SaveCam
	STA.w !CamLookAhead
	LDA.w !SaveEvent
	BEQ +
	STA.w !KongEvent
+
	LDA.w !SaveRopeV             ; el companero no toca las cuerdas del lider
	STA.w !RopeAvailV            ; (CODE_BF8584 las borra al pisar suelo)
	LDA.w !SaveRopeS
	STA.w !RopeAvailS
	LDA.w !SaveRopeHeld
	STA.w !RopeHeld

	; ¿Golpearon al companero? -> deshacer el traspaso sobre el lider
	LDY.w !SaveLeadIdx
	LDA.w !SprState,y
	CMP.w #$000E
	BNE .no_hurt
	CMP.w !SaveLeadState
	BEQ .no_hurt                 ; el lider ya estaba en 0x0E (no fue por nosotros)
	LDA.w !SaveLeadState
	STA.w !SprState,y
	LDA.w !SaveLead1375
	STA.w !SprTimer1375,y
	LDA.w !SaveLead11A1
	STA.w !SprMask11A1,y
	LDA.w !Save1929
	STA.w !KongFreeze
	LDA.w !PartnerFlags          ; el companero se va: ya no hay companero
	AND.w #$FFFE                 ; (si ahora golpean al lider, se pierde vida como en el original)
	STA.w !PartnerFlags
.no_hurt

	; Companero en estado 1 (aire) pero apoyado en el suelo: si se lo puso en 1
	; estando ya en el suelo, el juego nunca lo "aterriza" y queda en la pose de
	; caida, deslizandose y sin poder saltar ("patinando"). En un salto normal
	; esto dura a lo sumo 1 frame; si dura 3, aterrizarlo como hace el juego.
	LDX.b !CurIndex
	LDA.w !SprState,x
	CMP.w #$0001
	BNE .air_ok
	LDA.w !SprOnGround,x
	AND.w #$0001
	BEQ .air_ok
	INC.w !StuckAir
	LDA.w !StuckAir
	CMP.w #3
	BCC .air_done
	STZ.w !SprState,x
.air_ok
	STZ.w !StuckAir
.air_done
	; Borde de pantalla / reaparicion solo mientras se controla normalmente
	; (no durante el golpe y la huida).
	LDX.b !CurIndex
	LDA.w !SprState,x
	CMP.w #$0002
	BCC .keep                    ; 0 o 1 (suelo / aire)
	CMP.w #$002B                 ; nadando
	BEQ .keep
	CMP.w #$0014                 ; montando un animal (suelo)
	BEQ .keep
	CMP.w #$0015                 ; montando un animal (aire)
	BEQ .keep
	CMP.w #$0030                 ; montando a Enguarde
	BEQ .keep
	CMP.w #$0017                 ; cargando un barril ($17 parado/caminando,
	BCC .done                    ;  $18 levantandolo, $19/$1A saltando con el)
	CMP.w #$001B
	BCS .done
.keep
	JSR P2_KeepNearLead
	JSR P2_ClampToScreen
.done
	PLB                          ; DB original
	RTL

; -----------------------------------------------------------------------------
; Z = 1 si el Kong actual ($84) es el lider.  (DB = $7E)
; -----------------------------------------------------------------------------
P2_IsLead:
	LDA.b !KongType              ; 0/2 -> 1/2
	LSR
	INC
	CMP.w !CurrentKong
	RTS

; -----------------------------------------------------------------------------
; P2 se une con cualquier boton; se va tras !IdleFrames sin input. (DB = $7E)
; -----------------------------------------------------------------------------
P2_UpdateJoin:
	LDA.w !GameMode
	CMP.w #$0001                 ; solo en "Two player team" (co-op)
	BEQ +
	STZ.w !P2Joined              ; One player / contest: juego original
	STZ.w !P2IdleTimer
	RTS
+
	LDA.w !HeldP2
	BEQ .idle
	STZ.w !P2IdleTimer
	LDA.w !P2Joined
	BNE +
	JSR P2_JoinGiveAnimal        ; recien se une
	LDA.w #120                   ; mostrar "1"/"2" sobre los Kongs ~2 s
	STA.w !TagTimer
+
	LDA.w #$0001
	STA.w !P2Joined
	RTS
.idle
	LDA.w !P2Joined
	BEQ .done
	; Si falta Diddy (el Kong del P2), el P2 no tiene nada que mover: no
	; contar inactividad, asi sigue "unido" y su Kong reaparece.
	LDA.w !PartnerFlags
	AND.w #$0001
	BNE +
	LDA.w #$0002                 ; Kong del P2: 2 = Diddy, 1 = DK si intercambiaron
	SEC
	SBC.w !P2Swap
	CMP.w !CurrentKong
	BEQ +                        ; el Kong del P2 es el lider: esta presente
	STZ.w !P2IdleTimer           ; falta el Kong del P2
	RTS
+
	INC.w !P2IdleTimer
	LDA.w !P2IdleTimer
	CMP.w #!IdleFrames
	BCC .done
	STZ.w !P2Joined
	STZ.w !P2IdleTimer
.done
	RTS

; -----------------------------------------------------------------------------
; Con el P2 unido, si falta un Kong lo trae de vuelta junto al lider.
; Se llama desde el lider (CurIndex = lider). (DB = $7E)
; -----------------------------------------------------------------------------
P2_UpdateRespawn:
	BRA .start
.reset
	STZ.w !RespawnTimer
	RTS
.start
	LDA.w !P2Joined
	BNE +
	LDA.w !GameMode              ; en co-op siempre (empezar con los dos Kongs)
	CMP.w #$0001
	BNE .reset
+
	LDA.w !PartnerFlags
	AND.w #$0001
	BNE .reset                   ; ya hay companero
	; Etapas de bonus de animales (fichas): con el P2 sin jugar, un solo animal
	; y sin el otro Kong, como en el original (P2_BonusSolo, banco $D2).
	JSL P2_BonusSolo
	BCS .reset
	LDA.w !CurrentKong
	BEQ .reset
	CMP.w #$0003
	BCS .reset
	ASL
	EOR.w #$0006
	TAX                          ; X = indice del Kong que falta
	LDA.w !SprState,x
	CMP.w #$000C                 ; esperar a que termine de huir (0x0C = ausente)
	BNE .done
	; El contador avanza con el lider "libre", se pausa si esta ocupado (cuerda,
	; barril canon, etc.) y vuelve a 0 solo si el lider muere, desaparece o
	; cambia de cuarto. (Si no se reiniciaba al morir, la reaparicion podia
	; dispararse mientras el juego saca al Kong del barril estrella: congelado.)
	LDX.b !CurIndex
	LDA.w !SprState,x
	JSR P2_LeadGone
	BCS .reset
	LDA.w !SprState,x
	JSR P2_IsFreeState           ; libre (incluye cargar un barril)
	BCS .count
	CMP.w #$0022                 ; agachado
	BNE .done                    ; ocupado: pausa
.count
	LDA.w !RespawnTimer
	CMP.w #!RespawnFrames
	BCS +
	INC.w !RespawnTimer
	BRA .done
+
	; tiempo cumplido: sacar al Kong solo con el lider a pie, en el aire,
	; nadando o montando (como siempre); si no, esperar
	LDA.w !SprState,x
	CMP.w #$0002
	BCC .release
	CMP.w #$002B
	BEQ .release
	CMP.w #$0014
	BEQ .release
	CMP.w #$0015
	BEQ .release
	CMP.w #$0030
	BNE .done
.release
	STZ.w !RespawnTimer

	; Llamar a la rutina JSR/RTS del banco BF desde aqui:
	; pila = [ret largo a .back] + [ret corto a un RTL del banco BF]
	; pila aqui: [DB original (de P2_Common)][ret JSR (2)]
	LDA.b !KongType
	PHA                          ; pila: ... [ret JSR][KongType]  -> DB original en $05,s
	SEP #$20
	LDA $05,s
	PHA
	PLB                          ; DB original, como lo espera el juego
	REP #$20
	PHK
	PEA.w .back-1
	PEA.w (!RTL_InBankBF&$FFFF)-1
	JML !ReleaseKong             ; su RTS cae en el RTL del banco BF -> vuelve a .back
.back
	REP #$30
	PEA $7E7E
	PLB
	PLB                          ; DB = $7E
	PLA
	STA.b !KongType
.done
	RTS

; -----------------------------------------------------------------------------
; Si el companero esta demasiado lejos en vertical del lider, lo traemos
; a la posicion del lider. (X = indice del companero, DB = $7E)
; -----------------------------------------------------------------------------
P2_KeepNearLead:
	LDA.w !CurrentKong
	ASL
	TAY                          ; Y = indice del lider (DK = 2, Diddy = 4)
	LDA.w !SprYPos,x
	SEC
	SBC.w !SprYPos,y
	BPL .above                   ; companero mas arriba que el lider
	EOR.w #$FFFF
	INC
	BRA +
.above
	; El lider esta mas abajo: si va en el aire (p.ej. cayendo a un hoyo) no
	; arrastrar al companero con el (si cae al hoyo, el otro pasa a lider).
	PHA
	LDA.w !SprState,y
	CMP.w #$0001
	BEQ .lead_air
	CMP.w #$0015
	BEQ .lead_air
	CMP.w #$0019
	BEQ .lead_air
	CMP.w #$001A
	BEQ .lead_air
	PLA
+
	CMP.w #!MaxYDist
	BCC .ok
	LDA.w !SprXPos,y
	STA.w !SprXPos,x
	LDA.w !SprYPos,y
	STA.w !SprYPos,x
	STZ.w !SprXSpeed,x
	STZ.w !SprYSpeed,x
	LDA.w !SprState,x
	CMP.w #$0014                 ; montando: solo mover (el animal lo sigue)
	BEQ .ok
	CMP.w #$0015
	BEQ .ok
	CMP.w #$0030                 ; montando a Enguarde
	BEQ .ok
	CMP.w #$0017                 ; cargando un barril: solo mover
	BCC +
	CMP.w #$001B
	BCC .ok
+
	LDA.w #$0001                 ; en el aire: cae con gravedad (0 en el aire = flota)
	STA.w !SprState,x
.ok
	RTS
.lead_air
	PLA
	RTS

; -----------------------------------------------------------------------------
; Mantener al companero dentro de la pantalla (borde izq/der).
; (X = indice del companero, DB = $7E)
; -----------------------------------------------------------------------------
P2_ClampToScreen:
	JSL P2_ClampWide             ; (banco $EE)
	RTS

; -----------------------------------------------------------------------------
; Seleccion de control. Reemplaza en CODE_BFB2C7:
;     LDA.b $44 / ASL / TAY      (Y = 0 -> control 1, Y = 2 -> control 2)
;   P2 unido : DK -> control 1, Diddy -> control 2 (fijo por personaje)
;   P2 ausente: lider -> control 1 (companero -> control 2, que esta quieto)
; -----------------------------------------------------------------------------
P2_SelectPad:
	LDA.l $7E0000+!P2Joined
	BEQ .by_role
	LDA.l $7E0000+!P2Swap        ; 0: DK -> control 1, Diddy -> control 2
	ASL                          ; 1: al reves
	EOR.b !KongType
	TAY
	JSR P2_CartShareB
	RTL
.by_role
	LDA.b !KongType
	LSR
	INC
	CMP.l $7E0000+!CurrentKong
	BNE .p2
	LDY.w #$0000
	RTL
.p2
	LDY.w #$0002
	RTL

; -----------------------------------------------------------------------------
; Reemplazo de CODE_BBA574 ("¿el sprite actual toca al jugador?", A = mascara).
; Original: solo acepta al lider. Con el P2 unido aceptamos a cualquiera de los
; dos Kongs (indices 4 y 2). Devuelve carry = toca, $88 = indice del Kong.
; -----------------------------------------------------------------------------
P2_TouchPlayer:
	STA.b $B8
	LDX.b !CurIndex              ; sprite que pregunta
	LDA.l $7E0000+!SprID,x
	CMP.w #$0051                 ; vagoneta: solo el lider puede subir (como el original)
	BEQ .original
	CMP.w #$0014                 ; pared de bonus: solo el lider abre la entrada
	BEQ .original
	CMP.w #$0038                 ; barril canon: solo el lider (el companero entra con el)
	BNE .not_cannon
	LDA.l $7E0000+!CannonProps,x
	AND.w #$3000                 ; ...salvo barriles "solo DK"/"solo Diddy"
	BEQ .original
.not_cannon
	JSR P2_PartnerIsPlayer
	BCC .original
	LDA.w #$0006                 ; CODE_BBA594 revisa desde $88-2 hacia abajo: 4, 2
	STA.b $88
	JSL $BBA594
	RTL
.original
	LDA.l $7E0000+!CurrentKong   ; = CODE_BBA564
	BEQ .def
	CMP.w #$0003
	BPL .def
	ASL
	BRA +
.def
	LDA.w #$0002
+
	PHA
	INC
	INC
	STA.b $88
	JSL $BBA594
	PLA
	BCC .no
	CMP.b $88
	BNE .no
	SEC
	RTL
.no
	; El lider no lo toca. Barril canon / pared de bonus: si los toca el Kong
	; del P2, pasa a ser el lider (asi puede entrar a bonus y barriles).
	LDX.b !CurIndex
	LDA.l $7E0000+!SprID,x
	CMP.w #$0014
	BEQ +
	CMP.w #$0038
	BNE .no2
+
	JSR P2_PartnerIsPlayer
	BCC .no2
	JSL $809B9C                  ; Y = lider
	TYA
	EOR.w #$0006
	PHA                          ; [companero]
	INC
	INC
	STA.b $88
	JSL $BBA594
	PLA
	BCC .no2
	CMP.b $88
	BNE .no2
	JSR P2_Handoff
	BCC .no2
	RTL                          ; carry = 1, $88 = el nuevo lider
.no2
	CLC
	RTL

; -----------------------------------------------------------------------------
; Carry = 1 si el companero esta siendo jugado por el P2 (debe contar para
; choques con enemigos y objetos). No cuenta si el P2 no esta unido, si el
; lider va en la vagoneta, o si el companero esta siguiendo/escondido.
; (Llamada desde el banco $CA; no depende de DB; preserva X)
; -----------------------------------------------------------------------------
P2_PartnerIsPlayer:
	PHX
	LDA.l $7E0000+!P2Joined
	BEQ .no
	LDA.l $7E0000+!CurrentKong
	BEQ .no
	CMP.w #$0003
	BCS .no
	ASL
	TAX                          ; X = indice del lider
	LDA.l $7E0000+!SprState,x
	CMP.w #$002E
	BEQ .no
	CMP.w #$002F
	BEQ .no
	TXA
	EOR.w #$0006
	TAX                          ; X = indice del companero
	LDA.l $7E0000+!SprState,x
	CMP.w #$0002
	BEQ .no
	CMP.w #$0005
	BEQ .no
	CMP.w #$0006
	BEQ .no
	CMP.w #$000C
	BEQ .no
	CMP.w #$0036
	BEQ .no
	PLX
	SEC
	RTS
.no
	PLX
	CLC
	RTS

; -----------------------------------------------------------------------------
; Caja de animal abierta. Y = guion de aparicion del animal.
; 1) original: crea el animal (sprite nuevo en un slot bajo, CODE_B5804C).
; 2) si el P2 esta unido: un segundo animal igual en un sprite nuevo,
;    un poco a la derecha, para que cada Kong tenga el suyo.
; -----------------------------------------------------------------------------
P2_SpawnAnimal:
	PHY
	JSL $B5804C                  ; original
	REP #$30
	PLY
	LDA.l $7E0000+!GameMode      ; en co-op siempre (aunque el P2 no este tocando el control)
	CMP.w #$0001
	BNE .done
	JSL P2_TooManyAnimals        ; ya hay 2 (contando el recien creado): no crear el segundo
	BCS .done
	PHY
	JSL $BF8148                  ; liberar recursos de video si hace falta (como el original)
	REP #$30
	PLY
	JSL $B5804C                  ; otro sprite nuevo (slot bajo $02-$1C, visible para los choques) -> $86
	REP #$30
	BCS .done                    ; no hubo lugar
	LDX.b $86
	LDA.l $7E0000+!SprXPos,x
	CLC
	ADC.w #!SecondAnimalDX
	STA.l $7E0000+!SprXPos,x
	; si el P2 esta jugando, dejar caer a su Kong sobre este animal (lo monta el juego)
	LDA.l $7E0000+!P2Joined
	BEQ .done
	LDA.l $7E0000+!PartnerFlags
	AND.w #$0001
	BEQ .done
	LDA.l $7E0000+!CurrentKong
	BEQ .done
	CMP.w #$0003
	BCS .done
	ASL
	EOR.w #$0006
	TAY                          ; Y = companero
	PHX
	TYX
	LDA.l $7E0000+!SprState,x
	PLX
	CMP.w #$0002
	BCS .done                    ; solo si esta a pie / en el aire, controlado
	LDA.l $7E0000+!SprXPos,x     ; X = animal
	PHA
	LDA.l $7E0000+!SprYPos,x
	CLC
	ADC.w #$0028
	TYX                          ; X = companero
	STA.l $7E0000+!SprYPos,x
	PLA
	STA.l $7E0000+!SprXPos,x
	LDA.w #$0001
	STA.l $7E0000+!SprState,x
	LDA.w #$FC00
	STA.l $7E0000+!SprYSpeed,x
	LDA.w #$0000
	STA.l $7E0000+!SprXSpeed,x
.done
	RTL

; -----------------------------------------------------------------------------
; El animal del companero ($0512,y con y = $84) debe ser un animal que lo tenga
; como jinete ($1375 del animal = indice del companero). Si no (p.ej. despues de
; cambiar de cuarto el indice quedo apuntando a otra cosa), se borra.
; (X = indice del companero, DB = $7E; preserva X)
; -----------------------------------------------------------------------------
P2_CheckPartnerAnimal:
	LDY.b !KongType
	LDA.w $0512,y
	BEQ .ok
	PHX
	TAX                          ; X = indice del animal
	LDA.w !SprID,x
	CMP.w #$0009                 ; Rambi..Enguarde = $09..$0C
	BCC .bad
	CMP.w #$000D
	BCS .bad
	LDA.w !SprTimer1375,x        ; jinete del animal
	CMP.b !CurIndex
	BEQ .good
.bad
	LDA.w #$0000
	STA.w $0512,y
.good
	PLX
.ok
	RTS

; -----------------------------------------------------------------------------
; Si el Kong esta montado (0x14/0x15) y su animal lo tiene como jinete pero el
; animal quedo "libre" (estado 0), volver a ponerlo "montado" (estado 1).
; Pasa cuando el juego re-monta a un Kong que ya iba montado (p.ej. al tomar
; el liderazgo): la senal de subir ($1595 = 8) le llega a un animal ya montado
; y lo baja. (X = indice del Kong, DB = $7E; preserva X)
; -----------------------------------------------------------------------------
P2_RepairRide:
	LDA.w !SprState,x
	CMP.w #$0014
	BEQ +
	CMP.w #$0015
	BNE .ok
+
	LDY.b !KongType
	LDA.w $0512,y
	BEQ .ok
	TAY                          ; Y = indice del animal
	LDA.w !SprID,y
	CMP.w #$0009
	BCC .ok
	CMP.w #$000D
	BCS .ok
	TXA
	CMP.w !SprTimer1375,y        ; ¿este Kong es su jinete?
	BNE .ok
	LDA.w !SprState,y
	BNE .ok                      ; ya esta montado (1) u otro estado
	LDA.w #$0001
	STA.w !SprState,y
	LDA.w #$0000
	STA.w !SprYSpeed,y
	STA.w !SprAnimSpeed,y
.ok
	RTS

; -----------------------------------------------------------------------------
; Filtro al montar. Entrada igual que el original en $BF88AD (A/flags se pisan).
; Salida: N=1 -> no monta (el BMI siguiente salta a "no monta").
;         N=0 y A = $88 -> monta (el codigo original guarda A en $0512,y).
; -----------------------------------------------------------------------------
P2_MountFilter:
	LDA.b $88
	CMP.w #$0006
	BMI .done                    ; no es un sprite valido (N=1)
	PHX
	TAX
	LDA.l $7E0000+!SprID,x
	CMP.w #$0009
	BCC .ok
	CMP.w #$000D
	BCS .ok                      ; no es un animal: comportamiento original
	LDA.l $7E0000+!SprState,x
	CMP.w #$0001                 ; animal montado...
	BNE .ok
	LDA.l $7E0000+!SprTimer1375,x
	CMP.b !CurIndex              ; ...por otro Kong -> no se puede
	BEQ .ok
	PLX
	LDA.w #$FFFF                 ; N=1
	RTL
.ok
	PLX
	LDA.b $88                    ; N=0, A = indice del animal
.done
	RTL

; -----------------------------------------------------------------------------
; Entrar a un bonus: si el companero (con el P2 unido) va montado, recordar el
; animal para devolverselo en el cuarto nuevo. Luego hace lo reemplazado.
; -----------------------------------------------------------------------------
P2_BonusEnter:
	PHX
	LDA.w #$0000
	STA.l $7E0000+!P2SavedAnimal
	STA.l $7E0000+!P2GivePending
	LDA.l $7E0000+!P2Joined
	BEQ .done
	LDA.l $7E0000+!CurrentKong
	BEQ .done
	CMP.w #$0003
	BCS .done
	ASL
	EOR.w #$0006
	TAX                          ; X = indice del companero
	LDA.l $7E0000+!SprState,x
	CMP.w #$0014
	BEQ .riding
	CMP.w #$0030                 ; Enguarde
	BEQ .riding
	CMP.w #$0015
	BNE .done
.riding
	DEX
	DEX                          ; X = tipo de Kong (0/2)
	LDA.l $7E0512,x
	BEQ .done
	TAX                          ; X = indice del animal
	LDA.l $7E0000+!SprID,x
	CMP.w #$0009
	BCC .done
	CMP.w #$000D
	BCS .done
	STA.l $7E0000+!P2SavedAnimal
	LDA.w #$0001
	STA.l $7E0000+!P2GivePending
	LDA.w #600
	STA.l $7E0000+!P2GiveTimeout
.done
	PLX
	JSL $809B9C                  ; instruccion reemplazada (Y = indice del lider)
	RTL

; Carga de un cuarto (reemplaza LDA $1E15 / AND #$0040 en CODE_80838C; el BNE
; siguiente usa el mismo resultado). Bit $40 de $1E15 = viene de un bonus
; (el juego conserva/devuelve el animal del lider). Hacemos lo mismo con el P2.
P2_RoomLoad:
	LDA.l $7E1E15
	AND.w #$0040
	BEQ .fresh
	LDA.l $7E0000+!P2SavedAnimal
	BEQ .keep
	LDA.w #$0001
	STA.l $7E0000+!P2GivePending
	LDA.w #600
	STA.l $7E0000+!P2GiveTimeout
.keep
	LDA.w #$0040                 ; Z = 0 (como el original)
	RTL
.fresh
	LDA.w #$0000                 ; nivel nuevo: olvidar el animal del P2
	STA.l $7E0000+!P2SavedAnimal
	STA.l $7E0000+!P2GivePending ; Z = 1 (como el original)
	RTL

; -----------------------------------------------------------------------------
; En el cuarto nuevo: cuando el companero (P2 unido) ya esta a pie y controlable,
; crear su animal debajo de el y dejarlo caer encima: el juego lo monta solo.
; (llamada desde el camino del companero; DB = $7E al entrar y al salir)
; -----------------------------------------------------------------------------
P2_GiveBackAnimal:
	LDA.w !P2GivePending
	BNE +
	RTS
+
	DEC.w !P2GiveTimeout
	BEQ .cancel
	LDA.w !PartnerFlags
	AND.w #$0001
	BEQ .done                    ; no hay companero (todavia)
	LDX.b !CurIndex
	LDA.w !SprState,x
	BEQ .go                      ; companero a pie, controlado
	CMP.w #$0001
	BEQ .go
	CMP.w #$0002                 ; o siguiendo al lider (se convierte despues)
	BEQ .go
	CMP.w #$0005
	BNE .done
.go
	JSL P2_TooManyAnimals        ; ya hay 2 animales: no crear otro; si hay uno libre
	BCC +                        ; cerca, dejarlo caer encima (lo monta el juego)
	JSL P2_DropOnFreeAnimal
	JMP .cancel
+
	LDA.w !P2SavedAnimal
	LDY.w #!DATA_RambiBox
	CMP.w #$0009
	BEQ .spawn
	LDY.w #!DATA_ExpressoBox
	CMP.w #$000A
	BEQ .spawn
	LDY.w #!DATA_WinkyBox
	CMP.w #$000B
	BEQ .spawn
	LDY.w #!DATA_EnguardeBox
.spawn
	LDA.b !KongType
	PHA
	LDA.b !CurIndex
	PHA
	JSL $B5804C                  ; animal nuevo en la posicion del companero
	REP #$30
	PEA $7E7E
	PLB
	PLB                          ; DB = $7E de nuevo
	PLA
	STA.b !CurIndex
	PLA
	STA.b !KongType
	BCS .cancel                  ; no hubo lugar
	; dejar caer al companero sobre su animal
	LDX.b !CurIndex
	LDA.w !SprYPos,x
	CLC
	ADC.w #$0028
	STA.w !SprYPos,x
	LDA.w #$0001
	STA.w !SprState,x
	LDA.w #$FC00
	STA.w !SprYSpeed,x
	STZ.w !SprXSpeed,x
.cancel
	STZ.w !P2GivePending         ; (P2SavedAnimal se conserva: al volver del bonus
.done                            ;  se devuelve el animal que tenia al entrar)
	RTS

; -----------------------------------------------------------------------------
; Reemplazo de CODE_BBA64A (A = mascara, Y = caja de colision del Kong).
; Original: solo el lider. Con el companero jugado por el P2: primero el lider
; (como el original) y, si el lider no toca, el companero.
; Devuelve carry = toca, $88 = indice del Kong. Preserva Y.
; -----------------------------------------------------------------------------
P2_TouchPlayer2:
	STA.b $B8
	LDA.l $7E0000+!CurrentKong   ; indice del lider (= CODE_BBA564)
	BEQ .def
	CMP.w #$0003
	BPL .def
	ASL
	BRA +
.def
	LDA.w #$0002
+
	PHA                          ; [indice del lider]
	LDA.l $7E0000+!TouchMode
	CMP.w #$0002
	BEQ .partner                 ; modo 2: solo el companero
	JSR .check                   ; ¿toca el lider?
	BCS .yes
	LDA.l $7E0000+!TouchMode
	CMP.w #$0001
	BEQ .no                      ; modo 1: solo el lider
.partner
	JSR P2_PartnerIsPlayer
	BCC .no
	LDA $01,s
	EOR.w #$0006                 ; indice del companero
	STA $01,s
	JSR .check
	BCS .yes
.no
	PLA
	CLC
	RTL
.yes
	PLA
	SEC
	RTL

; carry = el Kong con indice ($03,s) toca (Y = caja; preserva Y)
.check
	LDA $03,s
	INC
	INC
	STA.b $88
	PHY
	JSL $BBA66A
	PLY
	BCC .c_no
	LDA $03,s
	CMP.b $88
	BNE .c_no
	SEC
	RTS
.c_no
	CLC
	RTS

; -----------------------------------------------------------------------------
; El lider entro a un barril canon (Y = indice del lider, X = companero, DB=$7E).
; Si el companero esta suelto (controlado por el P2):
;  - lider quieto dentro del barril (0x29, o 0x28 sin velocidad): meter al
;    companero en el mismo barril (lo mismo que hace el juego: CODE_BF8A22).
;  - lider volando tras el disparo: el companero pasa a "seguir" (estado 2) y
;    lo sigue por el aire como en el original.
; -----------------------------------------------------------------------------
P2_FollowIntoCannon:
	LDA.w !SprState,x
	CMP.w #$0002
	BCS .done                    ; solo si esta controlado (0/1)
	LDA.w !SprState,y
	CMP.w #$0029
	BEQ .into
	LDA.w !SprXSpeed,y
	ORA.w !SprYSpeed,y
	BEQ .into
	LDA.w #$0002                 ; volando: seguirlo
	STA.w !SprState,x
	BRA .done
.into
	LDA.w !SprXPos,y
	STA.w !SprXPos,x
	LDA.w !SprYPos,y
	STA.w !SprYPos,x
	PHX
	PHY
	JSL $BCB872                  ; prepara el "rastro" del companero (como el juego)
	REP #$30
	PEA $7E7E
	PLB
	PLB
	PLY
	PLX
	LDA.w #$0035                 ; dentro del barril con el lider
	STA.w !SprState,x
.done
	RTS

; -----------------------------------------------------------------------------
; Reemplazo de CODE_B696D2 (tambor de aceite $25, barril generador $4C): el
; original atiende a un solo Kong (el lider). Hacemos una pasada por Kong.
; -----------------------------------------------------------------------------
P2_StandBoth:
	LDA.w #$0001
	STA.l $7E0000+!TouchMode
	JSR .one
	JSR P2_PartnerIsPlayer
	BCC .end
	LDA.w #$0002
	STA.l $7E0000+!TouchMode
	JSR .one
.end
	LDA.w #$0000
	STA.l $7E0000+!TouchMode
	RTL
.one
	JSL $BBA4D5
	LDA.w #$0040
	LDY.w #$A534                 ; DATA_BBA534
	JSL $BBA64A
	BCC .r
	LDX.b $88
	PHK
	PEA.w .back-1
	PEA.w $875E-1                ; RTL en $B6875E
	JML $B695E8                  ; JSR/RTS del banco $B6
.back
	REP #$30
.r
	RTS

; -----------------------------------------------------------------------------
; Ascensor ($3D): reemplazo de BPL +3 / JSR CODE_BFEAD9 en $BFEA14.
; Una pasada para el lider y otra para el companero.
; -----------------------------------------------------------------------------
P2_LiftBoth:
	BPL .done
	LDA.w #$0001
	STA.l $7E0000+!TouchMode
	PHK
	PEA.w .b1-1
	PEA.w (!RTL_InBankBF&$FFFF)-1
	JML $BFEAD9
.b1
	REP #$30
	JSR P2_PartnerIsPlayer
	BCC .end
	LDA.w #$0002
	STA.l $7E0000+!TouchMode
	PHK
	PEA.w .b2-1
	PEA.w (!RTL_InBankBF&$FFFF)-1
	JML $BFEADC                  ; sin repetir el temporizador CODE_BFEB4D
.b2
	REP #$30
.end
	LDA.w #$0000
	STA.l $7E0000+!TouchMode
.done
	RTL

; -----------------------------------------------------------------------------
; Jefe Gnawty pisado ($1595 = 1): Y = indice del Kong que lo piso ($15C9,x,
; lo guarda CODE_BFA79C). Si no hay registro, el lider (como el original).
; -----------------------------------------------------------------------------
P2_BossStomper:
	LDY.w $15C9,x
	BEQ .lead
	RTL
.lead
	JSL $809B9C
	RTL

; -----------------------------------------------------------------------------
; Camara compartida. Y = Kong que sigue la camara (normalmente el lider).
; Si el companero lo juega el P2 y esta suelto, durante el calculo horizontal
; (CODE_809CD0) la X del lider se reemplaza por el punto medio de ambos.
; El borde de pantalla del companero hace el resto: si se separan, la camara
; queda entre los dos y el que se queda atras es empujado por el borde.
; -----------------------------------------------------------------------------
P2_Camera:
	PHY
	PHB
	JSR P2_CameraShared          ; carry = compartir; X = companero
	BCC .call
	PEA $7E7E
	PLB
	PLB                          ; DB = $7E
	JSL P2_MidX                  ; X del lider = punto medio (con limite) (banco $EE)
	PLB                          ; DB original para la rutina del juego
	PHB
.call
	PLB
	PHB
	PHK
	PEA.w .back-1
	PEA.w $9B9F-1                ; RTL en $809B9F
	JML $809CD0
.back
	REP #$30
	PLB
	LDA $01,s                    ; Y original
	TAY
	JSR P2_CameraShared
	BCC .vert
	LDA.l $7E0000+!SaveLeadX     ; restaurar la X del lider
	PHX
	TYX
	STA.l $7E0000+!SprXPos,x
	PLX
	JSL P2_MidY                  ; vertical: Y del lider = punto medio (con limite)
.vert
	PHB
	PHK
	PEA.w .back2-1
	PEA.w $9B9F-1                ; RTL en $809B9F
	JML $80A05B                  ; camara vertical (Y = Kong seguido)
.back2
	REP #$30
	PLB
	LDA $01,s
	TAY
	JSR P2_CameraShared
	BCC .done
	LDA.l $7E0000+!SaveLeadY     ; restaurar la Y del lider
	TYX
	STA.l $7E0000+!SprYPos,x
.done
	PLY
	RTL

; Carry = 1 si la camara debe ser compartida (Y = Kong seguido por la camara).
; Devuelve X = indice del companero. Preserva Y.
P2_CameraShared:
	LDA.l $7E0000+!P2Joined
	BEQ .no
	LDA.l $7E0000+!PartnerFlags
	AND.w #$0001
	BEQ .no
	LDA.l $7E0000+!CurrentKong
	BEQ .no
	CMP.w #$0003
	BCS .no
	ASL
	STA.b $76
	CPY.b $76
	BNE .no                      ; la camara no sigue al lider (caso especial del juego)
	EOR.w #$0006
	TAX                          ; X = companero
	LDA.l $7E0000+!SprState,x
	CMP.w #$0002
	BCC .yes                     ; suelo / aire
	CMP.w #$002B
	BEQ .yes                     ; nadando
	CMP.w #$0014
	BEQ .yes
	CMP.w #$0015
	BEQ .yes                     ; montando
	CMP.w #$0030
	BEQ .yes                     ; Enguarde
	CMP.w #$0017
	BCC .no
	CMP.w #$001B
	BCC .yes                     ; cargando un barril
.no
	CLC
	RTS
.yes
	SEC
	RTS

; -----------------------------------------------------------------------------
; Intercambio con A: con el P2 unido no se hace (vuelve por un RTS del banco BF).
; -----------------------------------------------------------------------------
P2_SwapFilter:
	LDA.l $7E0000+!P2Joined
	BEQ .original
	; Con el P2 jugando: A intercambia que Kong maneja cada jugador (sin mover
	; a nadie). Solo con los dos Kongs presentes; espera entre intercambios
	; para que el mismo A no lo deshaga al leerlo el otro Kong.
	LDA.l $7E0000+!PartnerFlags
	AND.w #$0001
	BEQ .no
	LDA.l $7E0000+!SwapCooldown
	BNE .no
	LDA.w #20
	STA.l $7E0000+!SwapCooldown
	LDA.l $7E0000+!P2Swap
	EOR.w #$0001
	STA.l $7E0000+!P2Swap
	LDA.w #120                   ; mostrar "1"/"2" sobre los Kongs ~2 s
	STA.l $7E0000+!TagTimer
.no
	JML $BFB840                  ; RTS en el banco BF -> no intercambiar a los Kongs
.original
	LDX.b !CurIndex              ; instrucciones reemplazadas
	LDA.l $7E0000+!SprState,x
	JML $BFBF93                  ; CMP #$0053 ...

; -----------------------------------------------------------------------------
; Pausa. La pausa se quita en CODE_809B15 mirando $0510 (botones "actuales",
; que en modo 1 jugador son solo del control 1) y durante la pausa el juego no
; actualiza el control 2. Leemos el control 2 del hardware ($421A).
; P2_PauseShare (camino del lider, cada frame normal): recordar el control 2.
; P2_PausePressed (reemplaza LDA $0510 / AND #$3000 en $809B1B): sumar el
; Start recien apretado del P2.
; -----------------------------------------------------------------------------
P2_PauseShare:
	LDA.l $00421A
	STA.w !PrevHW2
	RTS

P2_PausePressed:
	LDA.l $00421A
	TAX
	EOR.l $7E0000+!PrevHW2
	AND.l $00421A
	AND.w #$1000                 ; Start recien apretado por el P2
	STA.b $76
	TXA
	STA.l $7E0000+!PrevHW2
	LDA.l $7E0000+!P2Joined
	BNE +
	STZ.b $76
+
	LDA.w $0510                  ; instruccion reemplazada (+ Start del P2)
	ORA.b $76
	AND.w #$3000
	RTL

; -----------------------------------------------------------------------------
; El P2 se une con el lider montado y el companero a pie: darle un animal igual
; (usa la devolucion de animal: se crea debajo del companero y lo monta).
; (camino del lider, DB = $7E)
; -----------------------------------------------------------------------------
P2_JoinGiveAnimal:
	LDA.w !PartnerFlags
	AND.w #$0001
	BEQ .done
	LDX.b !CurIndex
	LDA.w !SprState,x
	CMP.w #$0014
	BEQ .riding
	CMP.w #$0015
	BEQ .riding
	CMP.w #$0030
	BNE .done
.riding
	LDY.b !KongType
	LDA.w $0512,y
	BEQ .done
	TAX                          ; animal del lider
	LDA.w !SprID,x
	CMP.w #$0009
	BCC .done
	CMP.w #$000D
	BCS .done
	STA.w !P2SavedAnimal
	LDA.w #$0001
	STA.w !P2GivePending
	LDA.w #600
	STA.w !P2GiveTimeout
.done
	RTS

; -----------------------------------------------------------------------------
; Cuando el lider se SUBE a un animal (transicion a montado) con el P2 jugando
; y el companero a pie, darle al companero un animal igual. (lider, DB = $7E)
; -----------------------------------------------------------------------------
P2_LeadMountWatch:
	LDX.b !CurIndex
	LDA.w !SprState,x
	LDY.w #$0000
	CMP.w #$0014
	BEQ +
	CMP.w #$0015
	BEQ +
	CMP.w #$0030
	BNE ++
+
	LDY.w #$0001
++
	TYA
	CMP.w !PrevLeadRide
	STA.w !PrevLeadRide
	BEQ .done                    ; sin cambio
	CMP.w #$0001
	BNE .done                    ; se bajo
	LDA.w !P2Joined
	BEQ .done
	JSR P2_JoinGiveAnimal
	LDA.w #60                    ; solo si el companero esta a pie ahora
	STA.w !P2GiveTimeout
.done
	RTS

print "Codigo nuevo termina en: ", pc
warnpc $CA79E0                ; ahi empieza la pantalla inicial (splash.asm)

incsrc splash.asm             ; pantalla inicial (dedicatoria + link del repo)

; =============================================================================
; Indicador sobre cada Kong (~2 s al intercambiar con A, al unirse el P2 o al
; cambiar el lider): "1" / "2" = que jugador lo maneja, y una banana girando
; sobre el lider ("el que manda"). Usa graficos del contador de bananas que ya
; estan en VRAM: digitos (tiles $66+d arriba, $76+d abajo) y la banana del HUD
; ($1E0.., 16x16), con la paleta del HUD ($0531, reservada al cargar el nivel).
; Se agrega al buffer de OAM justo despues del dibujo de las bananas sueltas.
; (espacio libre $F2FE52-$F2FFFF)
; =============================================================================
!PrevLeadTag   = $04C2       ; lider del frame anterior (para mostrar el indicador al cambiar)

org $F2FE60
P2_BananasAndTags:
	; el indicador va ANTES que las bananas sueltas: si hay muchas, el buffer de
	; OAM se llena y el indicador no alcanzaba a dibujarse
	REP #$30
	JSL P2_BonusFrame            ; etapas de animales con el P2 (banco $D2)
	REP #$30
	JSR .tags
	JSL P2_Bananas
	RTL

.tags
	LDA.l $7E0000+!TagTimer      ; sin indicador activo: igual se dibuja el
	BEQ .edge                    ; numero en el borde si un Kong esta fuera
	DEC
	STA.l $7E0000+!TagTimer
	LDA.w #$0000
	BRA .mode
.edge
	LDA.w #$0001
.mode
	STA.l $7E0000+!EdgeOnly
	LDA.l $7E0000+!P2Joined
	BEQ .done
	LDA.l $7E0000+!PartnerFlags  ; solo con los dos Kongs (salvo en las
	AND.w #$0001                 ; etapas de animales: un solo animal)
	BNE +
	JSL P2_BonusSolo
	BCC .done
+
	LDX.w #$0002                 ; DK
	JSR .one
	LDX.w #$0004                 ; Diddy
	JSR .one
.done
	RTS

.one                             ; X = indice del Kong
	LDA.l $7E0000+!SprState,x
	CMP.w #$000C                 ; ausente / escondido
	BNE ++
	JMP .r
++
	; digito = jugador que lo maneja: (KongType EOR intercambio*2) / 2 + 1
	LDA.l $7E0000+!P2Swap
	ASL
	STA.b $76
	TXA
	DEC
	DEC
	EOR.b $76
	LSR
	INC
	STA.b $78                    ; 1 o 2
	; X en pantalla (centro del Kong)
	LDA.l $7E0000+!SprXPos,x
	SEC
	SBC.l $7E088B                ; Layer1XPos
	SEC
	SBC.w #$0008
	STZ.b $7E                    ; 0 = en pantalla
	CMP.w #$00F0
	BCC .onscreen
	; fuera de pantalla: el numero va en el borde, parpadeando
	TAY
	LDA.b $28
	AND.w #$0010
	BEQ ++
	JMP .r
++
	INC.b $7E                    ; 1 = fuera de pantalla
	LDA.w #$0020                 ; a la altura del cuerpo
	STA.b $70
	TYA
	BMI +
	LDA.w #$00EA                 ; borde derecho (X - 8 + 4 = $EE)
	BRA ++
+
	LDA.w #$0000                 ; borde izquierdo (X = 4; con $FFFE el $FF se
	                             ; mezclaba con la Y y el numero quedaba arriba)
++
	BRA .xok
.onscreen
	TAY
	LDA.l $7E0000+!EdgeOnly
	BEQ +
	JMP .r
+
	LDA.w #$0040                 ; sobre la cabeza
	STA.b $70
	TYA
.xok
	STA.b $7A                    ; X - 8
	; Y en pantalla: $4A - Y - Layer1YPos (pies); el digito 0x40 mas arriba
	LDA.b $4A
	SEC
	SBC.l $7E0000+!SprYPos,x
	SEC
	SBC.l $7E0895
	SEC
	SBC.b $70
	STA.b $7C
	JSL P2_BonusSolo             ; etapas de animales: el Kong escondido queda mas
	LDA.b $7C                    ; abajo que el animal -> 0x30 mas arriba
	BCC +
	SBC.w #$0030
+
	BPL +
	LDA.w #$0012                 ; muy arriba: pegado al borde de arriba
+
	CMP.w #$00C8
	BCC +
	LDA.w #$00C7                 ; muy abajo: pegado al borde de abajo
+
	CMP.w #$0012
	BCS +
	LDA.w #$0012
+
	STA.b $7C                    ; Y del digito
	LDY.b $8E                    ; siguiente entrada libre del buffer de OAM
	CPY.w #$03F0
	BCS .r
	; digito (2 entradas de 8x8)
	LDA.b $7C
	XBA
	ORA.b $7A
	CLC
	ADC.w #$0004                 ; digito centrado (X - 4)
	STA.w $0000,y
	CLC
	ADC.w #$0800
	STA.w $0004,y
	LDA.b $78
	CLC
	ADC.w #$0066
	ORA.l $7E0531
	STA.w $0002,y
	ORA.w #$0010
	STA.w $0006,y
	LDA.w #$0000                 ; chicos
	JSR .hi
	INY
	INY
	INY
	INY
	LDA.w #$0000
	JSR .hi
	INY
	INY
	INY
	INY
	; lider: banana girando arriba del digito (16x16), si esta en pantalla
	LDA.b $7E
	BNE .end
	TXA
	LSR
	CMP.l $7E0000+!CurrentKong
	BNE .end
	LDA.b $7C
	SEC
	SBC.w #$0011
	XBA
	ORA.b $7A
	STA.w $0000,y
	LDA.b $28
	LSR
	AND.w #$000E
	CLC
	ADC.w #$01E0
	ORA.l $7E0531
	STA.w $0002,y
	LDA.w #$0002                 ; grande
	JSR .hi
	INY
	INY
	INY
	INY
.end
	STY.b $8E
.r
	RTS

; tabla alta del OAM para la entrada en Y: A = bits (0 chico / 2 grande; X < 256)
.hi
	PHY
	PHX
	STA.b $76
	TYA
	SEC
	SBC.w #$0200
	LSR
	LSR                          ; n = numero de entrada
	PHA
	AND.w #$0003
	ASL
	TAX                          ; desplazamiento (0,2,4,6)
	LDA.w #$FFFC
-	CPX.w #$0000
	BEQ +
	SEC
	ROL
	ASL.b $76
	DEX
	BRA -
+
	STA.b $72                    ; mascara
	PLA
	LSR
	LSR
	CLC
	ADC.w #$0400
	TAY
	SEP #$20
	LDA.w $0000,y
	AND.b $72
	ORA.b $76
	STA.w $0000,y
	REP #$20
	PLX
	PLY
	RTS

print "Indicador termina en: ", pc
warnpc $F30000

; =============================================================================
; v1.2: traspaso de liderazgo, salidas y cuerdas para el Kong del P2
; (espacio libre $CA6C70-$CA6FFF)
; =============================================================================
org $BFD970                  ; salida de nivel (sprite $13): JSL CODE_809B9C
	JSL P2_Exit13
org $B6C46B                  ; puerta de salida $6A (estado 0): JSL CODE_809B9C
	JSL P2_ExitDoor
org $B6C3EB                  ; puerta de salida bajo el agua $6B (estado 0)
	JSL P2_ExitDoorWater
org $BFEF0C                  ; cuerda vertical $30: JSL CODE_809B9C
	JSL P2_RopeV
org $B68002                  ; cuerda que se balancea $31: JSL CODE_809B9C
	JSL P2_RopeS

org $BFA6C9                  ; caida a un hoyo (CODE_BFA6C9): LDA $1E15 / AND #$0020
	JSL P2_PitFall
	NOP
	NOP

org $B8B524                  ; dibujo y recoleccion de bananas sueltas: JSL CODE_B8B89F
	JSL P2_BananasAndTags        ; bananas + indicador 1/2 (ver "Indicador")

org $CA6C70
; -----------------------------------------------------------------------------
; Bananas sueltas. CODE_B8B89F las dibuja y revisa si las toca la caja de
; colision que dejo el ULTIMO Kong procesado ($C5-$CC): con los dos Kongs
; controlados siempre era la de Diddy, asi que DK nunca juntaba bananas.
; En co-op, un frame se revisa con la caja de Diddy y el siguiente con la de DK.
; -----------------------------------------------------------------------------
P2_SaveDKBox:                ; (entrada de Diddy: DK ya se proceso este frame)
	LDA.l $7E0000+!P2Joined
	BEQ .no
	LDA.l $7E0000+!PartnerFlags
	AND.w #$0001
	BEQ .no
	LDA.b $C5
	STA.l $7E0000+!DKBox
	LDA.b $C7
	STA.l $7E0000+!DKBox+2
	LDA.b $C9
	STA.l $7E0000+!DKBox+4
	LDA.b $CB
	STA.l $7E0000+!DKBox+6
	LDA.w #$0001
	BRA +
.no
	LDA.w #$0000
+
	STA.l $7E0000+!DKBoxValid
	RTS

P2_Bananas:
	LDA.l $7E0000+!DKBoxValid
	BEQ .plain
	LDA.w #$0000
	STA.l $7E0000+!DKBoxValid
	LDA.l $7E0000+!BananaToggle
	EOR.w #$0001
	STA.l $7E0000+!BananaToggle
	BEQ .plain
	; frame de DK: guardar la caja de Diddy y poner la de DK
	LDA.b $C5
	STA.l $7E0000+!OtherBox
	LDA.b $C7
	STA.l $7E0000+!OtherBox+2
	LDA.b $C9
	STA.l $7E0000+!OtherBox+4
	LDA.b $CB
	STA.l $7E0000+!OtherBox+6
	LDA.l $7E0000+!DKBox
	STA.b $C5
	LDA.l $7E0000+!DKBox+2
	STA.b $C7
	LDA.l $7E0000+!DKBox+4
	STA.b $C9
	LDA.l $7E0000+!DKBox+6
	STA.b $CB
	JSL $B8B89F
	REP #$30
	LDA.l $7E0000+!OtherBox
	STA.b $C5
	LDA.l $7E0000+!OtherBox+2
	STA.b $C7
	LDA.l $7E0000+!OtherBox+4
	STA.b $C9
	LDA.l $7E0000+!OtherBox+6
	STA.b $CB
	RTL
.plain
	JSL $B8B89F
	RTL

; -----------------------------------------------------------------------------
; Vagoneta: el lider va en el carro ($2E / $2F) y el otro Kong escondido. Con el
; P2 jugando, el B de cualquiera de los dos controles hace saltar el carro (se
; suma el B del otro control al del lider, como el truco del modo team).
; Y = control del Kong actual (0/2). Preserva X e Y. (DB del juego)
; -----------------------------------------------------------------------------
P2_CartShareB:
	PHX
	LDX.b !CurIndex
	LDA.w !SprState,x
	CMP.w #$002E
	BEQ +
	CMP.w #$002F
	BNE .done
+
	TYA
	EOR.w #$0002
	TAX                          ; X = el otro control
	LDA.w $0504,x                ; recien apretados del otro control
	AND.w #$8000                 ; B
	ORA.w $0504,y
	STA.w $0504,y
	LDA.w $0500,x                ; mantenidos
	AND.w #$8000
	ORA.w $0500,y
	STA.w $0500,y
.done
	PLX
	RTS

; -----------------------------------------------------------------------------
; Caida a un hoyo. El juego pone al Kong en $3B, congela la camara ($1929 = 1)
; y descuenta una vida (CODE_B6A856). En co-op, si el que cae es el companero
; y el lider no esta cayendo, solo desaparece (como tras un golpe) y reaparece
; a los ~3 s: sin perder vida ni congelar nada. Si cae el lider y el otro Kong
; (jugado por el P2) esta libre, el otro pasa a ser el lider y pasa lo mismo.
; Si no, lo original.
; -----------------------------------------------------------------------------
P2_PitFall:
	LDA.l $7E0000+!GameMode
	CMP.w #$0001
	BNE .original
	LDA.l $7E0000+!PartnerFlags
	AND.w #$0001
	BEQ .original                ; no hay companero: el que cae es el ultimo
	JSL $809B9C                  ; Y = lider
	CPY.b !CurIndex
	BNE .partner_falls
	; Cae el lider: si el otro Kong lo juega el P2 y esta libre, pasa a ser el
	; lider (traspaso) y el que cayo desaparece como un companero.
	JSR P2_Handoff
	BCC .original
	BRA .gone
.partner_falls
	LDA.w !SprState,y
	CMP.w #$003B
	BEQ .original
.gone
	LDX.b !CurIndex
	LDA.w #$000C                 ; companero ausente
	STA.w !SprState,x
	STZ.w !SprXSpeed,x
	STZ.w !SprYSpeed,x
	LDY.b !KongType
	LDA.w #$0000
	STA.w $0512,y                ; ya no monta su animal
	LDA.l $7E0000+!PartnerFlags
	AND.w #$FFFE
	STA.l $7E0000+!PartnerFlags
	SEP #$20
	PLA                          ; sacar la vuelta del JSL (3 bytes)
	PLA
	PLA
	REP #$20
	JML $BFA6C2                  ; RTS de la rutina original (vuelve a quien la llamo)
.original
	LDA.l $7E1E15                ; instrucciones reemplazadas
	AND.w #$0020
	RTL

; -----------------------------------------------------------------------------
; Traspaso: el companero (jugado por el P2) pasa a ser el lider. Lo usa el juego
; cuando el lider recibe un golpe; aca, cuando el companero toca algo que solo
; atiende al lider (salida, bonus, barril canon, cuerda). Solo si los dos estan
; libres y el juego no esta congelado. Carry = 1 si se hizo. Preserva X e Y.
; (cualquier DB: todo con direcciones largas)
; -----------------------------------------------------------------------------
P2_Handoff:
	PHX
	PHY
	JSR P2_PartnerIsPlayer
	BCC .no
	LDA.l $7E0000+!KongFreeze
	BNE .no
	LDA.l $7E0000+!CurrentKong   ; (1 o 2: lo valido P2_PartnerIsPlayer)
	ASL
	TAX                          ; X = lider
	LDA.l $7E0000+!SprState,x
	JSR P2_IsFreeState
	BCC .no
	TXA
	EOR.w #$0006
	TAX                          ; X = companero
	LDA.l $7E0000+!SprState,x
	JSR P2_IsFreeState
	BCC .no
	; prioridad de dibujo: el lider va adelante (como hace el juego)
	LDA.l $7E0000+!SprOAMZ,x
	PHA
	TXA
	EOR.w #$0006
	TAX                          ; X = lider
	LDA.l $7E0000+!SprOAMZ,x
	PHA
	LDA $03,s
	STA.l $7E0000+!SprOAMZ,x
	TXA
	EOR.w #$0006
	TAX                          ; X = companero
	PLA
	STA.l $7E0000+!SprOAMZ,x
	PLA
	LDA.l $7E0000+!CurrentKong
	EOR.w #$0003
	STA.l $7E0000+!CurrentKong
	; recordar si el nuevo lider va montado (P2_LeadMountWatch no debe creer
	; que recien se subio a un animal)
	LDA.l $7E0000+!SprState,x
	LDY.w #$0001
	CMP.w #$0014
	BEQ +
	CMP.w #$0015
	BEQ +
	CMP.w #$0030
	BEQ +
	LDY.w #$0000
+
	TYA
	STA.l $7E0000+!PrevLeadRide
	PLY
	PLX
	SEC
	RTS
.no
	PLY
	PLX
	CLC
	RTS

; Carry = 1 si el lider ($82 = lider, DB = $7E) va por el aire: saltando (con o
; sin animal o barril), colgado de una cuerda, en un barril canon o la vagoneta saltando.
P2_LeadAirborne:
	LDX.b !CurIndex
	LDA.w !SprState,x
	CMP.w #$0001
	BEQ .yes
	CMP.w #$0015
	BEQ .yes
	CMP.w #$0019
	BEQ .yes
	CMP.w #$001A
	BEQ .yes
	CMP.w #$0025
	BEQ .yes
	CMP.w #$0026
	BEQ .yes
	CMP.w #$0028
	BEQ .yes
	CMP.w #$0029
	BEQ .yes
	CMP.w #$002F
	BEQ .yes
	CLC
	RTS
.yes
	SEC
	RTS

; Carry = 1 si el estado A del lider es de muerte, ausencia o cambio de cuarto.
P2_LeadGone:
	CMP.w #$000B
	BEQ .yes
	CMP.w #$0011
	BEQ .yes
	CMP.w #$003B
	BEQ .yes
	CMP.w #$003F
	BEQ .yes
	CMP.w #$000C
	BEQ .yes
	CMP.w #$000D
	BEQ .yes
	CMP.w #$0009
	BEQ .yes
	CMP.w #$0054
	BEQ .yes
	CMP.w #$0032
	BEQ .yes
	CMP.w #$0046
	BCC .no
	CMP.w #$0049                 ; $46-$48: entrando o saliendo de un cuarto
	BCC .yes
.no
	CLC
	RTS
.yes
	SEC
	RTS

; Carry = 1 si el estado A es "libre" (a pie, en el aire, nadando, montando o
; cargando un barril).
P2_IsFreeState:
	CMP.w #$0002
	BCC .yes
	CMP.w #$002B
	BEQ .yes
	CMP.w #$0014
	BEQ .yes
	CMP.w #$0015
	BEQ .yes
	CMP.w #$0030
	BEQ .yes
	CMP.w #$0017
	BCC .no
	CMP.w #$001B
	BCC .yes
.no
	CLC
	RTS
.yes
	SEC
	RTS

; -----------------------------------------------------------------------------
; Salida de nivel (sprite $13, CODE_BFD970). Devuelve Y = Kong a revisar: el
; lider, o el companero si el esta en la caja de salida y el lider no (traspaso).
; -----------------------------------------------------------------------------
P2_Exit13:
	JSL $809B9C                  ; Y = lider
	JSR P2_PartnerIsPlayer
	BCC .done
	LDX.b !CurIndex
	JSR .inbox
	BCS .done                    ; el lider esta en la salida: original
	TYA
	EOR.w #$0006
	TAY                          ; Y = companero
	JSR .inbox
	BCC .back
	JSR P2_Handoff
	BCS .done                    ; Y = companero, ahora lider
.back
	TYA
	EOR.w #$0006
	TAY                          ; Y = lider
.done
	RTL

; carry = Kong Y dentro de la caja de la salida X (misma prueba que el juego) y en el suelo
.inbox
	LDA.w !SprXPos,x
	SEC
	SBC.w #$0008
	CMP.w !SprXPos,y
	BPL .out
	CLC
	ADC.w #$0010
	CMP.w !SprXPos,y
	BMI .out
	LDA.w !SprYPos,x
	SEC
	SBC.w #$0008
	CMP.w !SprYPos,y
	BPL .out
	CLC
	ADC.w #$0010
	CMP.w !SprYPos,y
	BMI .out
	LDA.w !SprOnGround,y
	AND.w #$0001
	BEQ .out
	SEC
	RTS
.out
	CLC
	RTS

; -----------------------------------------------------------------------------
; Puerta de salida $6A (CODE_B6C45C): se activa cuando el lider pasa la X de la
; puerta, a menos de 5 px en vertical y en el suelo. Igual para el companero.
; -----------------------------------------------------------------------------
P2_ExitDoor:
	JSL $809B9C
	JSR P2_PartnerIsPlayer
	BCC .done
	LDX.b !CurIndex
	LDA.w !SprXPos,y
	CMP.w !SprXPos,x
	BPL .done                    ; el lider ya paso: original
	TYA
	EOR.w #$0006
	TAY                          ; companero
	LDA.w !SprXPos,y
	CMP.w !SprXPos,x
	BMI .back
	LDA.w !SprYPos,y
	SEC
	SBC.w !SprYPos,x
	BPL +
	EOR.w #$FFFF
	INC
+
	CMP.w #$0005
	BPL .back
	LDA.w !SprOnGround,y
	AND.w #$0001
	BEQ .back
	JSR P2_Handoff
	BCS .done
.back
	TYA
	EOR.w #$0006
	TAY
.done
	RTL

; Puerta de salida bajo el agua $6B (CODE_B6C3EB): basta con pasar su X.
P2_ExitDoorWater:
	JSL $809B9C
	JSR P2_PartnerIsPlayer
	BCC .done
	LDX.b !CurIndex
	LDA.w !SprXPos,y
	CMP.w !SprXPos,x
	BPL .done
	TYA
	EOR.w #$0006
	TAY
	LDA.w !SprXPos,y
	CMP.w !SprXPos,x
	BMI .back
	JSR P2_Handoff
	BCS .done
.back
	TYA
	EOR.w #$0006
	TAY
.done
	RTL

; -----------------------------------------------------------------------------
; Cuerdas. Las cuerdas solo se ofrecen al lider ($1AFD / $1AFF). Si el Kong del
; P2 salta a una cuerda (estado 1) y el lider no esta colgado, primero se prueba
; la cuerda con el companero (misma rutina del juego) y, si la alcanza, pasa a
; ser el lider: el juego lo cuelga y el otro sube detras, como en el original.
; -----------------------------------------------------------------------------
P2_RopeV:                    ; cuerda vertical (CODE_BFEF0C, rutina JSR del banco BF)
	JSR P2_RopeCandidate         ; carry = probar; Y = companero
	BCC .lead
	LDA.w $1AFD
	PHA
	STZ.w $1AFD
	PHY
	PHK
	PEA.w .back-1
	PEA.w (!RTL_InBankBF&$FFFF)-1
	CLC                          ; como deja el acarreo CODE_809B9C (CODE_B6FC84 puede
	JML $BFEF10                  ; volver sin tocarlo) -- resto de la rutina con Y = companero
.back
	REP #$30
	PLY
	LDA.w $1AFD
	BEQ +
	JSR P2_Handoff
+
	PLA
	STA.w $1AFD
.lead
	JSL $809B9C                  ; Y = lider (el nuevo, si hubo traspaso)
	RTL

P2_RopeS:                    ; cuerda que se balancea (CODE_B68000, DB = $B6, RTL)
	JSR P2_RopeCandidate
	BCC .lead
	LDA.w $1AFF
	PHA
	PHY
	PHK
	PEA.w .back-1
	JML $B68006                  ; resto de la rutina con Y = companero (carry = la alcanza)
.back
	REP #$30
	PLY
	BCC +
	JSR P2_Handoff
+
	PLA
	STA.w $1AFF
	LDX.b !CurIndex
.lead
	JSL $809B9C
	RTL

; carry = 1 si conviene probar la cuerda con el companero; Y = companero
P2_RopeCandidate:
	JSR P2_PartnerIsPlayer
	BCC .no
	LDA.l $7E0000+!CurrentKong
	ASL
	TAX                          ; X = lider
	LDA.l $7E0000+!SprState,x
	CMP.w #$0025
	BEQ .no                      ; el lider ya esta colgado
	CMP.w #$0026
	BEQ .no
	TXA
	EOR.w #$0006
	TAY
	TAX
	LDA.l $7E0000+!SprState,x
	CMP.w #$0001                 ; companero en el aire
	BNE .no
	LDX.b !CurIndex
	SEC
	RTS
.no
	LDX.b !CurIndex
	CLC
	RTS

print "Bloque v1.2 termina en: ", pc
warnpc $CA7000

; =============================================================================
; Animales: limite de 2 (espacio libre $D2FE8C-$D2FFFF)
; =============================================================================
org $D2FE90
; Carry = 1 si ya hay 2 o mas animales (Rambi/Expresso/Winky/Enguarde) libres
; o montados (no los que huyen tras un golpe). Preserva X e Y.
P2_TooManyAnimals:
	PHX
	PHY
	LDY.w #$0000
	LDX.w #$0006
-	LDA.l $7E0000+!SprID,x
	CMP.w #$0009
	BCC +
	CMP.w #$000D
	BCS +
	LDA.l $7E0000+!SprState,x
	CMP.w #$0002                 ; 0 libre / 1 montado
	BCS +
	INY
+
	INX
	INX
	CPX.w #$0034
	BNE -
	CPY.w #$0002                 ; carry = (cuenta >= 2)
	PLY
	PLX
	RTL

; El companero ($82) se deja caer sobre un animal libre a menos de $80 px en X
; (si hay): queda en el aire encima y el juego lo monta al caer.
P2_DropOnFreeAnimal:
	PHX
	PHY
	LDY.b !CurIndex              ; Y = companero
	LDX.w #$0006
-	LDA.l $7E0000+!SprID,x
	CMP.w #$0009
	BCC .next
	CMP.w #$000D
	BCS .next
	LDA.l $7E0000+!SprState,x
	BNE .next                    ; solo libres
	LDA.l $7E0000+!SprXPos,x
	SEC
	SBC.w !SprXPos,y
	BPL +
	EOR.w #$FFFF
	INC
+
	CMP.w #$0080
	BCS .next
	; encontrado: companero encima del animal
	LDA.l $7E0000+!SprXPos,x
	STA.w !SprXPos,y
	LDA.l $7E0000+!SprYPos,x
	CLC
	ADC.w #$0028
	STA.w !SprYPos,y
	LDA.w #$0001
	STA.w !SprState,y
	LDA.w #$FC00
	STA.w !SprYSpeed,y
	LDA.w #$0000
	STA.w !SprXSpeed,y
	BRA .done
.next
	INX
	INX
	CPX.w #$0034
	BNE -
.done
	PLY
	PLX
	RTL

; -----------------------------------------------------------------------------
; Etapas de bonus de animales (3 fichas): Rambi $D2, Winky $D3, Expresso $6C,
; Enguarde $A6 (y la de prueba $34). Como en el original: un solo animal (el
; Kong lider "es" el animal) y el otro Kong ausente; con dos animales la etapa
; se ponia muy lenta. Con el P2 jugando: el A de cualquiera de los dos le pasa
; el animal al otro jugador, y el numero 1/2 queda visible toda la etapa.
; -----------------------------------------------------------------------------
; carry = 1 si estamos en una etapa de animales
P2_InAnimalBonus:
	LDA.b $3E
	CMP.w #$00D2
	BEQ .yes
	CMP.w #$00D3
	BEQ .yes
	CMP.w #$006C
	BEQ .yes
	CMP.w #$00A6
	BEQ .yes
	CMP.w #$0034
	BEQ .yes
	CLC
	RTS
.yes
	SEC
	RTS

; carry = 1 en una etapa de animales (no traer al otro Kong). (JSL)
P2_BonusSolo:
	JSR P2_InAnimalBonus
	RTL

; Una vez por frame (antes del indicador).
P2_BonusFrame:
	LDA.l $7E0000+!CurrentKong   ; cambio de lider -> mostrar el indicador 1/2
	CMP.l $7E0000+!PrevLeadTag
	BEQ +
	STA.l $7E0000+!PrevLeadTag
	LDA.w #120
	STA.l $7E0000+!TagTimer
+
	JSR P2_InAnimalBonus
	BCC .done
	LDA.l $7E0000+!P2Joined
	BEQ .done
	LDA.l $7E0000+!TagTimer      ; indicador siempre visible
	CMP.w #$0002
	BCS +
	LDA.w #$0002
	STA.l $7E0000+!TagTimer
+
	; A (recien apretado) de cualquiera de los dos: el animal pasa al otro jugador
	LDA.l $7E0504
	ORA.l $7E0506
	AND.w #$0080
	BEQ .done
	LDA.l $7E0000+!SwapCooldown
	BNE .done
	LDA.w #20
	STA.l $7E0000+!SwapCooldown
	LDA.l $7E0000+!P2Swap
	EOR.w #$0001
	STA.l $7E0000+!P2Swap
	LDA.w #120
	STA.l $7E0000+!TagTimer
.done
	RTL

print "Bloque animales termina en: ", pc
warnpc $D30000

; =============================================================================
; v1.4: mas espacio entre los Kongs. El companero puede salir hasta ~80 px de
; la pantalla por cada lado (antes el borde lo frenaba); la camara sigue el
; punto medio pero sin dejar al lider fuera; el numero 1/2 del que queda fuera
; se dibuja en el borde (ver el indicador). (espacio libre $EEFF6F-$EEFFFF)
; =============================================================================
!WideMargin = $0050
!MidMaxX    = $0090          ; el punto medio se calcula con el companero a lo sumo a esta distancia del lider
!MidMaxY    = $0050

org $EEFF70
; X = companero (DB = $7E)
P2_ClampWide:
	LDA.w !SprXPos,x
	SEC
	SBC.w !CameraX               ; X en pantalla (con signo)
	CLC
	ADC.w #!WideMargin
	BMI .left
	CMP.w #256+!WideMargin+!WideMargin
	BCC .done
	LDA.w !CameraX               ; derecha
	CLC
	ADC.w #256+!WideMargin
	BRA .set
.left
	LDA.w !CameraX
	SEC
	SBC.w #!WideMargin
.set
	STA.w !SprXPos,x
	STZ.w !SprXSpeed,x
.done
	RTL

; A = d (companero - lider, con signo), $74 = limite -> A = d/2 limitado
P2_HalfClamped:
	BMI .neg
	CMP.b $74
	BCC .half
	LDA.b $74
	BRA .half
.neg
	EOR.w #$FFFF
	INC
	CMP.b $74
	BCC +
	LDA.b $74
+
	EOR.w #$FFFF
	INC
.half
	CMP.w #$8000                 ; division con signo
	ROR
	RTS

; X = companero, Y = lider (DB = $7E)
P2_MidX:
	LDA.w !SprXPos,y
	STA.w !SaveLeadX
	LDA.w #!MidMaxX
	STA.b $74
	LDA.w !SprXPos,x
	SEC
	SBC.w !SprXPos,y
	JSR P2_HalfClamped
	CLC
	ADC.w !SprXPos,y
	STA.w !SprXPos,y
	RTL

; X = companero, Y = lider (cualquier DB)
P2_MidY:
	PHX
	TYX
	LDA.l $7E0000+!SprYPos,x
	STA.l $7E0000+!SaveLeadY
	STA.b $72
	PLX
	LDA.w #!MidMaxY
	STA.b $74
	LDA.l $7E0000+!SprYPos,x
	SEC
	SBC.b $72
	JSR P2_HalfClamped
	CLC
	ADC.b $72
	PHX
	TYX
	STA.l $7E0000+!SprYPos,x
	PLX
	RTL

print "Bloque v1.4 termina en: ", pc
warnpc $EF0000

