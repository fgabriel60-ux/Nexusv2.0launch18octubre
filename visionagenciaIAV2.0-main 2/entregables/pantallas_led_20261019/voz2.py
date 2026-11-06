"""Voz del spot de pantallas LED (30 s), voz por defecto de Fish Audio."""
import json, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TEXTO = ('(excited)(confident) ¿Sigues gastando en lonas que nadie ve? Es momento de que tu negocio brille, literalmente. '
         '(excited) Las pantallas LED no son un lujo, son la herramienta más potente para atraer clientes hoy mismo. '
         'Ya sea para tu bar, restaurante o incluso tu iglesia, tenemos la tecnología que se adapta a tu presupuesto. '
         '(excited) Contamos con equipos de importación directa y manufactura de alta calidad. '
         'Y lo mejor: al instalar con nosotros, ¡te incluimos tus primeros videos publicitarios gratis! '
         '(excited)(confident) No te quedes atrás. Haz clic en el botón de abajo y cotiza tu instalación hoy mismo.')
env = {}
for l in Path('/workspaces/Nexusv2.0launch18octubre/.env').read_text().splitlines():
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': TEXTO, 'format': 'mp3'}).encode(),
                             headers={'Authorization': 'Bearer ' + env['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's1'})
mp3 = AQUI / 'voz_led_v2.mp3'
mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
print(subprocess.run([FF, '-i', str(mp3)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0])
