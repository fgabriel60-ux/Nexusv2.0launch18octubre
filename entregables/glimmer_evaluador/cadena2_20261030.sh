#!/bin/bash
# Cadena 2 (30 oct), una GPU a la vez: Guillermo Pixar v2 → Giovanni v3 (cara real) → José v6 (sin rojo, sin labios sueltos) → Glimmer: califica los 3 + estrategia 10/10/10 del tatuador.
R=/workspaces/Nexusv2.0launch18octubre; cd $R; export GASTO_PERFIL=charlyfavela666
L=clientes/Guillermo/pixar_v2_20261030/modal.log
until grep -qi "saldo\|Traceback" $L; do sleep 30; done
echo "== guillermo terminó"; python3 clientes/Guillermo/pixar_v2_20261030/armar_pixar_v2.py || echo "FALLO armado guillermo"
python3 gasto_modal.py run clientes/Giovanni/video_v3_20261030/giovanni_v3_modal.py > clientes/Giovanni/video_v3_20261030/modal.log 2>&1; echo "== giovanni gpu"; tail -2 clientes/Giovanni/video_v3_20261030/modal.log
python3 clientes/Giovanni/video_v3_20261030/armar_giovanni_v3.py > clientes/Giovanni/video_v3_20261030/armado.log 2>&1 || echo "FALLO armado giovanni"
python3 gasto_modal.py run clientes/Jose/obrero_v6_20261030/jose_v6_modal.py > clientes/Jose/obrero_v6_20261030/modal.log 2>&1; echo "== jose gpu"; tail -2 clientes/Jose/obrero_v6_20261030/modal.log
python3 clientes/Jose/armado_20261029/armar_jose_v6.py > clientes/Jose/obrero_v6_20261030/armado.log 2>&1 || echo "FALLO armado jose"
python3 entregables/glimmer_evaluador/evaluar.py entregables/glimmer_evaluador/anuncios_20261030.json entregables/glimmer_evaluador/20261030 entregables/glimmer_evaluador/extra_20261030.json
python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/20261030/lote.json --tokens 3000 > entregables/glimmer_evaluador/20261030/glimmer.log 2>&1
echo "== FIN"
