#!/bin/bash
echo "=== Estado SMART del disco (salud fisica) ==="
diskutil info disk0 | grep -i smart

echo
echo "=== Lista de discos y particiones ==="
diskutil list

echo
echo "=== Verificacion del volumen raiz (solo lectura, no repara) ==="
diskutil verifyVolume /

echo
echo "=== Espacio y estado APFS del contenedor ==="
diskutil apfs list | head -40

echo
echo "=== Mensajes recientes del sistema relacionados a disco/IO ==="
log show --predicate 'eventMessage contains "I/O error" or eventMessage contains "disk" or eventMessage contains "fsck"' --last 1h 2>/dev/null | tail -50

echo
echo "=== FIN ==="
