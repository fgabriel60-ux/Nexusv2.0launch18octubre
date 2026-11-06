"""Voz de Carlos con Fish s2-pro (modelo más nuevo) para su reel de Visión Agencia; wav 48 kHz para MiniMax H3."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '1f679152b5d64c09a8e8eeecd3eb5424'  # Carlos real · voz aislada (limpia)
GUION = {
    'C1': 'Conseguir mensajes ya no es un problema. Ni hacer videos de la máxima calidad.',
    'C2': 'Y Facebook nos confirma que la campaña será excepcional... antes de sacarla.',
    'C3': 'Sí se logra con inteligencia artificial... pero casi nadie está usando la correcta.',
    'C4': 'Busco clientes que ya hayan corrido publicidad antes. Con la demanda que hay, no puedo detenerme a arreglar las '
          'fallas de Facebook. Mándame mensaje y agendemos una llamada. Solo acepto cinco clientes por semana.',
}
for nombre, texto in [(k, v) for k, v in GUION.items() if k == 'C4']:
    mp3 = AQUI / 'voz' / f'{nombre}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                                 headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                          'Content-Type': 'application/json', 'model': 's2-pro'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    wav = AQUI / 'voz' / f'T{nombre}.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'adelay=250|250,apad=pad_dur=0.5',
                    '-ar', '48000', '-ac', '2', str(wav)], check=True)
    out = subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr
    print(nombre, out.split('Duration: ')[1].split(',')[0])
