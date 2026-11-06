"""Voz de Carlos (Fish s2-pro) para el storytelling de Mariano."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg
AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
GUION = {
    'S1': 'Hace tres meses lancé la primera campaña de Mariano. Funcionó... y de repente, dejó de funcionar.',
    'S2': 'Tres meses de vacas flacas. Probamos anuncios, videos, textos... y nada. En bienes raíces, cada mensaje cuesta.',
    'S3': 'Pero no nos rendimos. Nos obsesionamos con entender qué hizo excepcional esa primera campaña: cada número, cada palabra, cada video.',
    'S4': 'Hasta que encontramos la fórmula. La aplicamos tal cual... y al día siguiente: dos mensajes, y una cita para ver un departamento el domingo.',
    'S5': 'Hoy Mariano me escribe: estoy realmente sorprendido por todo el avance en tan solo tres meses.',
    'S6': 'Si llevas meses adivinando con tu publicidad, mándame mensaje. En una llamada te aplico la fórmula.',
}
for n, texto in GUION.items():
    mp3 = AQUI / 'voz' / f'{n}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': '1f679152b5d64c09a8e8eeecd3eb5424'}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's2-pro'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'adelay=250|250,apad=pad_dur=0.4', '-ar', '48000', '-ac', '2',
                    str(AQUI / 'voz' / f'T{n}.wav')], check=True)
    print(n)
