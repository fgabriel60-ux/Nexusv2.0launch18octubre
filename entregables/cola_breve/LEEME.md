# Cola breve (solo GPU, sin Claude)
- Encolar: `entregables/cola_breve/pendientes/AAAAMMDD_HHMM_<nombre>.sh` (cd a la raíz; GASTO_PERFIL=carlosfavelajeje ya está puesto por el runner).
- Cada trabajo tiene tope de 20 min (`timeout 1200`). Si pasa de ahí, va a `fallidos/`.
- Corre uno a la vez. Log: `entregables/cola_breve/cola.log`.
- Para pausar sin borrar: mover el archivo a `pausados/`, o crear `entregables/cola_breve/PAUSA`.
- Nada de `claude -p` aquí: son solo scripts de GPU (gasto_modal.py run ...).
