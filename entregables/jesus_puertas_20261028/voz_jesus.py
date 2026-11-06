"""Clona la voz de Jesús (notas de voz limpias de WhatsApp) en Fish y genera las 5 frases del guion de su video de carpintería."""
import json, subprocess, urllib.request, uuid
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
NOTAS = ['183517', '184226', '183118', '183910', '184306']
FRASES = {
    'J1': '¿Buscas puertas o cocinas en Mazatlán? Soy Jesús, carpintero.',
    'J2': 'Puertas de parota y cocinas en melamina, hechas a tu medida.',
    'J3': 'Una puerta económica, con chapa, bisagras e instalación, en oferta: tres mil quinientos pesos.',
    'J4': 'Y tu cocina en melamina: ocho mil pesos el metro lineal, con gabinete alto y bajo.',
    'J5': 'Escríbeme por WhatsApp y te cotizo.',
}
ID = AQUI / 'voz' / 'voz_id.txt'; (AQUI / 'voz').mkdir(exist_ok=True)


def crea_voz():
    if ID.exists(): return ID.read_text().strip()
    mp3 = AQUI / 'voz' / 'muestra.mp3'
    ent = []
    for n in NOTAS: ent += ['-i', str(AQUI / 'wav' / f'20261027_{n}_ptt.wav')]
    subprocess.run([FF, '-v', 'error', '-y', *ent, '-filter_complex', ''.join(f'[{i}:a]' for i in range(len(NOTAS))) + f'concat=n={len(NOTAS)}:v=0:a=1',
                    '-ac', '1', '-ar', '44100', str(mp3)], check=True)
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Jesús carpintero Mazatlán (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private')]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + mp3.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; ID.write_text(i); return i


vid = crea_voz(); print('voz', vid)
for k, t in FRASES.items():
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': t, 'format': 'wav', 'reference_id': vid}).encode(),
                               headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
    (AQUI / 'voz' / f'{k}.wav').write_bytes(urllib.request.urlopen(r, timeout=300).read()); print(k, 'ok')
