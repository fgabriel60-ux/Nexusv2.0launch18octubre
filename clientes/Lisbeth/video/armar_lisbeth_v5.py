"""Lisbeth v5: gancho frente a SU terreno real → la cámara sube como dron y ahí mismo empieza su narración («Así empieza tu patrimonio…», ya sin
«Hola, soy Lisbeth») → la construcción sobre SU terreno nuevo reemplaza la de la v22 (terreno viejo) → su vista real a las montañas → sigue la v22 desde el
mapa con los pines (Tecnológico, central, hospital, aeropuerto, presa), documentos y cierre, tal cual. Whoosh en la subida y golpe suave al construir.
Uso: python3 armar_lisbeth_v5.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
import armar_xv
from armar_xv import tex

AQUI = Path(__file__).resolve().parent
V3 = AQUI / 'v3'
V22 = AQUI.parent / 'referencia' / 'v22.mp4'
PAN = AQUI.parent / 'whatsapp' / 'nuevas_1024' / '24_130401_video.mp4'
SFX = AQUI.parents[1] / 'Guillermo' / 'video' / 'sfx'
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/lisbeth_v5'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 720, 1280
D_HABLA, VEL = 4.7, 1.5
SIN_HOLA = 1.64          # en la v22, «Así empieza…» arranca aquí
V22_MAPA = 10.0          # en la v22, el mapa con los pines empieza aquí
D_SUBE = 4.0 / VEL
D_CONS = 4.0
D_PAN = V22_MAPA - SIN_HOLA - D_SUBE - D_CONS   # lo que falta de narración hasta el mapa


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    armar_xv.W, armar_xv.H = W, H
    tex(['TOMATLÁN, JALISCO', 'TERRENO REAL'], TMP / 't0.png', 900, tam=56)
    tex(['TERRENOS DESDE', '300 M² · VISTA A LAS MONTAÑAS'], TMP / 't1.png', 900, tam=56)
    tex(['A 20 MINUTOS', 'DE LA PLAYA'], TMP / 't2.png', 900, tam=56)
    AJ = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps=30,setsar=1,format=yuv420p'
    T1 = D_HABLA; T2 = T1 + D_SUBE; T3 = T2 + D_CONS
    fl = (f"[0:v]{AJ},tpad=stop_mode=clone:stop_duration=1,trim=duration={D_HABLA},setpts=PTS-STARTPTS[h0];[h0][5:v]overlay=0:0:enable='between(t,0.2,{D_HABLA - 0.1})'[h];"
          f"[1:v]{AJ},setpts=PTS/{VEL}[s];"
          f"[2:v]{AJ},trim=duration={D_CONS},setpts=PTS-STARTPTS[k0];[k0][6:v]overlay=0:0:enable='between(t,0.3,{D_CONS})'[k];"
          f"[3:v]{AJ},eq=contrast=1.06:saturation=1.15,tpad=stop_mode=clone:stop_duration=2,trim=duration={D_PAN:.2f},setpts=PTS-STARTPTS[p0];[p0][7:v]overlay=0:0[p];"
          f"[4:v]{AJ},trim=start={V22_MAPA},setpts=PTS-STARTPTS[m];[h][s][k][p][m]concat=n=5:v=1:a=0[v];"
          # audio: su voz del gancho con música suave → desde la subida, la narración de la v22 sin el «Hola, soy Lisbeth»; whoosh y golpe encima
          f"[8:a]aresample=44100,apad=whole_dur={D_HABLA}[g];[9:a]aresample=44100,volume=0.2,atrim=0:{D_HABLA},afade=t=out:st={D_HABLA - 0.5}:d=0.5[mu];"
          f"[g][mu]amix=inputs=2:duration=longest:normalize=0,atrim=0:{D_HABLA}[p1];[4:a]aresample=44100,atrim=start={SIN_HOLA},asetpts=PTS-STARTPTS[p2];"
          f"[p1][p2]concat=n=2:v=0:a=1[nar];[10:a]aresample=44100,volume=0.7,adelay={int(T1 * 1000) - 150}|{int(T1 * 1000) - 150}[wh];"
          f"[11:a]aresample=44100,volume=0.35,adelay={int(T2 * 1000)}|{int(T2 * 1000)}[bo];[nar][wh][bo]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    sal = AQUI / 'Lisbeth_v5_terreno_nuevo.mp4'
    ff(['-i', str(V3 / 'LIS3_habla.mp4'), '-i', str(V3 / 'LIS3_sube_v.mp4'), '-i', str(V3 / 'LIS3_construye_v.mp4'), '-i', str(PAN), '-i', str(V22),
        '-loop', '1', '-t', str(D_HABLA), '-i', str(TMP / 't0.png'), '-loop', '1', '-t', str(D_CONS), '-i', str(TMP / 't1.png'),
        '-loop', '1', '-t', f'{D_PAN:.2f}', '-i', str(TMP / 't2.png'),
        '-i', str(AQUI / 'voz' / 'L_gancho.mp3'), '-i', str(MUSICA), '-i', str(SFX / 'whoosh.wav'), '-i', str(SFX / 'boom.wav'),
        '-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'pan {D_PAN:.2f}s')


if __name__ == '__main__':
    main()
