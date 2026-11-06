"""Lisbeth v3 sin teléfono volando: ella a la orilla de la carretera frente a SU terreno real dice el gancho con su voz → la cámara sube como dron hasta SU
foto aérea real → las casas aparecen sobre ese mismo terreno (rotulado como visualización) → sigue su v22 completa. Uso: python3 armar_lisbeth_v3.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
import armar_xv
from armar_xv import tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/lisbeth_v3'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 720, 1280
D_HABLA, VEL, D_CONS = 4.7, 1.5, 4.0


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    armar_xv.W, armar_xv.H = W, H   # textos al tamaño de este video
    tex(['TOMATLÁN, JALISCO', 'TERRENO REAL'], TMP / 't0.png', 900, tam=56)
    tex(['ASÍ PODRÍA VERSE', 'VISUALIZACIÓN'], TMP / 't1.png', 900, tam=56)
    v3 = AQUI / 'v3'; sal = AQUI / 'Lisbeth_v3_terreno_real.mp4'
    fl = (f"[0:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={D_HABLA},setpts=PTS-STARTPTS[a0];"
          f"[a0][5:v]overlay=0:0:enable='between(t,0.2,{D_HABLA - 0.1})'[a];"
          f"[1:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,setpts=PTS/{VEL}[s];"
          f"[2:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,trim=duration={D_CONS},setpts=PTS-STARTPTS[k0];[k0][6:v]overlay=0:0:enable='between(t,0.8,{D_CONS})'[k];"
          f"[3:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[c];[a][s][k][c]concat=n=4:v=1:a=0[v];"
          f"[4:a]aresample=44100,apad=whole_dur={D_HABLA}[va];[1:a]aresample=44100,atempo={VEL}[sa];[2:a]aresample=44100,atrim=0:{D_CONS},volume=0.6[ka];"
          f"[3:a]aresample=44100[ca];[va][sa][ka][ca]concat=n=4:v=0:a=1,loudnorm=I=-14:TP=-1.5[aud]")
    ff(['-i', str(v3 / 'LIS3_habla.mp4'), '-i', str(v3 / 'LIS3_sube_v.mp4'), '-i', str(v3 / 'LIS3_construye_v.mp4'), '-i', str(AQUI.parent / 'referencia' / 'v22.mp4'),
        '-i', str(AQUI / 'voz' / 'L_gancho.mp3'), '-loop', '1', '-t', str(D_HABLA), '-i', str(TMP / 't0.png'), '-loop', '1', '-t', str(D_CONS), '-i', str(TMP / 't1.png'),
        '-filter_complex', fl, '-map', '[v]', '-map', '[aud]', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
