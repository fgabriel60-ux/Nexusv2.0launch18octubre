#!/bin/bash
echo "=== Fecha y hora actuales del sistema ==="
date

echo
echo "=== Zona horaria ==="
systemsetup -gettimezone 2>/dev/null || echo "(necesita sudo, ignora si pide password)"

echo
echo "=== Fecha segun NTP (si hay red) ==="
sntp -sS time.apple.com 2>&1 | tail -3

echo
echo "=== FIN ==="
