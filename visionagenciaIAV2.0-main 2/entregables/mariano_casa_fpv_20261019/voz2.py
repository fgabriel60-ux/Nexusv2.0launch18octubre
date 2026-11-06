"""Voz de Mariano (Fish Audio, voz clonada) para el recorrido de casa estilo four horsemen."""
import json, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '574f8646b8e54d1dab2bb8a6dd1aa189'  # Mariano Herrera (Catania)
TEXTO = ('¡Vamos a ver, vamos a ver! Les enseño la Benjamina, desde dos punto ocho millones. Entramos a una sala amplia y luminosa, cocina equipada, '
         'comedor para toda la familia y un patio privado. Subimos a las recámaras, con mucha luz natural, y terminamos en la terraza con vista al mar. '
         'Se acepta Infonavit, crédito hipotecario y contado. Mándame mensaje y agendamos tu visita.')
env = {}
for l in Path('/workspaces/Nexusv2.0launch18octubre/.env').read_text().splitlines():
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                             headers={'Authorization': 'Bearer ' + env['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's1'})
mp3 = AQUI / 'voz' / 'guion2.mp3'
mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
print(subprocess.run([FF, '-i', str(mp3)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0])
