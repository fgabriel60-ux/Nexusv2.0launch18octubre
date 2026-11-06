"""Comprime el render completo (Cycles CPU en Modal + voz) a tamaño WhatsApp compatible y se lo manda a Carlos.
Uso: python3 enviar_render_whatsapp.py"""
import base64, json, subprocess, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGEN = AQUI / 'IMPLANTE_DENTAL_PARA_ALBERTO.mp4'
DESTINO = AQUI / 'IMPLANTE_DENTAL_RENDER_CPU_WHATSAPP.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ORIGEN), '-vf', 'scale=720:1280', '-c:v', 'libx264', '-profile:v', 'baseline',
                '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-maxrate', '1800k', '-bufsize', '3600k', '-c:a', 'aac',
                '-b:a', '128k', '-ar', '44100', '-movflags', '+faststart', str(DESTINO)], check=True)
env = {}
for line in Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")
body = {'chatId': '5216312470486@c.us', 'mediaBase64': base64.b64encode(DESTINO.read_bytes()).decode(), 'mediaName': DESTINO.name,
        'asDocument': False, 'mediaCaption': '🤖 Claude · Implante: render completo 35 s con voz (Modal sin GPU, Cycles CPU)'}
req = urllib.request.Request('https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/send-media',
                             data=json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + env['WAAPI_TOKEN'], 'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=300) as r:
    estado = (json.load(r).get('data') or {}).get('status')
(AQUI / 'recibo_render_whatsapp.json').write_text(json.dumps({'archivo': DESTINO.name, 'status': estado}))
print('WhatsApp:', estado)
