"""Mariano · gancho Spiderman v3: sólo el gancho (salto → aterrizaje → habla → dron) con los efectos de la referencia:
sacudida + destello en el impacto, hilo blanco brillante que sale disparado del dedo al señalar el cielo y whoosh/golpe sincronizados.
Uso: python3 armar_gancho_fx.py [vN]   → Vizcaino_gancho_fx_vN.mp4"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import armar_spiderman as A
from armar_spiderman import ff, seg_ia, componer, W, H, FPS, XD, SP, SFX, FRASES, duracion, beat, palabras, subs_virales

AQUI = Path(__file__).resolve().parent
VOZ = SP / 'voz'
T_IMPACTO = 1.24          # segundos desde el inicio: manos al piso + polvo
T_HILO = (6.30, 7.15)     # brazo arriba → el hilo sale del dedo
DEDO = ((0.26, 0.11), (0.20, 0.07))   # posición del dedo (fracción del cuadro) al inicio y al final del tramo


def hilo(fr, t):
    a, z = T_HILO
    if not (a <= t <= z + 0.3): return fr
    k = min(1.0, (t - a) / (z - a)); x = (DEDO[0][0] + (DEDO[1][0] - DEDO[0][0]) * k) * W; y = (DEDO[0][1] + (DEDO[1][1] - DEDO[0][1]) * k) * H
    cre = min(1.0, (t - a) / 0.14)                       # el hilo crece hacia arriba en 0.14 s
    fade = 1.0 if t <= z else max(0.0, 1 - (t - z) / 0.3)
    top = y - (y + 80) * cre
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.line([(x, y), (x + 6 * cre, top)], fill=255, width=7)
    brillo = np.asarray(m.filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255 * 1.6
    nucleo = np.asarray(m.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    al = np.clip(brillo * 0.7 + nucleo, 0, 1)[..., None] * fade
    return fr * (1 - al) + al


def impacto(fr, t):
    dt = t - T_IMPACTO
    if not (0 <= dt <= 0.4): return fr
    amp = 26 * np.exp(-dt * 11); dx = int(round(amp * np.sin(dt * 90))); dy = int(round(amp * np.cos(dt * 70)))
    fr = np.roll(fr, (dy, dx), (0, 1))
    fl = max(0.0, 0.55 - dt * 5.5)
    return fr * (1 - fl) + fl


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else 'v3'
    TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/cca32502-2d68-4e1b-bd4c-481af2b2afca/scratchpad') / f'gancho_{ver}'; TMP.mkdir(parents=True, exist_ok=True)
    ia = lambda n: SP / 'r2' / f'{n}.mp4'
    d_salto, d_habla, d_aereo = 5.2 / 2.6, 5.15, 1.4
    ini = [0.0, d_salto, d_salto + d_habla]; total = ini[2] + d_aereo
    ff(['-i', str(ia('S_salto')), '-filter_complex', f'[0:v]trim=start=0:end=5.2,setpts=(PTS-STARTPTS)/2.6,{A.AJ},fps={FPS},format=yuv420p[o]', '-map', '[o]', '-c:v', 'libx264', '-crf', '12', str(TMP / 'a.mp4')])
    seg_ia(ia('S_habla'), 0, d_habla + 1, 1.0, TMP / 'b.mp4', d_habla + XD)
    seg_ia(ia('S_aereo'), 0, 4.0, 1.9, TMP / 'c.mp4', d_aereo)
    ff(['-i', str(TMP / 'a.mp4'), '-i', str(TMP / 'b.mp4'), '-filter_complex',
        f'[0:v]trim=duration={ini[1]:.3f},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,fps={FPS},format=yuv420p[o]', '-map', '[o]', '-c:v', 'libx264', '-crf', '12', str(TMP / 'ab.mp4')])
    ff(['-i', str(TMP / 'ab.mp4'), '-i', str(TMP / 'c.mp4'), '-filter_complex',
        f'[0:v]fps={FPS},format=yuv420p[a];[1:v]fps={FPS},format=yuv420p[b];[a][b]xfade=transition=zoomin:duration={XD}:offset={ini[2] - XD / 2:.3f}[o]', '-map', '[o]', '-c:v', 'libx264', '-crf', '12', str(TMP / 'abc.mp4')])
    A.marca(TMP / 'marca.png'); A.etiqueta('Visualización', TMP / 'visual.png')
    t0 = ini[1]
    ws = [(w, a + t0, z + t0) for w, a, z in palabras(VOZ / 'gancho.wav', FRASES['gancho'].replace('¿', '').replace('¡', ''))]
    subs = subs_virales.capas(ws, TMP / 'sv', y=0.70, W=W, H=H)
    capas = [(png, a, z, 0.17, 12) for png, a, z in subs]
    capas += [(TMP / 'marca.png', ini[2] + 0.1, total, 0.25, 0), (TMP / 'visual.png', ini[2] + 0.1, total, 0.2, 0)]
    fx = lambda fr, t: hilo(impacto(fr, t), t)
    componer(TMP / 'abc.mp4', capas, total, TMP / 'video.mp4', fx)
    beat(TMP / 'beat.wav', ini[2], total)
    pistas = [(VOZ / 'gancho.wav', t0, 1.0), (SFX / 'whoosh.wav', 0.0, 0.7), (SFX / 'golpe.wav', T_IMPACTO - 0.03, 1.0), (SFX / 'boom.wav', T_IMPACTO - 0.03, 0.55),
              (SFX / 'whoosh.wav', T_HILO[0] - 0.02, 0.9), (SFX / 'whoosh.wav', ini[2] - 0.3, 0.9)]
    ent, fa = [], ''
    for j, (p, t, g) in enumerate(pistas):
        ent += ['-i', str(p)]; ms = int(max(0, t) * 1000)
        fa += f'[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms}[a{j}];'
    ent += ['-i', str(TMP / 'beat.wav')]; jb = len(pistas)
    fa += ''.join(f'[a{j}]' for j in range(len(pistas))) + f'amix=inputs={len(pistas)}:duration=longest:normalize=0,apad=whole_dur={total:.3f},asplit=2[vz][key];'
    fa += f'[{jb}:a]aresample=44100,volume=0.55[mu];[mu][key]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=300[mud];'
    fa += f'[vz][mud]amix=inputs=2:duration=longest:normalize=0,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5[a]'
    ff(ent + ['-filter_complex', fa, '-map', '[a]', '-ar', '44100', str(TMP / 'mezcla.wav')])
    sal = AQUI / f'Vizcaino_gancho_fx_{ver}.mp4'
    ff(['-i', str(TMP / 'video.mp4'), '-i', str(TMP / 'mezcla.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{total:.2f}s')


if __name__ == '__main__':
    main()
