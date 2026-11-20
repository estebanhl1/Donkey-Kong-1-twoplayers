#!/bin/bash
# Bateria de regresion del parche 2P. Uso: tools/regresion.sh [--completo]
#   --completo  agrega el recorrido de 40 niveles (unos 10 minutos)
# Requiere roms/dkc_2p.sfc (./build.sh) y los savestates de work/.
cd "$(dirname "$0")/.."
PY=tools/venv/bin/python
ROM=roms/dkc_2p.sfc
OUT=$(mktemp -d)
pass=0; fail=0
ok()   { echo "  [OK]    $1"; pass=$((pass+1)); }
bad()  { echo "  [FALLA] $1"; fail=$((fail+1)); }
run()  { "$@" 2>&1 | grep -v Map_; }

echo "== Modo One player = original"
r=$(run $PY tools/test_1p_identical.py)
[ "$(echo "$r" | grep -c IDENTICO)" = "5" ] && ok "One player identico al original (5 escenas)" || { bad "One player difiere"; echo "$r"; }

export COOP=1
echo "== Co-op (Two player team)"
r=$(run $PY tools/test_hurt.py $ROM)
echo "$r" | grep -qE "f 400 DK 032A st00 \| Di 03[0-9A-F]{2} st00" && ok "golpe al companero -> reaparece" || bad "golpe al companero"
echo "$r" | grep -qE "DK [0-9A-F]{4} st23 \| Di [0-9A-F]{4} st00 \| lider 2" && ok "golpe al lider -> traspaso y reaparece" || bad "golpe al lider"
[ "$(run $PY tools/test_drop.py $ROM | grep -c MATA)" = "6" ] && ok "pisoton de los dos Kongs" || bad "pisoton"
[ "$(run $PY tools/test_pickups.py $ROM work/1p_twokongs.state 1500 | grep -c 'companero: RECOGE')" = "2" ] && ok "objetos con el P2" || bad "objetos"
run $PY tools/test_lost.py $ROM | grep -q "VOLVIO a" && ok "el Kong del P2 vuelve aunque el P2 no toque nada" || bad "reaparicion sin input"
run $PY tools/test_cart.py $ROM 1 $OUT/c.png | grep -q "st2E | Di .* st0C" && ok "vagoneta" || bad "vagoneta"
run $PY tools/test_animals.py $ROM work/spr_JungleHijinxs_18.state $OUT/a.png | tail -1 | grep -q "st1 jinete=2 .*st1 jinete=4" && ok "dos animales, cada uno con su jinete" || bad "animales"
r=$(run $PY tools/test_rhino_coop.py $ROM)
echo "$r" | grep -q "B P2 jugando: animales 2, Diddy montado True" && ok "caja de Rambi con el P2 jugando: Diddy se sube solo" || { bad "caja con P2 jugando"; echo "$r"; }
echo "$r" | grep -q "A P2 sin tocar: animales al abrir 2, DK montado True, Diddy montado True" && ok "caja con el P2 sin tocar el control: 2 Rambis y Diddy recibe el suyo" || { bad "caja con P2 quieto"; echo "$r"; }
run $PY tools/test_cannon.py $ROM dk | grep -q "st28 | Di .* st35" && ok "barril canon: el P2 entra con el lider" || bad "barril canon"
run $PY tools/test_forkB_rope2.py $ROM dk | grep -q "st25 | Di .* st34" && ok "cuerda: el lider no se suelta, el P2 sube detras" || bad "cuerda"
run $PY tools/test_forkE_lift.py $ROM | tail -1 | grep -q "Di y00A9" && ok "ascensor lleva a los dos" || bad "ascensor"
run $PY tools/test_forkD_bonusend.py $ROM | grep -q "SALE DEL BONUS" && ok "fin de bonus" || bad "fin de bonus"
run $PY tools/test_forkC_bossbot.py $ROM VeryGnawty E0 diddy_p2 3000 | grep -q "TERMINA" && ok "jefe Very Gnawty con el P2 solo" || bad "jefe Very Gnawty"
r=$(run $PY tools/test_camera.py $ROM | head -2)
echo "$r" | grep -q "ambos derecha .*final DK 7[2-4] Diddy 8[01]" && ok "camara compartida" || { bad "camara compartida"; echo "$r"; }
r=$(run $PY tools/test_cores.py $ROM | grep RESULTADO)
echo "$r" | grep -q "8/8" && ok "co-op desde cero (menu Team)" || { bad "co-op desde cero"; echo "$r"; }

echo "== Arreglos v1.2"
r=$(run $PY tools/test_v12.py $ROM)
for c in reaparecer_en_checkpoint:"reaparecer en el checkpoint con un solo Kong (no se congela)" \
         hoyo_sin_perder_vida:"el companero cae a un hoyo: sin perder vida" \
         no_queda_patinando:"el companero no queda patinando (estado 1 en el suelo)" \
         p2_cuerda_sola:"el P2 se cuelga solo de una cuerda" \
         p2_barril_bonus:"el P2 entra solo a un barril de bonus" \
         p2_puerta_salida:"el P2 sale solo por la puerta" \
         a_intercambia:"A intercambia los personajes" \
         bonus_animales_sin_kong_extra:"bonus de animales: no aparece el otro Kong" \
         reaparece_a_tiempo:"el Kong que falta vuelve a los ~3 s aunque el lider este ocupado" \
         dk_junta_bananas:"DK tambien junta bananas sueltas" \
         lider_cae_sin_perder_vida:"cae el lider a un hoyo: el otro sigue, sin perder vida" \
         indicador_1p_2p:"indicador 1/2 y banana del lider al intercambiar" \
         vagoneta_salta_con_p2:"vagoneta: el B del P2 hace saltar el carro" \
         animales_sin_duplicar:"bajarse y subirse no crea animales de mas"; do
  echo "$r" | grep -q "^OK ${c%%:*}" && ok "${c#*:}" || { bad "${c#*:}"; echo "$r" | grep "${c%%:*}"; }
done

if [ "$1" = "--completo" ]; then
  echo "== 40 niveles"
  r=$(run $PY tools/survey.py $ROM $OUT/s | grep -cE "2kongs=NO|P2mueve=NO|CONGELADO")
  [ "$r" = "0" ] && ok "40 niveles sin problemas" || bad "40 niveles: $r con problemas"
fi
echo
echo "RESULTADO: $pass OK, $fail fallas"
rm -rf "$OUT"
[ $fail = 0 ]
