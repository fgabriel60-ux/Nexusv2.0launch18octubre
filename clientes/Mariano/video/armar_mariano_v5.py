"""Mariano · Vizcaíno v5 (color corregido + subs virales): arma las escenas de mariano_v4_escenas.py con palabras gigantes palabra por palabra (como el reel del realtor), los 3 modelos
con sus precios del arte oficial en tarjeta premium y cierre con palabra clave. Uso: python3 armar_mariano_v4.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu
from kinetic import palabras
import subs_virales
from mariano_v4_escenas import FRASES as GUION   # el texto real de cada frase, para que Whisper no cambie palabras

AQUI = Path(__file__).resolve().parent
V4 = AQUI / 'v4'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/22fc94f1-5b92-44e4-9296-5a2e47cda3a3/scratchpad/mariano_v5'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
WHOOSH = AQUI.parents[1] / 'Guillermo' / 'video' / 'sfx' / 'whoosh.wav'
W, H = 1080, 1920
TARJ = 3.6
# frase de voz → (toma, desde qué segundo de la toma, palabras clave en color); la frase 4 (precios) va sobre la misma toma que la 3
FRASES = [('M4_camina', 0.0, {'oportunidad'}), ('M4_dron', 0.0, {'etapa', 'vida'}), ('M4_presenta', 0.0, {'acceso', 'controlado'}),
          ('M4_fila', 0.0, {'modelos'}), ('M4_fila', None, set()), ('M4_cierre', 0.0, {'whatsapp'})]
MODELOS = [('BENJAMINA', '$2.85 MDP'), ('SALVIA', '$3.5 MDP'), ('BUGAMBILIA', '$2.45 MDP')]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def tarjeta_precios(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for y in range(H // 2, H):   # degradado oscuro abajo para que el texto respire
        d.line([(0, y), (W, y)], fill=(6, 10, 22, int(215 * min(1, (y - H / 2) / (H * 0.25)))))
    NAR = (255, 160, 40)
    def c(t, cx, y, tam, col, peso):
        f = fu(tam, peso); d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=col)
    c('DESDE', W / 2, 1180, 46, (255, 255, 255), 'Bold')
    for i, (n, p) in enumerate(MODELOS):
        cx = W * (i + 0.5) / 3
        c(n, cx, 1270, 52, (255, 255, 255), 'Black'); c(p, cx, 1340, 58, NAR, 'Black')
        if i: d.line([(W * i / 3, 1275), (W * i / 3, 1405)], fill=(255, 255, 255, 120), width=2)
    c('*APLICAN RESTRICCIONES · GRUPO LAGSA', W / 2, 1460, 26, (220, 220, 220), 'Bold')
    img.save(ruta)


def tarjeta_final(ruta):
    img = Image.new('RGB', (W, H), (8, 18, 44)); d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=(int(8 + 30 * y / H), int(30 + 60 * (1 - y / H)), int(90 + 80 * (1 - y / H))))
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('VIZCAÍNO', 560, 140, (255, 255, 255)); c('RESIDENCIAL · ROSARITO, B.C.', 720, 46, (255, 200, 120), 'Bold')
    c('EN PRIVADA · ACCESO CONTROLADO', 820, 38, (255, 255, 255), 'Bold'); c('CANCHA DE PÁDEL · ÁREA DE JUEGOS', 875, 38, (255, 255, 255), 'Bold')
    t = 'ESCRIBE «VIZCAÍNO» + TU PRESUPUESTO'; f = fu(40, 'ExtraBold'); a = d.textlength(t, font=f) + 100
    d.rounded_rectangle(((W - a) / 2, 990, (W + a) / 2, 1110), 60, fill=(37, 211, 102)); d.text(((W - a) / 2 + 50, 1025), t, font=f, fill=(255, 255, 255))
    c('GRUPO LAGSA', 1200, 44, (220, 230, 255), 'Bold')
    img.save(ruta)


def main():
    durs = [duracion(V4 / 'voz' / f'f{i}.wav') for i in range(len(FRASES))]
    T = sum(durs); TOTAL = T + TARJ
    # tomas: la 3 y la 4 son la misma toma continua (fila de casas)
    tramos, t0 = [], 0.0
    for i, (toma, ini, _) in enumerate(FRASES):
        if ini is None: tramos[-1][2] += durs[i]
        else: tramos.append([toma, ini, durs[i]])
    ent, fl = [], ''
    for i, (toma, ini, d) in enumerate(tramos):
        ent += ['-ss', str(ini), '-i', str(V4 / f'{toma}.mp4')]
        fl += (f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.7,eq=contrast=1.03:saturation=0.78:gamma=1.03,colorbalance=rs=-0.05:gs=0.01:bs=0.05:rm=-0.07:gm=0.0:bm=0.06:rh=-0.04:bh=0.04,'
               f'fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];')
    k = len(tramos)
    tarjeta_final(TMP / 'final.png'); ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'final.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];' + ''.join(f'[c{i}]' for i in range(k)) + f'[tj]concat=n={k + 1}:v=1:a=0[base];'
    # subtítulos virales palabra por palabra (menos la frase de precios, que lleva tarjeta)
    ws, t0 = [], 0.0
    for i, (_, ini, clave) in enumerate(FRASES):
        if ini is not None or clave:
            ws += [(w, a + t0, z + t0) for w, a, z in palabras(V4 / 'voz' / f'f{i}.wav', GUION[i])]
        t0 += durs[i]
    t_prec = sum(durs[:4])
    capas = subs_virales.capas(ws, TMP / 'subs', y=0.80, evitar=[(t_prec - 0.01, t_prec + durs[4])])
    ent_s, fl_s, cur = subs_virales.overlay(capas, 'base', k + 1, TOTAL)
    ent += ent_s; fl += fl_s
    tarjeta_precios(TMP / 'precios.png'); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(TMP / 'precios.png')]
    fl += f"[{cur}][{k + 1 + len(capas)}:v]overlay=0:0:enable='between(t,{t_prec + 0.1:.2f},{t_prec + durs[4]:.2f})'[opre];"; cur = 'opre'
    a0 = k + 2 + len(capas)
    voz = TMP / 'voz.wav'
    ff([x for i in range(len(FRASES)) for x in ('-i', str(V4 / 'voz' / f'f{i}.wav'))] + ['-filter_complex',
       ''.join(f'[{i}:a]aresample=48000[a{i}];' for i in range(len(FRASES))) + ''.join(f'[a{i}]' for i in range(len(FRASES))) + f'concat=n={len(FRASES)}:v=0:a=1[v]', '-map', '[v]', str(voz)])
    t_dron = durs[0]
    ent += ['-i', str(MUSICA), '-i', str(voz), '-i', str(WHOOSH)]
    fl += (f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,volume=0.2,afade=t=in:st=0:d=0.4,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];[{a0 + 1}:a]aresample=48000[vz];"
           f"[{a0 + 2}:a]aresample=48000,volume=0.6,adelay={int(t_dron * 1000) - 120}|{int(t_dron * 1000) - 120}[wh];"
           f"[mu][vz][wh]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / 'hd.mp4'; sal = AQUI / 'Vizcaino_v5_color_subs.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', str(hd)])
    ff(['-i', str(hd), '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
