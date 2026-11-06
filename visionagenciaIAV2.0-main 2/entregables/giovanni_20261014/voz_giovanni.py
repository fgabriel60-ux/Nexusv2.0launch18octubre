"""Clona la voz de Giovanni Pulido (audio de su video del día del abogado) en Fish y genera las 2 partes del guion."""
import json, os, subprocess, urllib.request, uuid
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
MUESTRA_TEXTO = ('Hoy 12 de julio celebramos a quienes ejercen una de las profesiones más nobles, la abogacía. Ser abogado es mucho más que '
                 'conocer las leyes, es defender la justicia, proteger los derechos de las personas y transformar vidas en cada juicio, en cada '
                 'asesoría y en cada decisión. Hoy reconozco el esfuerzo, la dedicación y la integridad de todas las abogadas y abogados que '
                 'trabajan día con día para hacer valer la ley y defender la dignidad humana. Reciban mi más sincero reconocimiento, feliz día del abogado.')
PARTES = {
    'G1': 'Su tranquilidad merece un divorcio sin vueltas. Soy el licenciado Giovanni Pulido, abogado en Los Cabos. Llevo más de quince años '
          'y más de noventa divorcios resueltos, con total discreción.',
    'G2': 'Si ambos están de acuerdo, el divorcio voluntario es desde dieciocho mil pesos. Precio claro, sin sorpresas. Tú cuidas lo que más '
          'importa, yo me encargo del trámite. Escríbeme por WhatsApp.',
}
ID = AQUI / 'voz' / 'voz_id.txt'


def crea_voz():
    if ID.exists(): return ID.read_text().strip()
    mp3 = AQUI / 'voz' / 'muestra.mp3'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'refs' / 'dia_abogado.mp4'), '-vn', '-ac', '1', '-ar', '44100', str(mp3)], check=True)
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Giovanni Pulido abogado (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private'), ('texts', MUESTRA_TEXTO)]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + mp3.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; ID.write_text(i); return i


vid = crea_voz(); print('voz', vid)
for k, t in PARTES.items():
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': t, 'format': 'wav', 'reference_id': vid}).encode(),
                               headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
    (AQUI / 'voz' / f'{k}.wav').write_bytes(urllib.request.urlopen(r, timeout=300).read()); print(k, 'ok')
