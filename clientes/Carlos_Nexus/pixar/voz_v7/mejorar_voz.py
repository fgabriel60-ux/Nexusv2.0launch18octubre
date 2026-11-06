"""Pixar v7 de Carlos (Nexus): misma imagen y lipsync del v6, voz nueva con Fish s2-pro (voz «Carlos real · voz aislada»).
Cada frase se genera aparte, se recorta el silencio y se ajusta a la duración de la frase original para que los labios sigan cuadrando."""
import json, os, re, subprocess, urllib.request
from pathlib import Path
AQUI = Path(__file__).resolve().parent
VOZ = '1f679152b5d64c09a8e8eeecd3eb5424'
FRASES = ['¿Tu publicidad no te trae mensajes?', 'Estás perdiendo dinero hoy mismo.',
          'Muchos negocios regalan su presupuesto a Meta intentando adivinar qué funciona, sin una estrategia clara.',
          'En Nexus creamos tu estrategia, tus volantes y tu primer video gratis, en una llamada de diez minutos.',
          'Ya ayudamos a otros a bajar sus costos de mensajes drásticamente.', 'Toca el botón y agenda tu llamada.',
          'El costo es de quinientos pesos.', 'El precio por dejar de adivinar y empezar a dominar Facebook.']
FIN_PAL = ['mensajes', 'mismo', 'clara', 'minutos', 'drásticamente', 'llamada', 'pesos', 'facebook']
ff = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
dur = lambda p: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)
pal = [(re.sub(r'[^\wáéíóúñ]', '', w.lower()), a, b) for s in json.load(open(AQUI / 'segmentos.json')) for w, a, b in s['pal']]
# tramos originales: cada frase va del inicio de su primera palabra al final de la palabra con que termina
tramos, i = [], 0
for fin in FIN_PAL:
    ini = pal[i][1]
    while not pal[i][0].startswith(fin[:6]): i += 1
    tramos.append((ini, pal[i][2])); i += 1
total = dur(AQUI / 'original.wav'); ent, flt = [], []
for k, (txt, (a, b)) in enumerate(zip(FRASES, tramos)):
    raw, w = AQUI / f'f{k}_raw.wav', AQUI / f'f{k}.wav'
    if not raw.exists():
        r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': txt, 'format': 'wav', 'reference_id': VOZ}).encode(),
                                   headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's2-pro'})
        raw.write_bytes(urllib.request.urlopen(r, timeout=300).read())
    ff('-i', str(raw), '-af', 'silenceremove=start_periods=1:start_threshold=-55dB,areverse,silenceremove=start_periods=1:start_threshold=-55dB,areverse', '-ar', '44100', '-ac', '1', str(AQUI / 'tmp.wav'))
    f = dur(AQUI / 'tmp.wav') / (b - a); f = min(max(f, 0.8), 1.25)  # ajuste suave de velocidad para caber en el tramo
    ff('-i', str(AQUI / 'tmp.wav'), '-af', f'atempo={f:.3f}', str(w))
    print(f'{k} {a:5.2f}-{b:5.2f} orig {b - a:.2f}s nueva {dur(w):.2f}s (x{f:.2f}) {txt}')
    ent += ['-i', str(w)]; flt.append(f'[{k}:a]adelay={int(a * 1000)}|{int(a * 1000)}[a{k}]')
mix = ';'.join(flt) + ';' + ''.join(f'[a{k}]' for k in range(len(FRASES))) + f'amix=inputs={len(FRASES)}:normalize=0,apad,atrim=0:{total:.2f},highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5[o]'
ff(*ent, '-filter_complex', mix, '-map', '[o]', '-ar', '44100', '-ac', '2', str(AQUI / 'voz_nueva.wav'))
sal = AQUI.parent / 'Pixar_v7_voz_mejorada.mp4'
ff('-i', str(AQUI.parent / 'Pixar_v6_efectos_v2.mp4'), '-i', str(AQUI / 'voz_nueva.wav'), '-filter_complex', '[1:a]apad[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', str(dur(AQUI.parent / 'Pixar_v6_efectos_v2.mp4')), '-movflags', '+faststart', str(sal))
print(sal, round(dur(sal), 1), 's')
