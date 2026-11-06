#!/bin/bash
# ChatGPT → Claude: pregunta corta a Claude (con su memoria de Carlos y el workspace). Gasta uso de Claude: máx. 5 al día.
# Uso: herramientas/preguntar_claude.sh "pregunta"
L=/vol/claude-config/codex/preguntas_claude.log; HOY=$(date +%F)
N=$(grep -c "^$HOY" "$L" 2>/dev/null || echo 0)
if [ "$N" -ge 5 ]; then echo "Límite de 5 preguntas a Claude por hoy alcanzado (cuidar uso hasta el martes). Busca en la memoria /vol/claude-config/projects/*/memory o pregúntale a Carlos."; exit 0; fi
echo "$HOY $(date +%T) $1" | cut -c1-300 >> "$L"
cd /workspaces/Nexusv2.0launch18octubre
timeout 600 claude -p "Te pregunta ChatGPT, el otro asistente de Carlos. Responde en español, corto y concreto (máx. 10 líneas), solo con lo que sabes de tu memoria y del workspace; no hagas cambios ni mandes mensajes. Pregunta: $1" --max-turns 6 --allowedTools "Read Grep Glob" 2>/dev/null
