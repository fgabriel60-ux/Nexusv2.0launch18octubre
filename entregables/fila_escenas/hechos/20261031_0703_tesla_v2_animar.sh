while ! grep -qE "Saldo restante|Traceback" entregables/specs_20261031/mariano_r4_animar.log 2>/dev/null; do sleep 20; done
GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run clientes/_escenas_carlos/escenas_carlos_modal.py::animar --spec entregables/specs_20261031/tesla_mexico_v2.json > entregables/specs_20261031/tesla_mexico_v2_animar.log 2>&1
