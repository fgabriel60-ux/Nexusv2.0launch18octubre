"""Baja y transcribe los audios nuevos (tarde del 17 sep) del chat 360 Salud."""
import json, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from leer_chat import accion

AQUI = Path(__file__).resolve().parent
AUDIOS = AQUI / 'audios'
AUDIOS.mkdir(exist_ok=True)
MX = timezone(timedelta(hours=-7))

res = json.loads((AQUI / 'crudo_mensajes_nuevos.json').read_text())
pendientes = []
for it in res['data']['data']:
    d = it['message']['_data']
    if d.get('type') not in ('ptt', 'audio'):
        continue
    mid = d['id']['_serialized']
    quien = 'CARLOS' if d['id'].get('fromMe') else 'JESUS'
    cuando = datetime.fromtimestamp(d['t'], MX)
    nombre = f"{cuando.strftime('%H%M%S')}_{quien}_{d.get('duration','?')}s.ogg"
    destino = AUDIOS / nombre
    if not destino.exists():
        r = accion('download-media', {'messageId': mid})
        url = ((r.get('data') or {}).get('data') or {}).get('media', {}).get('url')
        if not url:
            print('sin media:', nombre); continue
        with urllib.request.urlopen(url, timeout=120) as resp:
            destino.write_bytes(resp.read())
        print('bajado', nombre, destino.stat().st_size, 'bytes', flush=True)
    pendientes.append((cuando, quien, destino))

print(f'\n{len(pendientes)} audios, transcribiendo...\n', flush=True)
from faster_whisper import WhisperModel
modelo = WhisperModel('medium', device='cpu', compute_type='int8')

salida = []
for cuando, quien, ruta in sorted(pendientes):
    segs, _ = modelo.transcribe(str(ruta), language='es', vad_filter=True)
    texto = ' '.join(s.text.strip() for s in segs).strip()
    linea = f"{cuando.strftime('%d %b %H:%M')}  {quien}  (audio {ruta.stem.split('_')[-1]})\n    {texto}"
    print(linea, flush=True)
    salida.append(linea)

(AQUI / 'AUDIOS_TARDE_TRANSCRITOS.txt').write_text('\n\n'.join(salida))
print('\n-> AUDIOS_TARDE_TRANSCRITOS.txt')
