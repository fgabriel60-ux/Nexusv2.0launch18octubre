"""Corrige la v22 de Lisbeth: el hospital está A UN LADO del Tecnológico (lo dijo ella el 24 oct), no «a dos kilómetros y medio». Cambia esa frase por su
voz clonada y tapa con desenfoque el pin del hospital mal puesto, el subtítulo y el letrero «HOSPITAL ≈ 2.5 km»; encima pone el pin junto al Tecnológico,
el subtítulo y el letrero nuevos. El resto de la v22 queda igual. Deja referencia/v22_corregido.mp4. Uso: python3 corregir_v22_hospital.py"""
import json, subprocess, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu

AQUI = Path(__file__).resolve().parent
V22 = AQUI.parent / 'referencia' / 'v22.mp4'
SAL = AQUI.parent / 'referencia' / 'v22_corregido.mp4'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/v22_fix'); TMP.mkdir(parents=True, exist_ok=True)
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
VOZ_LISBETH = '9882e85f87334044b99ba2c4d3add4d3'
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
W, H = 720, 1280
A, B = 15.22, 17.92          # «y el hospital a dos kilómetros y medio» en la v22
PIN = (15.6, 20.6)           # mientras se ve el pin del hospital mal puesto
LETRERO = (15.6, 19.25)      # letrero «HOSPITAL ≈ 2.5 km», hasta que entra «ZONA QUE YA»
SUB_FIN = 18.79              # el subtítulo viejo «kilómetros y medio la» sigue hasta que entra «zona ya se está»


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def voz():
    mp3 = TMP / 'frase.mp3'
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                               data=json.dumps({'text': 'con el hospital a un lado del Tecnológico.', 'format': 'mp3', 'reference_id': VOZ_LISBETH,
                                                'prosody': {'speed': 1.04}, 'temperature': 0.65, 'top_p': 0.8}).encode(),
                               headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
    mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
    d = duracion(mp3); vel = max(0.8, min(1.25, d / (B - A - 0.1)))   # que quepa en el hueco de la frase vieja
    ff(['-i', str(mp3), '-af', f'{CADENA},atempo={vel:.3f},apad=whole_dur={B - A:.2f}', '-ar', '44100', '-ac', '2', '-t', f'{B - A:.2f}', str(TMP / 'frase.wav')])
    return d, vel


def capas():
    img = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(img)   # subtítulo como los de la v22: blanco con la última palabra en amarillo
    f = fu(44, 'Bold'); t1, t2 = 'con el hospital a un ', 'lado'
    x = (W - d.textlength(t1 + t2, font=f)) / 2
    d.text((x, 800), t1, font=f, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((x + d.textlength(t1, font=f), 800), t2, font=f, fill=(255, 205, 40), stroke_width=3, stroke_fill=(0, 0, 0)); img.save(TMP / 'sub.png')
    img = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(img)   # letrero inferior
    d.rectangle((46, 1052, 51, 1132), fill=(226, 186, 98))
    d.text((70, 1050), 'HOSPITAL', font=fu(40, 'ExtraBold'), fill=(255, 255, 255)); d.text((70, 1098), 'A UN LADO DEL TECNOLÓGICO', font=fu(26, 'Bold'), fill=(235, 235, 235))
    img.save(TMP / 'letrero.png')
    img = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(img)   # pin junto al Tecnológico, con el estilo de las etiquetas de la v22
    d.ellipse((392, 594, 410, 612), fill=(232, 76, 76), outline=(255, 255, 255), width=3)
    f = fu(22, 'ExtraBold'); w = d.textlength('HOSPITAL', font=f) + 36
    d.rounded_rectangle((376 - w, 586, 376, 622), 9, fill=(16, 28, 56), outline=(226, 186, 98), width=2); d.text((376 - w + 18, 592), 'HOSPITAL', font=f, fill=(255, 255, 255))
    img.save(TMP / 'pin.png')


def main():
    d, vel = voz(); capas()
    tapa = [(480, 690, 220, 110, *PIN), (60, 780, 600, 100, A, SUB_FIN), (30, 1040, 610, 105, *LETRERO)]   # x, y, ancho, alto, desde, hasta
    fl, cur = '', '0:v'
    for i, (x, y, w, h, a, b) in enumerate(tapa):
        fl += f"[{cur}]split[s{i}][t{i}];[t{i}]crop={w}:{h}:{x}:{y},boxblur=18:2[b{i}];[s{i}][b{i}]overlay={x}:{y}:enable='between(t,{a},{b})'[v{i}];"; cur = f'v{i}'
    for j, (png, a, b) in enumerate([('sub.png', A, SUB_FIN), ('letrero.png', *LETRERO), ('pin.png', *PIN)]):
        fl += f"[{cur}][{j + 1}:v]overlay=0:0:enable='between(t,{a},{b})'[w{j}];"; cur = f'w{j}'
    fl += (f"[0:a]asplit[x1][x2];[x1]atrim=0:{A},asetpts=PTS-STARTPTS[p1];[x2]atrim=start={B},asetpts=PTS-STARTPTS[p3];"
           f"[4:a]aresample=44100,aformat=channel_layouts=stereo[p2];[p1][p2][p3]concat=n=3:v=0:a=1[a]")
    ff(['-i', str(V22)] + [x for p in ('sub.png', 'letrero.png', 'pin.png') for x in ('-loop', '1', '-i', str(TMP / p))] + ['-i', str(TMP / 'frase.wav'),
       '-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{duracion(V22):.2f}', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(SAL)])
    print(SAL, f'frase {d:.2f}s a {vel:.2f}x')


if __name__ == '__main__':
    main()
