#!/bin/bash
# Cola breve: corre uno por uno los .sh de pendientes/ con tope de 20 min. Solo GPU; no lanza Claude.
C=/workspaces/Nexusv2.0launch18octubre/entregables/cola_prioridad; cd /workspaces/Nexusv2.0launch18octubre; export GASTO_PERFIL=carlosfavelajeje
while true; do
  if [ ! -e $C/PAUSA ]; then
    T=$(ls $C/pendientes/*.sh 2>/dev/null | head -1)
    if [ -n "$T" ]; then
      echo "$(date -u +%F' '%T) ▶ $(basename $T)" >> $C/cola.log
      if timeout 1200 bash "$T" >> $C/cola.log 2>&1; then mv "$T" $C/hechos/; echo "$(date -u +%T) ✔ $(basename $T)" >> $C/cola.log
      else mv "$T" $C/fallidos/; echo "$(date -u +%T) ✘ $(basename $T) (fallo o tope de 20 min)" >> $C/cola.log; fi
      continue
    fi
  fi
  sleep 60
done
