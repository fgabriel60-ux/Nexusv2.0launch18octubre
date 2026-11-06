set -e
cd /workspaces/Nexusv2.0launch18octubre
python3 entregables/glimmer_evaluador/evaluar.py entregables/glimmer_evaluador/anuncios_20261031_jose_v9d.json entregables/glimmer_evaluador/20261031_jose_v9d
GASTO_PERFIL=fgabriel60 python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote entregables/glimmer_evaluador/20261031_jose_v9d/lote.json --tokens 4500 > entregables/glimmer_evaluador/20261031_jose_v9d/glimmer.log 2>&1
