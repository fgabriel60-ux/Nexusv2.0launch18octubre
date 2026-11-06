"""Voz de Uriel Chávez (Fish Audio, voz clonada) para «El costo del caos operativo»."""
import json, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '0984985214304200b262e31466d9cc3e'  # Uriel Chávez (voz real)
TEXTO = ('¿Sabes cuánto le cuesta a tu empresa que tú seas el único que sabe cómo se hacen las cosas? '
         'El costo oculto de no tener estructura es tu tiempo y tu libertad. '
         'Si cada duda te interrumpe y ninguna decisión se toma sin tu visto bueno, no tienes un negocio, tienes un autoempleo agotador. '
         'La falta de documentos claros mata la autonomía de tu equipo. '
         'Ayudo a dueños de negocios a crear sistemas de documentos que realmente se implementan. '
         'Para que tu empresa avance, incluso cuando tú no estás. '
         'Deja de ser el bombero de tu empresa. Haz clic aquí y agenda una sesión de diagnóstico hoy mismo.')
env = {}
for l in Path('/workspaces/Nexusv2.0launch18octubre/.env').read_text().splitlines():
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                             headers={'Authorization': 'Bearer ' + env['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's1'})
mp3 = AQUI / 'voz_uriel.mp3'
mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
print(subprocess.run([FF, '-i', str(mp3)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0])
