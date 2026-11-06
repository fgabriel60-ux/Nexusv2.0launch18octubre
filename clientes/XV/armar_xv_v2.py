"""Reel XV completo v2 (Manuel): planos «mágicos» de IA (Modal) con música suave + fiesta real con el audio animado (entra con las escenas de fiesta, como en la referencia).
Uso: python3 armar_xv_v2.py [ruta_musica.wav]"""
import subprocess, sys
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
XV = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/6babdfdf-0126-43a3-a459-73c583442b35/scratchpad/xv')   # segmentos de fiesta ya cortados en 9:16 (armar_xv.py)
TOM = AQUI / 'modal_tomas'
MUSICA = Path(sys.argv[1]) if len(sys.argv) > 1 else None
W, H = 1080, 1920
XF = 0.3
# (toma, inicio, duración)
INTRO = [('S2', 0.0, 3.6), ('S1', 0.3, 3.2), ('S4', 0.2, 2.8), ('S3', 0.2, 2.6), ('S5', 0.2, 3.0)]
T_INTRO = sum(d for _, _, d in INTRO) - XF * (len(INTRO) - 1)
FIESTA = ['s20.mp4', 's21.mp4', 's22.mp4', 's23.mp4', 's24.mp4', 's40.mp4']
T_FIESTA = 3.0 * 5 + 6.0
TOTAL = T_INTRO + T_FIESTA
TMP = XV / 'v2'; TMP.mkdir(parents=True, exist_ok=True)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    # 1) intro mágico: xfade entre planos, con un acabado de cine suave (nitidez, contraste, grano fino)
    ent, fl = [], ''
    for i, (t, ini, d) in enumerate(INTRO):
        ent += ['-ss', str(ini), '-t', str(d), '-i', str(TOM / f'{t}.mp4')]
        fl += (f"[{i}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.7,eq=contrast=1.05:saturation=1.07,noise=alls=5:allf=t,fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS,settb=1/30,fps=30[v{i}];")
    prev, acum = 'v0', INTRO[0][2]
    for i in range(1, len(INTRO)):
        off = acum - XF
        fl += f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}];"; prev = f'x{i}'; acum = off + INTRO[i][2]
    intro = TMP / 'intro.mp4'
    ff(ent + ['-filter_complex', fl.rstrip(';'), '-map', f'[{prev}]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', str(intro)])
    # 2) concatenar intro + fiesta
    (TMP / 'lista.txt').write_text(f"file '{intro}'\n" + ''.join(f"file '{XV / f}'\n" for f in FIESTA))
    # 3) audio: música suave (intro) → audio animado real de la fiesta
    fiesta_wav = TMP / 'fiesta.wav'
    ff(['-ss', '20', '-t', f'{T_FIESTA + 1.5:.1f}', '-i', str(AQUI / 'originales' / 'C6755.MP4'), '-vn', '-ac', '2', '-ar', '44100', str(fiesta_wav)])
    t_f = T_INTRO - 0.6                                  # la fiesta entra un poco antes del corte, como pulso que anuncia el cambio
    ent2 = ['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-loop', '1', '-t', '3.2', '-i', str(XV / 'tarjeta.png'), '-i', str(fiesta_wav)]
    if MUSICA: ent2 += ['-i', str(MUSICA)]
    fl2 = f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+{TOTAL - 3.0:.2f}/TB[tj];[0:v][tj]overlay=0:0:eof_action=pass[v];"
    fl2 += f"[2:a]loudnorm=I=-15:TP=-1.5,afade=t=in:st=0:d=0.9,adelay={int(t_f * 1000)}|{int(t_f * 1000)}[f];"
    if MUSICA:
        fl2 += f"[3:a]aresample=44100,loudnorm=I=-19:TP=-2,afade=t=in:st=0:d=0.8,afade=t=out:st={t_f - 0.2:.2f}:d=1.4,atrim=0:{t_f + 1.4:.2f}[m];[m][f]amix=inputs=2:normalize=0,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[a]"
    else:
        fl2 += f"[f]afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[a]"
    hd = TMP / 'xv_v2_hd.mp4'; sal = AQUI / 'final' / 'XV_reel_v2_magico.mp4'
    ff(ent2 + ['-filter_complex', fl2, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
