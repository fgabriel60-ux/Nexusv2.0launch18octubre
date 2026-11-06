"""Saca los mensajes recientes del chat 360 Salud en formato legible."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from leer_chat import accion

AQUI = Path(__file__).resolve().parent
CHAT = '31606932787332@lid'
MX = timezone(timedelta(hours=-7))  # Nogales/Sonora

if not (AQUI / 'crudo_mensajes.json').exists():
    res = accion('fetch-messages', {'chatId': CHAT, 'limit': 60})
    (AQUI / 'crudo_mensajes.json').write_text(json.dumps(res, ensure_ascii=False, indent=2))
res = json.loads((AQUI / 'crudo_mensajes.json').read_text())

lineas = []
for item in res['data']['data']:
    d = item['message']['_data']
    t = d.get('t') or 0
    cuando = datetime.fromtimestamp(t, MX).strftime('%d %b %H:%M')
    quien = 'CARLOS' if (d.get('id') or {}).get('fromMe') else 'JESUS'
    tipo = d.get('type', '?')
    cuerpo = (d.get('body') or '').strip()
    if tipo in ('ptt', 'audio'):
        cuerpo = f'[AUDIO {d.get("duration", "?")}s]  media={"si" if item.get("media") else "no"}'
    elif tipo == 'image':
        cuerpo = f'[IMAGEN] {cuerpo}'
    elif tipo == 'document':
        cuerpo = f'[DOC {d.get("filename", "")}] {cuerpo}'
    elif tipo == 'video':
        cuerpo = f'[VIDEO] {cuerpo}'
    elif tipo != 'chat':
        cuerpo = f'[{tipo.upper()}] {cuerpo}'
    lineas.append(f'{cuando}  {quien:6}  {cuerpo}')

texto = '\n'.join(lineas)
(AQUI / 'HILO_360SALUD.txt').write_text(texto)
print(texto)
