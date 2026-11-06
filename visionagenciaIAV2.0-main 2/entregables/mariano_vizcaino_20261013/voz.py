"""Voz de Mariano (Fish Audio, voz clonada) para el reel de Vizcaíno Residencial; guarda mp3 y wav 48 kHz para MiniMax H3."""
import json, os, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = '574f8646b8e54d1dab2bb8a6dd1aa189'  # Mariano Herrera (Catania)
GUION = {
    'T2': '¿Buscas casa en Rosarito? Aterricé en Vizcaíno Residencial para enseñártela.',
    'T3': 'Privada, acceso controlado y cancha de pádel. Bugambilia desde dos punto cuarenta y cinco millones, Benjamina dos punto ochenta y cinco, y Salvia tres punto cinco.',
    'T4': 'Un nuevo modelo de vivienda para cada estilo de vida. Mándame mensaje y agendamos tu visita.',
}
env = {}
for l in Path('/workspaces/Nexusv2.0launch18octubre/.env').read_text().splitlines():
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
(AQUI / 'voz').mkdir(exist_ok=True)
for nombre, texto in GUION.items():
    mp3 = AQUI / 'voz' / f'{nombre}.mp3'
    req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                 data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                                 headers={'Authorization': 'Bearer ' + env['FISH_API_KEY'],
                                          'Content-Type': 'application/json', 'model': 's1'})
    mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    wav = mp3.with_suffix('.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'adelay=300|300,apad=pad_dur=0.6',
                    '-ar', '48000', '-ac', '2', str(wav)], check=True)
    out = subprocess.run([FF, '-i', str(wav)], capture_output=True, text=True).stderr
    print(nombre, out.split('Duration: ')[1].split(',')[0])
