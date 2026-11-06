"""Voz de Omar v4: misma voz clonada (Fish s2-pro) con más energía y confianza: habla ~10 % más rápido,
y masterización con compresión, presencia en medios y volumen parejo (punch de locutor)."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '8b783cb40a734c88a9bf801fca6114fa'
GUION = {
    'O1': '¿Conoces el multinivel? ¡Con Red Natura, tu libertad financiera puede empezar hoy! Estamos en cuatro países '
          'y tenemos más de cincuenta productos para toda la familia.',
    'O2': 'Control de peso, detox y nutrición. ¡Y tienes seis formas de generar ingresos! Escríbeme por WhatsApp y te '
          'explico cómo empezar.',
}
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
for nombre, texto in GUION.items():
    mp3 = AQUI / 'voz' / f'{nombre}_v4.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ,
                                                  'prosody': {'speed': 1.1, 'volume': 3}, 'temperature': 0.8, 'top_p': 0.8}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                          'Content-Type': 'application/json', 'model': 's2-pro'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    wav = AQUI / 'voz' / f'T{nombre}_v4.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', f'{CADENA},adelay=300|300,apad=pad_dur=0.5',
                    '-ar', '48000', '-ac', '2', str(wav)], check=True)
    out = subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr
    print(nombre, out.split('Duration: ')[1].split(',')[0])
