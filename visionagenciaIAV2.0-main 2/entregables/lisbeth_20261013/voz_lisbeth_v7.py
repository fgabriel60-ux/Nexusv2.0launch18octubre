"""Lisbeth v7: clona su voz real (sus 2 notas de WhatsApp) en Fish y la regenera con más energía (speed 1.1) + masterizado de locutor, como el de Omar v4."""
import json, subprocess, urllib.request, uuid
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
MUESTRA_TEXTO = ('Hola, mi nombre es Lisbeth. Aquí tenemos terrenos desde 300 metros cuadrados con vista espectacular hacia las montañas, a 20 minutos de la playa, '
                 'con documentos en regla. Te invito a que lo conozcas. Es un lugar hermoso. Tu familia se lo merece. No compres promesa. Información por WhatsApp. '
                 'Hola, mi nombre es Lisbeth. Aquí tenemos terrenos desde 300 metros cuadrados, con vista espectacular hacia las montañas, a 20 minutos de la playa. '
                 'Cuenta con documentos en regla, te invito a que lo conozcas. Es un lugar hermoso, tu familia se lo merece. No compres promesa, información por WhatsApp.')
TEXTO = ('¡Hola! Mi nombre es Lisbeth. Aquí tenemos terrenos desde trescientos metros cuadrados, con vista espectacular hacia las montañas, '
         'a veinte minutos de la playa. Cuentan con documentos en regla. ¡Te invito a que lo conozcas! Es un lugar hermoso, tu familia se lo merece. '
         '¡No compres promesas! Escríbeme por WhatsApp.')
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
ID = AQUI / 'voz_real' / 'voz_id_fish.txt'


def crea_voz():
    if ID.exists(): return ID.read_text().strip()
    wav = AQUI / 'voz_real' / 'muestra.mp3'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'voz_real' / 'LISBETH_1.ogg'), '-i', str(AQUI / 'voz_real' / 'LISBETH_2.ogg'),
                    '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1', '-ac', '1', '-ar', '44100', str(wav)], check=True)
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Lisbeth Inmueble (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private'), ('texts', MUESTRA_TEXTO)]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + wav.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; ID.write_text(i); return i


vid = crea_voz(); print('voz', vid)
mp3 = AQUI / 'voz_real' / 'LISBETH_punch.mp3'
r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                           data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': vid, 'prosody': {'speed': 1.1, 'volume': 3}, 'temperature': 0.8, 'top_p': 0.8}).encode(),
                           headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
wav = AQUI / 'voz_real' / 'LISBETH_punch.wav'
subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', f'{CADENA},adelay=300|300,apad=pad_dur=0.5', '-ar', '48000', '-ac', '2', str(wav)], check=True)
print(subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0])
