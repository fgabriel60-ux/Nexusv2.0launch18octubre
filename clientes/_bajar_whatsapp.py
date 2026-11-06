"""Baja imágenes, videos y documentos de los chats de cada cliente a clientes/<Cliente>/whatsapp/{del_cliente,hechos_por_mi}."""
import json, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/360salud_pedido_jesus_20260917')
from leer_chat import accion

RAIZ = Path(__file__).resolve().parent
MX = timezone(timedelta(hours=-7))
MENSAJES = Path(sys.argv[1])
EXT = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'video/mp4': 'mp4', 'application/pdf': 'pdf'}
MAX_MB = 60

for cliente, items in json.loads(MENSAJES.read_text()).items():
    for it in items:
        d = it['message']['_data']
        if d.get('type') not in ('image', 'video', 'document'):
            continue
        mid = d['id']['_serialized']
        carpeta = RAIZ / cliente / 'whatsapp' / ('hechos_por_mi' if d['id'].get('fromMe') else 'del_cliente')
        carpeta.mkdir(parents=True, exist_ok=True)
        cuando = datetime.fromtimestamp(d['t'], MX).strftime('%Y%m%d_%H%M%S')
        if list(carpeta.glob(f'{cuando}_{d["type"]}.*')):
            continue
        for intento in range(4):
            r = accion('download-media', {'messageId': mid})
            media = ((r.get('data') or {}).get('data') or {}).get('media') or {}
            if media.get('url'):
                break
            time.sleep(8)
        else:
            print('sin media', cliente, cuando, d['type'], flush=True); time.sleep(6); continue
        ext = EXT.get(media.get('mimetype', '').split(';')[0], 'bin')
        try:
            with urllib.request.urlopen(media['url'], timeout=180) as resp:
                datos = resp.read(MAX_MB * 1024 * 1024 + 1)
            if len(datos) > MAX_MB * 1024 * 1024:
                print('muy grande, omitido', cliente, cuando, flush=True)
            else:
                (carpeta / f'{cuando}_{d["type"]}.{ext}').write_bytes(datos)
                print('ok', cliente, carpeta.name, cuando, d['type'], len(datos), flush=True)
        except Exception as e:
            print('error', cliente, cuando, e, flush=True)
        time.sleep(6)
