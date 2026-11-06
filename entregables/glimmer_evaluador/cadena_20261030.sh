#!/bin/bash
# Cadena del 30 oct: espera Guillermo Pixar v2 → arma → Giovanni v3 (su cara real) → arma → Glimmer califica los 3 anuncios. Una GPU a la vez.
R=/workspaces/Nexusv2.0launch18octubre; cd $R; export GASTO_PERFIL=charlyfavela666
L=clientes/Guillermo/pixar_v2_20261030/modal.log
until grep -q "saldo\|Traceback" $L; do sleep 30; done
echo "== guillermo terminó"; python3 clientes/Guillermo/pixar_v2_20261030/armar_pixar_v2.py || echo "FALLO armado guillermo"
python3 gasto_modal.py run clientes/Giovanni/video_v3_20261030/giovanni_v3_modal.py > clientes/Giovanni/video_v3_20261030/modal.log 2>&1
tail -3 clientes/Giovanni/video_v3_20261030/modal.log
python3 clientes/Giovanni/video_v3_20261030/armar_giovanni_v3.py > clientes/Giovanni/video_v3_20261030/armado.log 2>&1 || echo "FALLO armado giovanni"
python3 entregables/glimmer_evaluador/evaluar.py entregables/glimmer_evaluador/anuncios_20261030.json entregables/glimmer_evaluador/20261030
python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/20261030/lote.json --tokens 2500 > entregables/glimmer_evaluador/20261030/glimmer.log 2>&1
echo "== FIN"; grep -n "saldo\|gast" clientes/Guillermo/pixar_v2_20261030/modal.log clientes/Giovanni/video_v3_20261030/modal.log entregables/glimmer_evaluador/20261030/glimmer.log | tail -6
