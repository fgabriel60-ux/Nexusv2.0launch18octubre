"""Voz Fish (GENÉRICA, femenina, no es la voz real de la Dra. Ángeles) para el reel de implantes estilo referencia.
Un audio por idea (= una toma H3 con lip-sync). Sale voz/ref_S1..S5.mp3 (44.1 kHz) y .wav (16 kHz mono, guía de labios de H3).
Uso: python3 voz_implantes_ref.py [S3 ...]   (sin argumentos: todas)"""
import json, subprocess, sys, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOZ = "9ea79fe31584435abe88b02e7aed4e6e"   # Fish «mujer»: femenina, madura, profesional, cálida (genérica)
MODELO = "s2.1-pro-free"
GUION = {
    "S1": ("¿Te falta un diente? No lo dejes así.", 1.0),
    "S2": ("Cuando pierdes una pieza, el hueso de esa zona puede irse perdiendo con el tiempo, y los dientes de al lado se pueden mover.", 1.06),
    "S3": ("La solución es un implante dental: una raíz de titanio que se coloca dentro del hueso, como una raíz nueva.", 1.04),
    "S4": ("Se coloca con anestesia local, y la corona va aparte.", 1.02),
    "S5": ("Aquí en Víniers Dental, tu implante va desde doce mil quinientos pesos. Escríbenos por WhatsApp y agenda tu valoración.", 1.04),
}


def llave():
    for l in open('/workspaces/Nexusv2.0launch18octubre/.env', encoding='utf8'):
        if l.startswith('FISH_API_KEY='):
            return l.split('=', 1)[1].strip().strip('"\'')


def main():
    k = llave(); (AQUI / 'voz').mkdir(exist_ok=True)
    for n, (t, vel) in GUION.items():
        if len(sys.argv) > 1 and n not in sys.argv[1:]:
            continue
        req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                     data=json.dumps({'text': t, 'format': 'mp3', 'sample_rate': 44100, 'reference_id': VOZ, 'prosody': {'speed': vel},
                                                      'temperature': 0.65, 'top_p': 0.8}).encode(),
                                     headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json', 'model': MODELO})
        mp3 = AQUI / 'voz' / f'ref_{n}.mp3'
        mp3.write_bytes(urllib.request.urlopen(req, timeout=180).read())
        # recorta silencios de los bordes
        subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.12',
                        '-ar', '44100', str(AQUI / 'voz' / f'ref_{n}_44.wav')], check=True)
        subprocess.run([FF, '-v', 'error', '-y', '-i', str(AQUI / 'voz' / f'ref_{n}_44.wav'), '-ac', '1', '-ar', '16000', str(AQUI / 'voz' / f'ref_{n}.wav')], check=True)
        print(n, round((AQUI / 'voz' / f'ref_{n}.wav').stat().st_size / 32000, 2), 's')


if __name__ == '__main__':
    main()
