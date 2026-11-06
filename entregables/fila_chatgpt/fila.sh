#!/bin/bash
# Fila de ChatGPT (5 nov 2026, pedido de Carlos: «los cambios que apliques desde el tablero se
# hacen en chatgpt»). Corre de uno en uno los encargos .md que deja el tablero.
#
# SEGURIDAD, a propósito:
# - Solo lee archivos .md de pendientes/, y le pasa a codex la RUTA, nunca el texto interpolado
#   en la línea de comando: así un encargo no puede inyectar comandos de shell.
# - Codex corre con --sandbox workspace-write, acotado al workspace. NO se usa
#   --dangerously-bypass-approvals-and-sandbox: esta carpeta se puede escribir desde el tablero,
#   que está en internet, y un agente con permisos totales sobre lo que llegue de ahí es un
#   agujero. Si un encargo necesita más permiso, lo corre una persona a mano.
# - `< /dev/null`: sin eso codex se queda esperando entrada y nunca arranca.
F=/workspaces/Nexusv2.0launch18octubre/entregables/fila_chatgpt
cd /workspaces/Nexusv2.0launch18octubre
mkdir -p $F/pendientes $F/hechos $F/fallidos
while true; do
  T=$(ls $F/pendientes/*.md 2>/dev/null | head -1)
  if [ -n "$T" ]; then
    N=$(basename "$T" .md)
    echo "$(date -u +%F' '%T) ▶ $N" >> $F/fila.log
    if codex exec --skip-git-repo-check --sandbox workspace-write \
         -C /workspaces/Nexusv2.0launch18octubre "$(cat "$T")" \
         < /dev/null > "$F/$N.log" 2>&1; then
      mv "$T" $F/hechos/; echo "$(date -u +%T) ✔ $N" >> $F/fila.log
    else
      mv "$T" $F/fallidos/; echo "$(date -u +%T) ✘ $N" >> $F/fila.log
    fi
    continue
  fi
  sleep 30
done
