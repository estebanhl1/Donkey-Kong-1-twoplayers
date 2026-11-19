; =============================================================================
; Pantalla inicial: dedicatoria + link del repo.
;
; Se engancha al vector de reset ($808000): se muestra antes que todo lo demas
; y al salir sigue el arranque original como si nada (el juego reinicia el PPU,
; la RAM y la pila por su cuenta). Sale con cualquier boton de cualquier
; control (despues de !SplashMinFrames) o sola a los !SplashMaxFrames.
;
; Mientras esta en pantalla deja !SplashMarker = $5A (lo usan los tests para
; saltarla, ver Emu.skip_splash en tools/emu.py).
; =============================================================================

!SplashMarker    = $04C0     ; WRAM $7E04C0 (zona libre)
!SplashMinFrames = 45        ; ~0.75 s antes de aceptar un boton
!SplashMaxFrames = 1200      ; ~20 s y sigue sola

!TileMapVRAM     = $0400     ; mapa de BG1 (palabras); el grafico de la letra N es el tile N

org $808000                  ; reset: CLC / XCE / SEI / REP #$20
	JML Splash               ; 4 bytes; el operando de REP ($808004) queda sin ejecutar

org $CA7900
Splash:
	SEI
	CLC
	XCE                          ; modo nativo
	REP #$30
	LDA.w #$01FF
	TCS
	LDA.w #$0000
	TCD                          ; D = 0
	SEP #$20
	PHA
	PLB                          ; DB = $00 (registros del PPU)

	LDA.b #$80
	STA.w $2100                  ; pantalla apagada
	STZ.w $4200                  ; sin NMI ni lectura de controles por ahora
	STZ.w $420C                  ; sin HDMA

	; Registros del PPU en 0 (dos pasadas: los de scroll se escriben dos veces)
	LDX.w #$0001
-	STZ.w $2100,x
	INX
	CPX.w #$0034
	BNE -
	LDX.w #$000D
-	STZ.w $2100,x
	INX
	CPX.w #$0015
	BNE -

	; VRAM en 0 (DMA de un byte fijo, 64 KB)
	LDA.b #$80
	STA.w $2115                  ; +1 palabra despues de escribir $2119
	LDX.w #$0000
	STX.w $2116
	LDA.b #$09                   ; fuente fija, dos registros ($2118/$2119)
	STA.w $4300
	LDA.b #$18
	STA.w $4301
	LDX.w #SplashZero
	STX.w $4302
	LDA.b #SplashZero>>16
	STA.w $4304
	LDX.w #$0000                 ; 0 = 65536 bytes
	STX.w $4305
	LDA.b #$01
	STA.w $420B

	; Letras: 1 bit por pixel -> plano 0 (color 1 de cada paleta). Tile $20 en adelante.
	LDX.w #$0020*8
	STX.w $2116
	LDX.w #$0000
-	LDA.l SplashFont,x
	STA.w $2118
	STZ.w $2119
	INX
	CPX.w #$0060*8
	BNE -

	; Texto: [direccion VRAM (palabra)] [atributo] [letras...] 0, fin = $FFFF
	LDX.w #$0000
.line
	REP #$20
	LDA.l SplashText,x
	CMP.w #$FFFF
	BEQ .text_done
	STA.w $2116
	SEP #$20
	INX
	INX
	LDA.l SplashText,x
	STA.b $00                    ; atributo (paleta) de la linea
	INX
.char
	LDA.l SplashText,x
	BEQ .eol
	STA.w $2118
	LDA.b $00
	STA.w $2119
	INX
	BRA .char
.eol
	INX
	BRA .line
.text_done
	SEP #$20

	; Paletas
	STZ.w $2121
	LDX.w #$0000
-	LDA.l SplashPal,x
	STA.w $2122
	INX
	CPX.w #SplashPalEnd-SplashPal
	BNE -

	; Modo 0, solo BG1, mapa en !TileMapVRAM, letras en $0000
	STZ.w $2105
	LDA.b #!TileMapVRAM>>8
	STA.w $2107
	STZ.w $210B
	LDA.b #$01
	STA.w $212C

	LDA.b #$5A
	STA.l $7E0000+!SplashMarker
	LDA.b #$01
	STA.w $4200                  ; lectura automatica de controles
	LDA.b #$0F
	STA.w $2100                  ; pantalla encendida

	; Esperar: cualquier boton nuevo (de P1 o P2) o el tiempo maximo.
	; $02 = frames, $04 = botones del frame anterior
	REP #$20
	STZ.b $02
	LDA.w #$FFFF
	STA.b $04                    ; como si hubiera algo apretado: obliga a soltar primero
.wait
	SEP #$20
-	LDA.w $4212
	BPL -                        ; esperar el vblank
-	LDA.w $4212
	BMI -                        ; esperar el fin del vblank (lectura de controles lista)
	REP #$20
	INC.b $02
	LDA.b $02
	CMP.w #!SplashMaxFrames
	BCS .exit
	LDA.w $4218
	ORA.w $421A
	TAY
	LDA.b $02
	CMP.w #!SplashMinFrames
	BCC .remember
	LDA.b $04
	BNE .remember                ; habia algo apretado: esperar a que suelte
	TYA
	BNE .exit
.remember
	STY.b $04
	BRA .wait

.exit
	SEP #$30
	LDA.b #$80
	STA.w $2100                  ; pantalla apagada
	STZ.w $4200
	LDA.b #$00
	STA.l $7E0000+!SplashMarker
	; Seguir el arranque original justo despues de lo que reemplazamos:
	; CLC/XCE/SEI ya hechos (nativo, X 8 bits), falta REP #$20.
	REP #$20
	JML $808005

SplashZero:
	db $00

; Cada linea: direccion en el mapa (fila*32+columna, centrada), atributo (paleta << 2), texto, 0
SplashText:
	dw !TileMapVRAM+(3*32)+6
	db $04, "DONKEY KONG COUNTRY", $00
	dw !TileMapVRAM+(5*32)+5
	db $08, "MODO 2 JUGADORES CO-OP", $00
	dw !TileMapVRAM+(10*32)+8
	db $0C, "Para Anibal H.,", $00
	dw !TileMapVRAM+(12*32)+11
	db $0C, "mi hijo ", $7F, $00    ; $7F = corazon
	dw !TileMapVRAM+(17*32)+10
	db $14, "Repositorio:", $00
	dw !TileMapVRAM+(19*32)+5
	db $10, "github.com/estebanhl1/", $00
	dw !TileMapVRAM+(20*32)+4
	db $10, "donkey-kong-1-twoplayers", $00
	dw !TileMapVRAM+(25*32)+9
	db $14, "Presiona START", $00
	dw $FFFF

; BGR555: color 0 = fondo; color 1 de las paletas 1..5 = texto
SplashPal:
	dw $1841, $7FFF, $0000, $0000   ; 0: fondo azul muy oscuro
	dw $1841, $033F, $0000, $0000   ; 1: amarillo
	dw $1841, $7FFF, $0000, $0000   ; 2: blanco
	dw $1841, $199F, $0000, $0000   ; 3: naranjo
	dw $1841, $7F0C, $0000, $0000   ; 4: celeste
	dw $1841, $5294, $0000, $0000   ; 5: gris
SplashPalEnd:

warnpc $CA7C00
org $CA7C00
incsrc splash_font.asm
warnpc $CA8000
