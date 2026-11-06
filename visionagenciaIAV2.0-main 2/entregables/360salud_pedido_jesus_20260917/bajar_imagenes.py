"""Baja las imagenes que mando Jesus hoy (referencias de donde va el precio)."""
import json, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from leer_chat import accion

AQUI = Path(__file__).resolve().parent
IMGS = AQUI / 'imagenes'
IMGS.mkdir(exist_ok=True)
MX = timezone(timedelta(hours=-7))

res = json.loads((AQUI / 'crudo_mensajes.json').read_text())
for it in res['data']['data']:
    d = it['message']['_data']
    if d.get('type') not in ('image', 'document'):
        continue
    mid = d['id']['_serialized']
    quien = 'CARLOS' if d['id'].get('fromMe') else 'JESUS'
    cuando = datetime.fromtimestamp(d['t'], MX)
    r = accion('download-media', {'messageId': mid})
    media = ((r.get('data') or {}).get('data') or {}).get('media') or {}
    url = media.get('url')
    if not url:
        print('sin media:', cuando.strftime('%H:%M'), quien, d.get('type')); continue
    ext = {'image/jpeg': 'jpg', 'image/png': 'png',
           'application/pdf': 'pdf'}.get(media.get('mimetype', '').split(';')[0], 'bin')
    destino = IMGS / f"{cuando.strftime('%H%M%S')}_{quien}_{d.get('type')}.{ext}"
    with urllib.request.urlopen(url, timeout=180) as resp:
        destino.write_bytes(resp.read())
    print('bajado', destino.name, destino.stat().st_size, 'bytes')
