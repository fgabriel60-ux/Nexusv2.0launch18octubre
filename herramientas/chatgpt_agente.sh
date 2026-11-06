#!/bin/bash
# Lanza ChatGPT (Codex, cuenta de Carlos) con acceso total al workspace, en segundo plano.
# Autorizado por Carlos el 31 oct 2026 («autorizo la opción b»). Reglas para ChatGPT: AGENTS.md (no escribir a clientes).
# Uso: herramientas/chatgpt_agente.sh ARCHIVO_TAREA.md ARCHIVO_LOG
set -e
TAREA="$1"; LOG="$2"
[ -f "$TAREA" ] && [ -n "$LOG" ] || { echo "uso: $0 tarea.md salida.log"; exit 1; }
export CODEX_HOME=/vol/claude-config/codex
cd /workspaces/Nexusv2.0launch18octubre
nohup setsid codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C /workspaces/Nexusv2.0launch18octubre "$(cat "$TAREA")" > "$LOG" 2>&1 < /dev/null &
echo "ChatGPT trabajando · pid $! · log $LOG"
