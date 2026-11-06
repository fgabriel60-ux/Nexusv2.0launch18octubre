"""Voz real de Omar (Fish, clonada de sus notas de voz) para las 2 tomas; wav 48 kHz para MiniMax H3."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '8b783cb40a734c88a9bf801fca6114fa'  # Omar Red Natura (voz real)
GUION = {
    'O1': '¿Conoces el multinivel? Con Red Natura, tu libertad financiera puede empezar hoy. Estamos en cuatro países '
          'y tenemos más de cincuenta productos para toda la familia.',
    'O2': 'Control de peso, detox y nutrición. Y tienes seis formas de generar ingresos. Escríbeme por WhatsApp y te '
          'explico cómo empezar.',
}
for nombre, texto in GUION.items():
    mp3 = AQUI / 'voz' / f'{nombre}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                          'Content-Type': 'application/json', 'model': 's2-pro'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    wav = AQUI / 'voz' / f'T{nombre}.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'adelay=300|300,apad=pad_dur=0.6',
                    '-ar', '48000', '-ac', '2', str(wav)], check=True)
    out = subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr
    print(nombre, out.split('Duration: ')[1].split(',')[0])
