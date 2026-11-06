"""Pone voz en off (Fish Audio, voz clonada de Jesús) a los 3 videos de Rar~Amore."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = 'd05ec13b5ba84b848060b6f2cfa8464b'  # Jesus Rar Amore natural
GUIONES = {  # guion de Meta AI (13 oct): enfoque positivo, sin preguntas de dolor ni promesas
    'A_Estudio': 'Mantener tu movilidad y vitalidad todos los días sí es posible. Rar Amore, cápsulas con colágeno, '
                 'magnesio, calcio y vitamina D. Haz tu pedido por WhatsApp.',
    'B_LuzCalida': 'Nutrición diaria para tus músculos y articulaciones. Rar Amore apoya tu bienestar con colágeno y '
                   'extractos naturales. Promoción por tiempo limitado, pide por WhatsApp.',
    'C_Naturaleza': 'Colágeno, calcio, vitamina D y semilla de uva, en una sola fórmula. Rar Amore favorece tu movilidad. '
                    'Ordena hoy por WhatsApp, con envío a domicilio.',
}

for nombre, texto in GUIONES.items():
    voz = AQUI / 'final' / f'voz_{nombre}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                          'Content-Type': 'application/json', 'model': 's1'})
    voz.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    video = AQUI / 'final' / f'RarAmore_{nombre}.mp4'
    salida = AQUI / 'final' / f'RarAmore_{nombre}_voz_meta.mp4'
    # voz al frente, audio ambiente del clip al 20 %; si la voz es más larga, se congela el último cuadro
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(video), '-i', str(voz), '-filter_complex',
                    '[0:v]tpad=stop_mode=clone:stop_duration=6[v];'
                    '[0:a]volume=0.2,apad[amb];[1:a]adelay=250|250[vz];'
                    '[amb][vz]amix=inputs=2:duration=shortest:normalize=0[a]',
                    '-map', '[v]', '-map', '[a]', '-shortest', '-c:v', 'libx264', '-crf', '20', '-preset', 'slow',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(salida)], check=True)
    print(salida.name)
