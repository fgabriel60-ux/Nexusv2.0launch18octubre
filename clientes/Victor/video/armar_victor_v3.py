"""Servilin (Víctor) v3: limpieza en OBRA FINA, sin escenas con líquidos raros (la máquina de la v2 y las 2 escenas nuevas salieron con charcos y pintura
escurriendo; se descartaron). Solo las 2 escenas IA limpias de la v2 (trapeado y supervisión) + SU video real de la barredora en bodega + SU voz real
clonada (sus notas del 20 oct) diciendo obra fina + tarjeta. Uso: python3 armar_victor_v3.py"""
import json, subprocess, sys, urllib.request, uuid
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/victor_v3'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
REAL = AQUI.parent / 'whatsapp' / 'nuevas' / '1023_122723_24316.mp4'
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
ID = AQUI / 'voz' / 'voz_id_fish.txt'
W, H = 1080, 1920
TARJ = 4.0
FRASES = [  # (voz, toma, inicio, texto en pantalla)
    ('¿Vas a entregar departamentos o casas? La limpieza de obra fina no debería ser un problema.', AQUI / 'v2' / 'S1_trapeo.mp4', 0.0,
     ['LIMPIEZA EN OBRA FINA', 'ENTREGA DE DEPAS Y CASAS']),
    ('En Servilín dejamos tu obra lista para entregar, con personal uniformado, capacitado y supervisado.', AQUI / 'v2' / 'S4_supervision.mp4', 0.0,
     ['PERSONAL UNIFORMADO', 'CAPACITADO Y SUPERVISADO']),
    ('También limpiamos plantas, bodegas y empresas.', REAL, 2.0, ['PLANTAS · BODEGAS', 'Y EMPRESAS']),
    ('Pide tu cotización por WhatsApp.', REAL, 14.0, ['PIDE TU COTIZACIÓN', 'POR WHATSAPP']),
]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def crea_voz():
    if ID.exists(): return ID.read_text().strip()
    notas = sorted((AQUI / 'voz' / 'notas').glob('*.ogg'))
    mp3 = AQUI / 'voz' / 'muestra.mp3'
    ff([x for n in notas for x in ('-i', str(n))] + ['-filter_complex', ''.join(f'[{i}:a]' for i in range(len(notas))) + f'concat=n={len(notas)}:v=0:a=1',
       '-ac', '1', '-ar', '44100', str(mp3)])
    lim = '----fish' + uuid.uuid4().hex; p = []
    for n, v in [('title', 'Victor Servilin (voz real)'), ('type', 'tts'), ('train_mode', 'fast'), ('visibility', 'private')]:
        p.append(f'--{lim}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    p.append(f'--{lim}\r\nContent-Disposition: form-data; name="voices"; filename="muestra.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + mp3.read_bytes() + b'\r\n')
    p.append(f'--{lim}--\r\n'.encode())
    r = urllib.request.Request('https://api.fish.audio/model', data=b''.join(p), headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'multipart/form-data; boundary=' + lim})
    i = json.loads(urllib.request.urlopen(r, timeout=300).read())['_id']; ID.write_text(i); return i


def voces():
    vid = crea_voz(); durs = []
    for i, (texto, *_) in enumerate(FRASES):
        mp3 = AQUI / 'voz' / f'v3_f{i}.mp3'; wav = AQUI / 'voz' / f'v3_f{i}.wav'
        if not wav.exists():
            r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                       data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': vid, 'prosody': {'speed': 1.05}, 'temperature': 0.65, 'top_p': 0.8}).encode(),
                                       headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
            mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
            ff(['-i', str(mp3), '-af', f'{CADENA},apad=pad_dur=0.25', '-ar', '48000', '-ac', '2', str(wav)])
        durs.append(round(duracion(wav), 2))
    return durs


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (10, 28, 64)); d = ImageDraw.Draw(img)
    AMARILLO, VERDE = (250, 214, 50), (37, 211, 102)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('SERVILIN', 540, 130, (255, 255, 255)); c('LIMPIEZA EN OBRA FINA', 700, 60, AMARILLO)
    c('CASAS · DEPARTAMENTOS · EMPRESAS', 790, 44, (255, 255, 255), 'Bold')
    t = 'PIDE TU COTIZACIÓN POR WHATSAPP'; f = fu(42, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 940, (W + a) / 2, 1070), 65, fill=VERDE); d.text(((W - a) / 2 + 55, 980), t, font=f, fill=(255, 255, 255))
    img.save(ruta)


def main():
    durs = voces(); tarjeta(TMP / 'tarjeta.png')
    T = sum(durs); TOTAL = T + TARJ
    ent, fl = [], ''
    for i, ((_, toma, ini, _), d) in enumerate(zip(FRASES, durs)):
        ent += ['-ss', str(ini), '-t', f'{d + 0.3:.2f}', '-i', str(toma)]
        fl += (f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.1,'
               f'fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];')
    k = len(FRASES)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];' + ''.join(f'[c{i}]' for i in range(k)) + f'[tj]concat=n={k + 1}:v=1:a=0[base];'
    cur, t0 = 'base', 0.0
    for j, ((*_, lin), d) in enumerate(zip(FRASES, durs)):
        p = TMP / f't{j}.png'; tex(lin, p, 1380, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{k + 1 + j}:v]overlay=0:0:enable='between(t,{t0 + 0.1:.2f},{t0 + d - 0.05:.2f})'[o{j}];"; cur = f'o{j}'; t0 += d
    a0 = k + 1 + k
    voz = TMP / 'voz.wav'
    ff([x for i in range(k) for x in ('-i', str(AQUI / 'voz' / f'v3_f{i}.wav'))] + ['-filter_complex', ''.join(f'[{i}:a]' for i in range(k)) + f'concat=n={k}:v=0:a=1[v]', '-map', '[v]', str(voz)])
    ent += ['-i', str(MUSICA), '-i', str(voz)]
    fl += (f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,volume=0.18,afade=t=in:st=0:d=0.5,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
           f"[{a0 + 1}:a]aresample=48000[vz];[mu][vz]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / 'hd.mp4'; sal = AQUI / 'Servilin_obra_fina_v3.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s', durs)


if __name__ == '__main__':
    main()
