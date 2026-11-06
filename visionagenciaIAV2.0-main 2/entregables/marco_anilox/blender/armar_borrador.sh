#!/bin/bash
# Arma el borrador del anilox: 12 fps (cuadros pares 144..720) → 24 fps interpolado, 540×960 → 1080×1920.
set -e
cd "$(dirname "$0")"
ffmpeg -v error -y -framerate 12 -pattern_type glob -i "anilox_borrador/frame_*.png" \
  -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1080:1920:flags=lanczos" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -movflags +faststart ANILOX_MARCO_BORRADOR_1080.mp4
ffmpeg -v error -y -i ANILOX_MARCO_BORRADOR_1080.mp4 -vf scale=720:1280 -c:v libx264 -crf 24 -profile:v baseline \
  -level 3.1 -pix_fmt yuv420p -movflags +faststart ANILOX_MARCO_BORRADOR_WHATSAPP.mp4
echo listo
