"""Baja audios e imagenes del chat de Victor Hugo Servilin y transcribe los audios con faster-whisper."""
import json, os, time, urllib.error, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MEDIA = AQUI / 'media'
MEDIA.mkdir(exist_ok=True)
MX = timezone(timedelta(hours=-7))
TOKEN = os.environ['WAAPI_TOKEN']
INSTANCIA = os.environ.get('WAAPI_INSTANCE', '105840')


def accion(nombre, payload):
    req = urllib.request.Request(
        f'https://waapi.app/api/v1/instances/{INSTANCIA}/client/action/{nombre}',
        data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    for intento in range(8):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                time.sleep(1.5)
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get('Retry-After') or 0) or 5 * 2 ** intento)
    raise RuntimeError('WaAPI sigue limitando peticiones (429)')


res = json.loads((AQUI / 'crudo_mensajes.json').read_text())
audios = []
for it in res['data']['data']:
    d = it['message']['_data']
    tipo = d.get('type')
    if tipo not in ('ptt', 'audio', 'image'):
        continue
    quien = 'CARLOS' if d['id'].get('fromMe') else 'VICTOR'
    cuando = datetime.fromtimestamp(d['t'], MX)
    ext = 'jpg' if tipo == 'image' else 'ogg'
    destino = MEDIA / f"{cuando.strftime('%m%d_%H%M%S')}_{quien}_{tipo}.{ext}"
    if not destino.exists():
        r = accion('download-media', {'messageId': d['id']['_serialized']})
        url = ((r.get('data') or {}).get('data') or {}).get('media', {}).get('url')
        if not url:
            print('sin media:', destino.name); continue
        with urllib.request.urlopen(url, timeout=120) as resp:
            destino.write_bytes(resp.read())
        print('bajado', destino.name)
    if tipo != 'image':
        audios.append((cuando, quien, destino))

from faster_whisper import WhisperModel
modelo = WhisperModel('small', device='cpu', compute_type='int8')
salida = []
for cuando, quien, ruta in sorted(audios):
    segs, _ = modelo.transcribe(str(ruta), language='es', vad_filter=True)
    texto = ' '.join(s.text.strip() for s in segs).strip()
    linea = f"{cuando.strftime('%d %b %H:%M')}  {quien}\n    {texto}"
    print(linea, flush=True)
    salida.append(linea)
(AQUI / 'AUDIOS_TRANSCRITOS.txt').write_text('\n\n'.join(salida))
