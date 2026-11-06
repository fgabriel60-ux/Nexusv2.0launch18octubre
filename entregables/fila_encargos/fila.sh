#!/bin/bash
# Fila de encargos del tablero (5 nov 2026). Cuando Carlos aprieta «Disparar el plan», el encargo
# cae en buzon/para_nexus2/. Esto lo toma de UNO EN UNO y se lo da a Claude para que lo trabaje.
#
# De uno en uno a propósito: el 1 nov correr varios en paralelo tumbó la memoria del sandbox
# (1 CPU, 4 GB). Si hay uno corriendo, los demás esperan su turno.
#
# Dentro del encargo ya va escrito que las IMÁGENES se generan con Codex y que hay que avisarle
# el progreso a Carlos por WhatsApp conforme se avanza.
RAIZ=/workspaces/Nexusv2.0launch18octubre
B=$RAIZ/buzon/para_nexus2
F=$RAIZ/entregables/fila_encargos
cd $RAIZ
mkdir -p $B $RAIZ/buzon/hecho $F
while true; do
  T=$(ls $B/*.md 2>/dev/null | head -1)
  if [ -n "$T" ]; then
    N=$(basename "$T" .md)
    echo "$(date -u +%F' '%T) ▶ $N" >> $F/fila.log
    if claude -p "$(cat "$T")" --permission-mode acceptEdits \
         < /dev/null > "$F/$N.log" 2>&1; then
      mv "$T" $RAIZ/buzon/hecho/; echo "$(date -u +%T) ✔ $N" >> $F/fila.log
    else
      echo "$(date -u +%T) ✘ $N (se queda en el buzón para revisarlo)" >> $F/fila.log
      mv "$T" "$T.fallido"
    fi
    continue
  fi
  sleep 45
done
