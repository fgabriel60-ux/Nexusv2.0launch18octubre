"""Manuel (Hunab Ku Fotografía) · XV v10: primero las tomas TRANQUILAS en movimiento (rosas, retrato, caballo, giro, salón) con fundidos y música suave,
luego la FIESTA en cortes rápidos con su música, y el cierre con el logo de Hunab Ku (últimos 3.2 s de la v9). Uso: python3 armar_xv_v10.py"""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
TRANQ = [('modal_tomas/S4', 2.8), ('modal_tomas/S1', 2.8), ('modal_tomas/S5', 3.2), ('modal_tomas/S3', 2.8), ('modal_tomas/S2', 2.6)]
FIESTA = [('modal_v4/V1_heroe', 1.6), ('modal_v4/V2_pista', 1.6), ('modal_v4/V3_xv', 1.6), ('modal_v4/V5_robot', 1.6), ('modal_v4/V6_familia', 1.6), ('modal_v4/V8_detalle', 2.2)]
XF, CIERRE = 0.45, 3.2
V9 = AQUI / 'final' / 'XV_reel_v9_endcard_hunabku.mp4'


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    ent, fl = [], ''
    norm = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,setsar=1,format=yuv420p'
    for i, (n, d) in enumerate(TRANQ):
        ent += ['-i', str(AQUI / f'{n}.mp4')]; fl += f'[{i}:v]{norm},trim=duration={d + XF},setpts=PTS-STARTPTS,fps=30,settb=AVTB[t{i}];'
    prev, acum = 't0', TRANQ[0][1] + XF
    for i in range(1, len(TRANQ)):
        off = acum - XF; fl += f'[{prev}][t{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}];'; prev = f'x{i}'; acum = off + TRANQ[i][1] + XF
    T_TRANQ = acum
    k = len(TRANQ)
    for j, (n, d) in enumerate(FIESTA):
        ent += ['-ss', '0.8', '-i', str(AQUI / f'{n}.mp4')]; fl += f'[{k + j}:v]{norm},trim=duration={d},setpts=PTS-STARTPTS,fps=30,settb=AVTB[f{j}];'
    k2 = k + len(FIESTA)
    ent += ['-sseof', f'-{CIERRE}', '-i', str(V9)]
    fl += f'[{k2}:v]{norm},trim=duration={CIERRE},setpts=PTS-STARTPTS,fps=30,settb=AVTB[cie];'
    fl += f'[{prev}]' + ''.join(f'[f{j}]' for j in range(len(FIESTA))) + f'[cie]concat=n={len(FIESTA) + 2}:v=1:a=0[v];'
    T_FIESTA = sum(d for _, d in FIESTA); TOTAL = T_TRANQ + T_FIESTA + CIERRE
    ent += ['-i', str(AQUI / 'musica_suave_s7.wav'), '-i', str(AQUI / 'final' / 'XV_reel_v6_fiesta.mp4')]
    a1, a2 = k2 + 1, k2 + 2
    fl += (f'[{a1}:a]aresample=44100,atrim=0:{T_TRANQ + 0.6:.2f},afade=t=in:st=0:d=0.8,afade=t=out:st={T_TRANQ - 0.6:.2f}:d=1.2,volume=0.9[m1];'
           f'[{a2}:a]aresample=44100,atrim=start=6,asetpts=PTS-STARTPTS,atrim=0:{T_FIESTA + CIERRE + 0.5:.2f},afade=t=in:st=0:d=0.4,afade=t=out:st={T_FIESTA + CIERRE - 1.2:.2f}:d=1.2,'
           f'adelay={int((T_TRANQ - 0.6) * 1000)}|{int((T_TRANQ - 0.6) * 1000)}[m2];[m1][m2]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]')
    sal = AQUI / 'final' / 'XV_reel_v10_tranquilas_fiesta.mp4'
    ff(ent + ['-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-vf' if False else '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
              '-crf', '21', '-preset', 'slow', '-s', '720x1280', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
