"""Prueba de `wavespeed-ai/minimax-h3/video-edit` ($0.25) como alternativa a Genjutsu.

A diferencia de lucy-restyle, este acepta hasta 9 imágenes de referencia (se citan en el prompt como <Picture 1>…),
que es lo que hace Genjutsu. Su tope es 15 s, así que el tramo A de 18 s se recorta antes de mandarlo.
`generate_audio` se apaga: si no, inventa audio encima.

El video y las imágenes van como data URI en base64, que ya se comprobó que WaveSpeed acepta.
Uso: python3 prueba_minimax_edit.py
"""
import base64, json, subprocess, time, urllib.error, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV = Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env')
API = 'https://api.wavespeed.ai/api/v3'
MODELO = 'wavespeed-ai/minimax-h3/video-edit'
ENTRADA = AQUI / 'TRAMO_A' / '00_VIDEO_TRAMO_A.mp4'
RECORTE = AQUI / '_tramoA_15s.mp4'
SALIDA = AQUI / 'PRUEBA_MINIMAX_EDIT_TRAMO_A.mp4'
IMAGENES = ['01_rostro_hueco.png', '02_closeup_espacio.png', '03_anestesia.png',
            '04_sticker_revela.png', '05_preparacion_fresa.png']

PROMPT = (
    "Edit this rough grey 3D dental animation into a premium photoreal implant explainer, keeping its exact camera "
    "motion, timing and composition. Match the look of the reference images: <Picture 1> is the woman with one "
    "missing upper front tooth, <Picture 2> the macro of her mouth, <Picture 3> the anaesthesia step, <Picture 4> the "
    "face peeling away like a sticker to reveal the upper jaw section, <Picture 5> the drill preparing the bone. "
    "Near-black background with deep teal and warm orange bokeh, bright glossy white enamel, translucent pink gums "
    "with a warm luminous edge, porous cream bone with a glowing orange cut edge, satin titanium, soft teal rim "
    "light, shallow depth of field. Keep the same woman and the same single gap. Anatomically clean, not gore. "
    "No text, no logos, no watermark."
)


def clave():
    for l in ENV.read_text().splitlines():
        if l.startswith('WAVESPEED_API_KEY='):
            return l.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


CAB = {'Authorization': 'Bearer ' + clave(), 'Content-Type': 'application/json'}


def uri(p, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(Path(p).read_bytes()).decode())


def esperar(job):
    for i in range(400):
        req = urllib.request.Request(f'{API}/predictions/{job}/result', headers=CAB)
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r).get('data') or {}
        if i % 6 == 0:
            print('  estado:', d.get('status'), flush=True)
        if d.get('status') == 'completed':
            return d['outputs'][0]
        if d.get('status') == 'failed':
            raise RuntimeError('falló: ' + str(d.get('error')))
        time.sleep(4)
    raise TimeoutError('sin respuesta')


if __name__ == '__main__':
    if not RECORTE.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', '15', '-i', str(ENTRADA),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-an', str(RECORTE)], check=True)
    print('entrada recortada a 15 s:', round(RECORTE.stat().st_size / 1e6, 2), 'MB')
    cuerpo = {
        'prompt': PROMPT,
        'video': uri(RECORTE, 'video/mp4'),
        'reference_images': [uri(AQUI / 'IMAGENES' / n, 'image/png') for n in IMAGENES],
        'resolution': '768p', 'generate_audio': False, 'duration': 15,
    }
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(API + '/' + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
        with urllib.request.urlopen(req, timeout=300) as r:
            job = json.load(r)['data']['id']
    except urllib.error.HTTPError as e:
        print('RECHAZADO:', e.code, e.read().decode()[:500]); raise SystemExit(1)
    print('job', job, flush=True)
    (AQUI / 'minimax_edit_job.json').write_text(json.dumps({'id': job, 'model': MODELO, 'prompt': PROMPT}, indent=2))
    url = esperar(job)
    with urllib.request.urlopen(url, timeout=600) as r:
        SALIDA.write_bytes(r.read())
    print('listo:', SALIDA.name, '|', round(time.monotonic() - t0), 'segundos |',
          round(SALIDA.stat().st_size / 1e6, 2), 'MB')
