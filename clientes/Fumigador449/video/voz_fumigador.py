"""Fumigaciones Chávez AGS (Héctor Chávez): clona SU voz (su speech de WhatsApp del 24 oct) en Fish y le dice el guion mejorado."""
import json, subprocess, urllib.request, uuid
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
SPEECH = AQUI.parent / 'whatsapp' / '1024_113459_video.mp4'
MUESTRA_TEXTO = ('Hola, en Fumigaciones Chávez nos dedicamos a que tú tengas la tranquilidad que mereces, que lleves una vida tranquila y que no tengas esa molesta '
                 'plaga que invade en tu hogar. Fumigamos casa habitación, locales de comida, camiones y todo tipo de lugar donde quieras que fumiguemos. '
                 'Tu tranquilidad es nuestra misión. Puedes confiar en que nosotros somos la mejor solución. Manda mensaje de WhatsApp.')
TEXTO = ('¿Chinches, cucarachas o alacranes en tu casa? Soy Héctor Chávez, de Fumigaciones Chávez, aquí en Aguascalientes. '
         'Fumigamos casas, locales de comida y camiones, y vamos cuando lo necesitas, hasta en domingo. '
         'Este es mi equipo, trabajando de verdad. Tu tranquilidad es nuestra misión. '
         'Mándame mensaje por WhatsApp y te digo cuánto cuesta tu servicio.')
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
ID = AQUI / 'voz' / 'voz_id_fish.txt'


def crea_voz():
    if ID.exists(): return ID.read_text().strip()
    mp3 = AQUI / 'voz' / 'muestra.mp3'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(SPEECH), '-vn', '-ac', '1', '-ar', '44100', str(mp3)], check=True)
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Hector Chavez fumigaciones (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private'), ('texts', MUESTRA_TEXTO)]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + mp3.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; ID.write_text(i); return i


vid = crea_voz(); print('voz', vid)
mp3 = AQUI / 'voz' / 'hector_guion.mp3'
r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                           data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': vid, 'prosody': {'speed': 1.08, 'volume': 2}, 'temperature': 0.65, 'top_p': 0.8}).encode(),
                           headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
wav = AQUI / 'voz' / 'hector_guion.wav'
subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', CADENA, '-ar', '48000', '-ac', '2', str(wav)], check=True)
print(subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0])
