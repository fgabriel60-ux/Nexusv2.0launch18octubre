"""Reel XV v3 (Manuel): sin Modal. Mejoras: color de cine + glow + viñeta + cámara lenta en la fiesta, y nueva música de fiesta (tramo C6801 con el ritmo más marcado).
Uso: python3 armar_xv_v3.py musica_suave_s7.wav"""
import subprocess, sys
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
ORI = AQUI / 'originales'
TOM = AQUI / 'modal_tomas'
XV = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/6babdfdf-0126-43a3-a459-73c583442b35/scratchpad/xv')
TMP = XV / 'v3'; TMP.mkdir(parents=True, exist_ok=True)
MUSICA = Path(sys.argv[1])
W, H = 1080, 1920
XF = 0.3
INTRO = [('S2', 0.0, 3.6), ('S1', 0.3, 3.2), ('S4', 0.2, 2.8), ('S3', 0.2, 2.6), ('S5', 0.2, 3.0)]
T_INTRO = sum(d for _, _, d in INTRO) - XF * (len(INTRO) - 1)
# fiesta: (archivo, inicio, centro, factor de velocidad) · salida de 3 s por corte (cámara lenta 0.5× = 1.5 s de fuente)
FIESTA = [('C6801', 50, .48, .5), ('C6755', 35, .75, 1.0), ('C6801', 65, .45, .5), ('C6801', 140, .45, 1.0), ('C6771', 10, .40, .5)]
FINAL = ('C6801', 170, .62, .5)       # 6 s de salida (3 s toma + 3 s tarjeta)
T_FIESTA = 3.0 * len(FIESTA) + 6.0
TOTAL = T_INTRO + T_FIESTA
AUDIO_FIESTA_INI = 72                 # tramo de C6801 con el ritmo más marcado y estable


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


GLOW = ("split[a][b];[b]gblur=sigma=20,eq=brightness=0.02[g];[a][g]blend=all_mode=screen:all_opacity=0.16,vignette=PI/5")


def seg_fiesta(n, f, ini, cx, vel, dur_sal):
    ancho = 2160 * 9 / 16; x = int(max(0, min(3840 - ancho, cx * 3840 - ancho / 2)))
    fuente = dur_sal * vel; s = TMP / f'p{n}.mp4'
    fc = (f"[0:v]crop={int(ancho)}:2160:{x}:0,scale={W}:{H}:flags=lanczos,setsar=1,setpts={1 / vel:.3f}*PTS,fps=30,"
          f"curves=all='0/0.03 0.35/0.40 1/1',eq=contrast=1.07:saturation=1.22:gamma=1.07,colorbalance=rs=0.04:bs=-0.04:rh=0.03:bh=-0.02,{GLOW},noise=alls=4:allf=t,format=yuv420p[v]")
    ff(['-ss', str(ini), '-t', f'{fuente:.2f}', '-i', str(ORI / f'{f}.MP4'), '-filter_complex', fc, '-map', '[v]', '-an', '-t', f'{dur_sal:.2f}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', str(s)])
    return s


def main():
    # 1) intro mágico (planos de IA): nitidez, color suave, glow y viñeta
    ent, fl = [], ''
    for i, (t, ini, d) in enumerate(INTRO):
        ent += ['-ss', str(ini), '-t', str(d), '-i', str(TOM / f'{t}.mp4')]
        fl += (f"[{i}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.8,eq=contrast=1.06:saturation=1.08,colorbalance=rs=0.02:bs=-0.02,{GLOW},noise=alls=5:allf=t,"
               f"fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS,settb=1/30,fps=30[v{i}];")
    prev, acum = 'v0', INTRO[0][2]
    for i in range(1, len(INTRO)):
        off = acum - XF
        fl += f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}];"; prev = f'x{i}'; acum = off + INTRO[i][2]
    intro = TMP / 'intro.mp4'
    ff(ent + ['-filter_complex', fl.rstrip(';'), '-map', f'[{prev}]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', str(intro)])
    # 2) fiesta con color de cine y cámara lenta
    segs = [seg_fiesta(i, f, ini, cx, vel, 3.0) for i, (f, ini, cx, vel) in enumerate(FIESTA)] + [seg_fiesta(9, *FINAL, 6.0)]
    (TMP / 'lista.txt').write_text(f"file '{intro}'\n" + ''.join(f"file '{s}'\n" for s in segs))
    # 3) audio: música suave → música de fiesta real (C6801, ritmo marcado)
    fiesta_wav = TMP / 'fiesta.wav'
    ff(['-ss', str(AUDIO_FIESTA_INI), '-t', f'{T_FIESTA + 1.5:.1f}', '-i', str(ORI / 'C6801.MP4'), '-vn', '-ac', '2', '-ar', '44100', str(fiesta_wav)])
    t_f = T_INTRO - 0.6
    ent2 = ['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-loop', '1', '-t', '3.2', '-i', str(XV / 'tarjeta.png'), '-i', str(fiesta_wav), '-i', str(MUSICA)]
    fl2 = f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+{TOTAL - 3.0:.2f}/TB[tj];[0:v][tj]overlay=0:0:eof_action=pass[v];"
    fl2 += f"[2:a]loudnorm=I=-15:TP=-1.5,afade=t=in:st=0:d=0.9,adelay={int(t_f * 1000)}|{int(t_f * 1000)}[f];"
    fl2 += f"[3:a]aresample=44100,loudnorm=I=-19:TP=-2,afade=t=in:st=0:d=0.8,afade=t=out:st={t_f - 0.2:.2f}:d=1.4,atrim=0:{t_f + 1.4:.2f}[m];[m][f]amix=inputs=2:normalize=0,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[a]"
    hd = TMP / 'xv_v3_hd.mp4'; sal = AQUI / 'final' / 'XV_reel_v3.mp4'
    ff(ent2 + ['-filter_complex', fl2, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '25', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
