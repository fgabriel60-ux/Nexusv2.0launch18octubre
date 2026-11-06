#!/bin/bash
# PAUSADO: vigía alcanzó límite $14.70. No mover a pendientes sin presupuesto autorizado.
set -e
cd /workspaces/Nexusv2.0launch18octubre
python3 entregables/glimmer_evaluador/evaluar.py entregables/victor_guillermo_20261031/anuncios_finales_pendientes.json entregables/glimmer_evaluador/20261031_victor_guillermo_finales
GASTO_PERFIL=fgabriel60 python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/20261031_victor_guillermo_finales/lote.json --tokens 3000 > entregables/glimmer_evaluador/20261031_victor_guillermo_finales/glimmer.log 2>&1
