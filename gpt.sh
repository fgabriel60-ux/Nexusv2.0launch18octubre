#!/bin/bash
# ChatGPT (Codex CLI, cuenta ChatGPT de Carlos) para tareas de texto y ahorrar uso de Claude.
# Uso: ./gpt.sh "instrucción"   ·   cat archivo | ./gpt.sh "resume esto"
export CODEX_HOME=/vol/claude-config/codex
cd /tmp
if [ -t 0 ]; then p="$1"; else p="$1

$(cat)"; fi
codex exec --skip-git-repo-check --sandbox read-only "$p" 2>/dev/null | sed '/^tokens used/,$d'
