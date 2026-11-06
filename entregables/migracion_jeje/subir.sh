#!/bin/bash
set -a; . /vol/claude-config/modal-carlosfavelajeje.env; set +a
echo "inicio $(date +%T)"
modal volume put -f nexus-workspace /vol/claude-config /claude-config && echo "config ok $(date +%T)"
modal volume put -f nexus-workspace /vol/workspaces /workspaces && echo "workspace ok $(date +%T)"
