"""Lisbeth v7 (gancho Kelsie + subs virales): gancho con la calidad de la referencia de la realtor del golf (ella de cuerpo completo SOBRE su terreno, moviendo las manos, labios con su voz)
y subtítulos palabra por palabra → la cámara sube y ahí empieza su narración (sin «Hola, soy Lisbeth») → la construcción sobre SU terreno nuevo (sin el clip
de terreno que se había colado) → su v22 desde el mapa, ya corregida (hospital a un lado del Tecnológico). Uso: python3 armar_lisbeth_v6.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
import imageio_ffmpeg
import armar_xv
from armar_xv import tex
from kinetic import palabras
import subs_virales

AQUI = Path(__file__).resolve().parent
V3, V6 = AQUI / 'v3', AQUI / 'v7'
V22 = AQUI.parent / 'referencia' / 'v22_corregido.mp4'
SFX = AQUI.parents[1] / 'Guillermo' / 'video' / 'sfx'
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/22fc94f1-5b92-44e4-9296-5a2e47cda3a3/scratchpad/lisbeth_v7'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 720, 1280
D_HABLA, VEL = 4.7, 1.5
SIN_HOLA, V22_MAPA = 1.64, 10.0
D_SUBE = 4.0 / VEL
CORTE, SALTO = 4.3, 0.45   # el brazo sube UNA sola vez: se corta «habla» antes de que lo levante y «sube» entra ya con el brazo subiendo
GANCHO = 'Tomatlán no es promesa, es terreno real. ¡Míralo desde arriba!'
D_CONS = V22_MAPA - SIN_HOLA - D_SUBE   # la construcción llena hasta que empieza el mapa (se congela al final)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    armar_xv.W, armar_xv.H = W, H
    (TMP / 'k').mkdir(exist_ok=True)
    subs = subs_virales.capas(palabras(AQUI / 'voz' / 'L_gancho.wav', GANCHO), TMP / 'sv', y=0.74, W=W, H=H)
    tex(['TERRENOS DESDE 300 M²', 'ASÍ PODRÍA VERSE · VISUALIZACIÓN'], TMP / 't1.png', 900, tam=50)
    tex(['A 20 MINUTOS', 'DE LA PLAYA'], TMP / 't2.png', 900, tam=56)
    AJ = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps=30,setsar=1,format=yuv420p'
    T1 = D_HABLA; T2 = T1 + D_SUBE; T_PLAYA = SIN_HOLA + D_SUBE + D_CONS - (10.0 - 8.04)   # «a 20 minutos de la playa» empieza en 8.04 de la v22
    fl = (f"[0:v]{AJ},tpad=stop_mode=clone:stop_duration=1,trim=duration={CORTE},setpts=PTS-STARTPTS[h];"
          f"[1:v]{AJ},trim=start={SALTO},setpts=(PTS-STARTPTS)/{VEL},trim=duration={D_SUBE + D_HABLA - CORTE:.3f}[s];"
          f"[2:v]{AJ},tpad=stop_mode=clone:stop_duration=4,trim=duration={D_CONS:.2f},setpts=PTS-STARTPTS[k0];"
          f"[k0][4:v]overlay=0:0:enable='between(t,0.3,{D_CONS - 1.96:.2f})'[k1];[k1][5:v]overlay=0:0:enable='between(t,{D_CONS - 1.96:.2f},{D_CONS:.2f})'[k];"
          f"[3:v]{AJ},trim=start={V22_MAPA},setpts=PTS-STARTPTS[m];[h][s][k][m]concat=n=4:v=1:a=0[base];")
    subs = [(p, a, min(z, D_HABLA)) for p, a, z in subs]
    ent_s, fl_s, cur = subs_virales.overlay(subs, 'base', 10, D_HABLA, rise=12)
    fl += fl_s
    fl += (f"[6:a]aresample=44100,apad=whole_dur={D_HABLA}[g];[7:a]aresample=44100,volume=0.2,atrim=0:{D_HABLA},afade=t=out:st={D_HABLA - 0.5}:d=0.5[mu];"
           f"[g][mu]amix=inputs=2:duration=longest:normalize=0,atrim=0:{D_HABLA}[p1];[3:a]aresample=44100,atrim=start={SIN_HOLA},asetpts=PTS-STARTPTS[p2];"
           f"[p1][p2]concat=n=2:v=0:a=1[nar];[8:a]aresample=44100,volume=0.7,adelay={int(T1 * 1000) - 150}|{int(T1 * 1000) - 150}[wh];"
           f"[9:a]aresample=44100,volume=0.35,adelay={int(T2 * 1000)}|{int(T2 * 1000)}[bo];[nar][wh][bo]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    sal = AQUI / 'Lisbeth_v7b_un_solo_brazo.mp4'
    ff(['-i', str(V6 / 'L7_habla.mp4'), '-i', str(V6 / 'L7_sube.mp4'), '-i', str(V3 / 'LIS3_construye_v.mp4'), '-i', str(V22),
        '-loop', '1', '-t', f'{D_CONS:.2f}', '-i', str(TMP / 't1.png'), '-loop', '1', '-t', f'{D_CONS:.2f}', '-i', str(TMP / 't2.png'),
        '-i', str(AQUI / 'voz' / 'L_gancho.mp3'), '-i', str(MUSICA), '-i', str(SFX / 'whoosh.wav'), '-i', str(SFX / 'boom.wav')]
       + ent_s +
       ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'construcción {D_CONS:.2f}s')


if __name__ == '__main__':
    main()
