#!/bin/bash
set -e
cd /workspaces/Nexusv2.0launch18octubre
python3 entregables/glimmer_evaluador/evaluar.py entregables/victor_guillermo_20261031/anuncios.json entregables/glimmer_evaluador/20261031_victor_guillermo
GASTO_PERFIL=fgabriel60 python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/20261031_victor_guillermo/lote.json --tokens 3000 > entregables/glimmer_evaluador/20261031_victor_guillermo/glimmer.log 2>&1
