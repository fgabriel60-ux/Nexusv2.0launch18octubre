"""Baja la media reenviada al chat propio (archivos de Servilin) y transcribe los audios."""
import json, os, time, urllib.error, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
import av, numpy as np

AQUI = Path(__file__).resolve().parent / 'reenviados'
MX = timezone(timedelta(hours=-7))
TOKEN = os.environ['WAAPI_TOKEN']
INSTANCIA = os.environ.get('WAAPI_INSTANCE', '105840')
EXT = {'image': 'jpg', 'video': 'mp4', 'audio': 'ogg', 'ptt': 'ogg', 'document': 'bin'}


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


def decodificar(ruta):
    c = av.open(str(ruta))
    rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    partes = [x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]
    return np.concatenate(partes).astype(np.float32) / 32768


res = json.loads((AQUI / 'crudo.json').read_text())
audios, indice = [], []
for n, it in enumerate(res['data']['data']):
    d = it['message']['_data']
    tipo = d.get('type')
    if tipo not in EXT or d['t'] < datetime(2026, 10, 12, 21, 0).timestamp():
        continue
    cuando = datetime.fromtimestamp(d['t'], MX)
    ext = (d.get('filename') or '').rsplit('.', 1)[-1] if tipo == 'document' and d.get('filename') else EXT[tipo]
    destino = AQUI / f"{n:03d}_{tipo}.{ext}"
    if not destino.exists():
        r = accion('download-media', {'messageId': d['id']['_serialized']})
        url = ((r.get('data') or {}).get('data') or {}).get('media', {}).get('url')
        if not url:
            print('sin media:', destino.name); continue
        with urllib.request.urlopen(url, timeout=300) as resp:
            destino.write_bytes(resp.read())
        print('bajado', destino.name, flush=True)
    indice.append(f"{destino.name}\t{'reenviado' if d.get('isForwarded') else 'propio'}\t{(d.get('caption') or '').replace(chr(10), ' / ')}")
    if tipo in ('audio', 'ptt'):
        audios.append(destino)
(AQUI / 'INDICE.txt').write_text('\n'.join(indice))

from faster_whisper import WhisperModel
modelo = WhisperModel('small', device='cpu', compute_type='int8')
salida = []
for ruta in audios:
    segs, _ = modelo.transcribe(decodificar(ruta), language='es', vad_filter=True)
    salida.append(f"{ruta.name}\n    {' '.join(s.text.strip() for s in segs)}")
    print(salida[-1], flush=True)
(AQUI / 'AUDIOS_TRANSCRITOS.txt').write_text('\n\n'.join(salida))
