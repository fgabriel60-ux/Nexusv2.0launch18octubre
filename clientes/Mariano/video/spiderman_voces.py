"""Mariano · gancho «estilo Spiderman»: voces Fish (voz clonada de Mariano) por frase → spiderman/voz/fN.wav.
Precios REALES de sus videos: Sotol desde 1.4M (2 hab.), Bugambilia desde 2.4M, Benjamina desde 2.8M, Salvia desde 3.1M (4 hab.).
Uso: python3 spiderman_voces.py   (borra el wav de una frase para regenerarla)"""
import json, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
VOZ = AQUI / 'spiderman' / 'voz'
FF = imageio_ffmpeg.get_ffmpeg_exe()
import os
LLAVE = os.environ.get('FISH_API_KEY', '')
VOZ_MARIANO = '574f8646b8e54d1dab2bb8a6dd1aa189'
FRASES = {
    'gancho': '¿Buscas casa en Rosarito? Vizcaíno Residencial, ¡mira esto!',
    'sotol': 'Sotol, desde un millón cuatrocientos mil.',
    'bugambilia': 'Bugambilia, desde dos millones cuatrocientos mil.',
    'benjamina': 'Benjamina, desde dos millones ochocientos mil.',
    'salvia': 'Y Salvia, de cuatro recámaras, desde tres millones cien mil.',
    'privada': 'En privada, con cancha de pádel. Aceptan Infonavit y crédito hipotecario.',
    'cta': 'Escríbeme «Vizcaíno» por WhatsApp y agendamos tu visita.',
}


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def voces(velocidad=1.08):
    VOZ.mkdir(parents=True, exist_ok=True); d = {}
    for n, t in FRASES.items():
        mp3, wav = VOZ / f'{n}.mp3', VOZ / f'{n}.wav'
        if not wav.exists():
            r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                       data=json.dumps({'text': t, 'format': 'mp3', 'reference_id': VOZ_MARIANO, 'prosody': {'speed': velocidad},
                                                        'temperature': 0.6, 'top_p': 0.8}).encode(),
                                       headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
            mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
            # recorta silencios de los extremos y deja 0.12 s de aire al final
            subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af',
                            'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.12',
                            '-ar', '44100', '-ac', '1', str(wav)], check=True)
        d[n] = round(duracion(wav), 2)
    return d


if __name__ == '__main__':
    print(voces())
