"""Voz Fish genérica femenina para los 4 videos de referencia de servicios. Sale voz/<toma>.mp3 (44.1k), <toma>_44.wav y <toma>.wav (16 kHz mono).
Uso: python3 voz_servicios_ref.py [C1 O2 ...]  (sin argumentos: todas)"""
import json, subprocess, sys, urllib.request
from pathlib import Path
import imageio_ffmpeg
sys.path.insert(0, str(Path(__file__).resolve().parent))
from servicios_ref_cfg import SERVICIOS
AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = "9ea79fe31584435abe88b02e7aed4e6e"; MODELO = "s2.1-pro-free"


def llave():
    for l in open('/workspaces/Nexusv2.0launch18octubre/.env', encoding='utf8'):
        if l.startswith('FISH_API_KEY='):
            return l.split('=', 1)[1].strip().strip('"\'')


def main():
    k = llave(); (AQUI / 'voz').mkdir(exist_ok=True)
    for srv, c in SERVICIOS.items():
        for n, (t, vel, _, _) in c['tomas'].items():
            if len(sys.argv) > 1 and n not in sys.argv[1:]:
                continue
            req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                data=json.dumps({'text': t, 'format': 'mp3', 'sample_rate': 44100, 'reference_id': VOZ, 'prosody': {'speed': vel}, 'temperature': 0.65, 'top_p': 0.8}).encode(),
                headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json', 'model': MODELO})
            mp3 = AQUI / 'voz' / f'{n}.mp3'
            mp3.write_bytes(urllib.request.urlopen(req, timeout=180).read())
            subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af',
                'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.12',
                '-ar', '44100', str(AQUI / 'voz' / f'{n}_44.wav')], check=True)
            subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'voz' / f'{n}_44.wav'), '-ac', '1', '-ar', '16000', str(AQUI / 'voz' / f'{n}.wav')], check=True)
            print(srv, n, round((AQUI / 'voz' / f'{n}.wav').stat().st_size / 32000, 2), 's', flush=True)


if __name__ == '__main__':
    main()
