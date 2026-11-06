"""Víctor · Servilin v5 (30 oct, cambios de Glimmer 6-7 → 8+): sin GPU, sobre los finales v4_empresas.
1) Los primeros 2.1 s (pantalla oscura con solo texto) se cambian por una toma en movimiento del mismo video, con el aviso «SOLO EMPRESAS · NO ES VACANTE» en la esquina.
2) La tarjeta final estática (~8 s) lleva un acercamiento lento. El audio no se toca."""
import subprocess, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent; V = AQUI.parent
# video: (segundo de la toma en movimiento para la apertura, inicio de la tarjeta final)
CASOS = {'servilin_obra_fina_v4_empresas': (9.7, 25.6), 'servilin_v1_v4_empresas': (6.0, 24.7), 'servilin_v2_v4_empresas': (6.0, 24.7)}
A = 2.1


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-1200:])


for n, (broll, tarj) in CASOS.items():
    src = V / f'{n}.mp4'; out = AQUI / f'{n.replace("_v4_", "_v5_")}.mp4'
    ff(['-i', str(src), '-i', str(AQUI / 'aviso_720.png'), '-filter_complex',
        f"[0:v]trim={broll}:{broll + A},setpts=PTS-STARTPTS,scale=792:1408,crop=720:1280,fps=25[a0];[a0][1:v]overlay=0:0[a];"
        f"[0:v]trim={A}:{tarj},setpts=PTS-STARTPTS[b];"
        f"[0:v]trim={tarj},setpts=PTS-STARTPTS,scale=iw*2:ih*2,zoompan=z='min(1+on*0.0012,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=25[c];"
        "[a][b][c]concat=n=3:v=1:a=0[v]", '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-profile:v', 'main', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', str(out)])
    print(out.name)
