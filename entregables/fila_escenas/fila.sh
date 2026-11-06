#!/bin/bash
# Fila de ESCENAS (Qwen/H3) en paralelo a la de Glimmer (otro volumen) (30 oct): corre uno por uno los .sh de pendientes/ (orden por nombre), una GPU a la vez, y los mueve a hechos/ o fallidos/.
# Encolar: escribir pendientes/<AAAAMMDD_HHMM>_<cliente>.sh (cd a la raíz y GASTO_PERFIL=carlosfavelajeje ya vienen puestos). Log: fila.log
# Espera a que termine cualquier cadena anterior (cadena*.sh) para no correr dos GPU contra el mismo volumen.
F=/workspaces/Nexusv2.0launch18octubre/entregables/fila_escenas; cd /workspaces/Nexusv2.0launch18octubre; export GASTO_PERFIL=carlosfavelajeje
while true; do
  if [ -e $F/sin_espera ]; then
    T=$(ls $F/pendientes/*.sh 2>/dev/null | head -1)
    if [ -n "$T" ]; then
      echo "$(date -u +%F' '%T) ▶ $(basename $T)" >> $F/fila.log
      if bash "$T" >> $F/fila.log 2>&1; then mv "$T" $F/hechos/; echo "$(date -u +%T) ✔ $(basename $T)" >> $F/fila.log
      else mv "$T" $F/fallidos/; echo "$(date -u +%T) ✘ $(basename $T)" >> $F/fila.log; fi
      continue
    fi
  fi
  sleep 60
done
