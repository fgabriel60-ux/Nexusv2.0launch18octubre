"""Voz clonada de Marcos (Fish) para el video estilo 'la chica de la Afore'; wav 48 kHz para MiniMax H3."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '2c1384bd99bd44b7a5a71e37ca871782'  # Marcos Ortega (voz real)
GUION = {
    'T1': '¿Sabías que podrías recibir hasta treinta y cinco mil ciento noventa y dos pesos de tu Afore, por un derecho que '
          'te corresponde?',
    'T2': 'En Soluciones Previsionales Ortega gestionamos ayuda por desempleo, negativas de pensión, corrección de RFC, '
          'semanas cotizadas y crédito Mejoravit.',
    'T3': 'Sin anticipos: pagas cuando recibes tu dinero. No estás solo. Escríbenos hoy por WhatsApp.',
}
(AQUI / 'voz').mkdir(exist_ok=True)
for nombre, texto in GUION.items():
    mp3 = AQUI / 'voz' / f'{nombre}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                          'Content-Type': 'application/json', 'model': 's1'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    wav = mp3.with_suffix('.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'adelay=300|300,apad=pad_dur=0.6',
                    '-ar', '48000', '-ac', '2', str(wav)], check=True)
    out = subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr
    print(nombre, out.split('Duration: ')[1].split(',')[0])
