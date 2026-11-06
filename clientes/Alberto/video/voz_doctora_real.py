"""Voz de la Dra. Ángeles CLONADA de su video real (grabado por Carlos el 27 oct, doctora_real/voz.wav, sin el «Aquí está» inicial) para el reel de implantes.
Cada frase se genera 4 veces (Fish s2-pro y s1) y se queda la que Whisper transcribe igual al guion. Sale voz/ref_S1..S5 (.mp3 44.1 kHz y .wav 16 kHz guía de labios).
Las voces genéricas anteriores quedaron en voz/generica_bak/."""
import difflib, json, os, re, subprocess, urllib.request, uuid
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
AQUI = Path(__file__).resolve().parent; V = AQUI / 'voz'
K = os.environ['FISH_API_KEY']
GUION = {"S1": "¿Te falta un diente? No lo dejes así.",
         "S2": "Cuando pierdes una pieza, el hueso de esa zona puede irse perdiendo con el tiempo, y los dientes de al lado se pueden mover.",
         "S3": "La solución es un implante dental: una raíz de titanio que se coloca dentro del hueso, como una raíz nueva.",
         "S4": "Se coloca con anestesia local, y la corona va aparte.",
         "S5": "Aquí en Víniers Dental, tu implante va desde doce mil quinientos pesos. Escríbenos por WhatsApp y agenda tu valoración."}
ff = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)


def voz_id():
    f = AQUI / 'doctora_real' / 'voz_fish_id.txt'
    if f.exists(): return f.read_text().strip()
    mp3 = AQUI / 'doctora_real' / 'muestra_clon.mp3'
    ff('-ss', '1.6', '-i', str(AQUI / 'doctora_real' / 'voz.wav'), '-af', 'highpass=f=80,afftdn=nf=-25,loudnorm=I=-16', '-ac', '1', '-ar', '44100', str(mp3))
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Dra. Ángeles Veneers Dental (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private')]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + mp3.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; f.write_text(i); return i


vid = voz_id(); print('voz', vid)
m = WhisperModel('medium', device='cpu', compute_type='int8')
norm = lambda t: re.sub(r'[^a-záéíóúñ0-9 ]', '', t.lower().replace('víniers', 'veneers').replace('doce mil quinientos', '12500').replace('12,500', '12500').replace('12 500', '12500'))
def tr(f):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    s, _ = m.transcribe(np.frombuffer(b, np.int16).astype(np.float32) / 32768, language='es', initial_prompt='Veneers Dental, implante, titanio, WhatsApp.')
    return ' '.join(x.text.strip() for x in s)
for n, t in GUION.items():
    mejor = (-1, None, '')
    for j, modelo in enumerate(['s2-pro', 's1', 's2-pro', 's1']):
        f = V / f'dra_{n}_{j}.mp3'
        if not f.exists():
            r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': t + (' ' if j > 1 else ''), 'format': 'mp3', 'sample_rate': 44100, 'reference_id': vid}).encode(),
                                       headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json', 'model': modelo})
            f.write_bytes(urllib.request.urlopen(r, timeout=300).read())
        tx = tr(f); sc = difflib.SequenceMatcher(None, norm(tx), norm(t)).ratio()
        if sc > mejor[0]: mejor = (sc, f, tx)
    ff('-i', str(mejor[1]), '-af', 'loudnorm=I=-16:TP=-1.5', '-ar', '44100', str(V / f'ref_{n}.mp3'))
    ff('-i', str(mejor[1]), '-ac', '1', '-ar', '16000', '-sample_fmt', 's16', str(V / f'ref_{n}.wav'))
    ff('-i', str(mejor[1]), '-ac', '1', '-ar', '44100', str(V / f'ref_{n}_44.wav'))
    print(n, f'{mejor[0]:.2f}', mejor[2], flush=True)
