#!/usr/bin/env bash
# Enciende Claude Code en Modal (sandbox nexus-claude) y abre una terminal dentro. Apagar: ./iniciar_claude_modal.sh apagar
export MODAL_PROFILE=${MODAL_PROFILE:-fabelagabriel645}
cd "$(dirname "$0")"
if [ "$1" = apagar ]; then python3 -c "import nexus_claude_modal as n; n.apagar()"; exit; fi
python3 -c "import nexus_claude_modal as n; n.encender()" 2>/dev/null || echo "(el sandbox ya estaba encendido)"
ID=$(python3 -c "import modal; print(modal.Sandbox.from_name('nexus-claude','nexus-claude').object_id)") && modal shell "$ID" -c "bash -lc 'cd /workspaces/Nexusv2.0launch18octubre && claude remote-control --name nexus'"
