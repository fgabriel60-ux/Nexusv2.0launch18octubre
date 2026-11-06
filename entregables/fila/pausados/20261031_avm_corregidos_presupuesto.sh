#!/bin/bash
# Pausado: tope de gasto $14.70 alcanzado. No lanzar sin ampliación explícita de Carlos.
set -e
cd /workspaces/Nexusv2.0launch18octubre
GASTO_PERFIL=fgabriel60 python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/20261031_avm_corregidos/lote.json --tokens 4500 > entregables/glimmer_evaluador/20261031_avm_corregidos/glimmer.log 2>&1
