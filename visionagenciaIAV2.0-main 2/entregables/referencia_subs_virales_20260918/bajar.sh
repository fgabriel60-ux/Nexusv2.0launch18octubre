#!/bin/bash
# Los que más se parecen a lo nuestro: dentistas hispanohablantes, videos cortos, muy vistos.
set -u
while IFS='|' read -r nombre url; do
  [ -f "videos/$nombre.mp4" ] && { echo "ya está $nombre"; continue; }
  yt-dlp -q --no-warnings -f "mp4" -o "videos/$nombre.%(ext)s" "$url" 2>&1 | tail -1 || echo "FALLÓ $nombre"
done <<'EOF'
01_doctorleonperu_29s_1.7M|https://www.tiktok.com/@doctorleonperu/video/7682513956929359124
02_odontoseguro_15s_1.5M|https://www.tiktok.com/@odontoseguro123.4/video/7663537415079939346
03_dentalsonris_38s_1.4M|https://www.tiktok.com/@dental.sonris/video/7602448293825711368
04_felicianorojas_12s_1.3M|https://www.tiktok.com/@dr.felicianorojas/video/7676175915923164436
05_dentaltreatment_20s_2.7M|https://www.tiktok.com/@dentaltreatmentweb/video/7670629719372483862
06_smiledoc_8s_16M|https://www.tiktok.com/@smile_doc/video/7668141929267301662
EOF
ls -la videos/
