#!/bin/bash
set -e
cd /__modal/volumes/vo-N6gOPxHfXSf5HzbsmuqjJ3/workspaces/Nexusv2.0launch18octubre
if [ "$(grep -o 'assistant to=user' entregables/glimmer_evaluador/ronda1c_20261031/glimmer.log 2>/dev/null | wc -l)" -lt 8 ]; then
  python3 entregables/glimmer_evaluador/evaluar.py entregables/glimmer_evaluador/anuncios_ronda1c_20261031.json entregables/glimmer_evaluador/ronda1c_20261031 && GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/ronda1c_20261031/lote.json --tokens 4500 > entregables/glimmer_evaluador/ronda1c_20261031/glimmer.log 2>&1
fi
if [ "$(grep -o 'assistant to=user' entregables/glimmer_evaluador/ronda1d_20261031/glimmer.log 2>/dev/null | wc -l)" -lt 4 ]; then
  python3 entregables/glimmer_evaluador/evaluar.py entregables/glimmer_evaluador/anuncios_ronda1d_20261031.json entregables/glimmer_evaluador/ronda1d_20261031 && GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/ronda1d_20261031/lote.json --tokens 4500 > entregables/glimmer_evaluador/ronda1d_20261031/glimmer.log 2>&1
fi
