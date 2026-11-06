"""Voz de Omar con el modelo Fish s1 (el que sonaba como él) para las tomas caminando."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg
AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
GUION = {
    'TO1': '¿Conoces el multinivel? Con Red Natura, tu libertad financiera puede empezar hoy. Estamos en cuatro países '
           'y tenemos más de cincuenta productos para toda la familia.',
    'TO2': 'Control de peso, detox y nutrición. Y tienes seis formas de generar ingresos. Escríbeme por WhatsApp y te '
           'explico cómo empezar.',
}
for n, texto in GUION.items():
    mp3 = AQUI / 'voz' / f'{n}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': '8b783cb40a734c88a9bf801fca6114fa'}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's1'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'adelay=300|300,apad=pad_dur=0.6', '-ar', '48000', '-ac', '2',
                    str(mp3.with_suffix('.wav'))], check=True)
    print(n)
