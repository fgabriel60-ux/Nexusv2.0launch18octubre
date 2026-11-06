"""Villa Bahía 3C · reel estilo referencia DM4A9JqzC1f (31 oct): ~24 cortes secos de 1 tiempo (115 bpm ≈ 0.52 s) con movimientos suaves
de gimbal, sin voz ni subtítulos, logo chico arriba, abre en la sala y cierra en el exterior con alberca. Música original MusicGen.
  python3 armar_ritmo.py [musica.wav] [version]"""
import subprocess, sys
from pathlib import Path
A = Path(__file__).parent; S1 = A / 'salida'; S2 = A / 'salida2'
MUS = sys.argv[1] if len(sys.argv) > 1 else str(A.parent / 'musica/villa_s3.wav'); V = sys.argv[2] if len(sys.argv) > 2 else 'v1'
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; N = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
B = 60 / 115   # un tiempo
# (clip, segundo de inicio, tiempos)
CORTES = [(S1 / 'VBT4_sala.mp4', .3, 2), (S2 / 'VCT05_sala.mp4', .2, 1), (S2 / 'VCT01_exterior.mp4', .2, 1), (S1 / 'VBT4_sala.mp4', 2.6, 1),
          (S2 / 'VCT06_sala2.mp4', .2, 1), (S1 / 'VBT3_balcon.mp4', .4, 1), (S1 / 'VBT3_balcon.mp4', 3.0, 1), (S2 / 'VCT04_comedor.mp4', .2, 1),
          (S1 / 'VBT5_cocina.mp4', .4, 1), (S1 / 'VBT5_cocina.mp4', 3.0, 1), (S2 / 'VCT05_sala.mp4', 1.6, 1), (S2 / 'VCT02_recamara.mp4', .2, 1),
          (S1 / 'VBT6_recamara.mp4', .4, 1), (S1 / 'VBT6_recamara.mp4', 3.2, 1), (S2 / 'VCT03_recamara_mar.mp4', .2, 1), (S2 / 'VCT07_recamara2.mp4', .2, 1),
          (S2 / 'VCT08_bano.mp4', .2, 1), (S2 / 'VCT08_bano.mp4', 1.4, 1), (S1 / 'VBT7_terraza.mp4', .4, 1), (S1 / 'VBT2_alberca.mp4', .4, 1),
          (S1 / 'VBT1_aereo.mp4', .4, 1), (S1 / 'VBT1_aereo.mp4', 3.0, 1), (S2 / 'VCT01_exterior.mp4', 1.2, 2)]
CORTES = [c for c in CORTES if c[0].exists()]
inp, fc = [], ''
for i, (clip, a, n) in enumerate(CORTES):
    inp += ['-ss', f'{a:.2f}', '-t', f'{n * B:.3f}', '-i', str(clip)]
    fc += f'[{i}:v]scale=720:1280,setsar=1,fps=30,trim=0:{n * B:.3f},setpts=PTS-STARTPTS[v{i}];'
k = len(CORTES); T = sum(n for _, _, n in CORTES) * B
fc += ''.join(f'[v{i}]' for i in range(k)) + f'concat=n={k}:v=1:a=0,'
fc += (f"drawtext=fontfile={F}:text='V I L L A   B A H Í A':fontsize=26:fontcolor=white@0.92:x=(w-text_w)/2:y=70:shadowcolor=black@0.35:shadowx=1:shadowy=1,"
       f"drawtext=fontfile={N}:text='S A N   C A R L O S  ·  S O N O R A':fontsize=13:fontcolor=white@0.85:x=(w-text_w)/2:y=104:shadowcolor=black@0.35:shadowx=1:shadowy=1[v];")
VOZ = A / 'voz'; INI = [0.4, 4.8, 9.1]
SUBS = ['Villa Bahía, en San Carlos', 'Vista al mar y al cerro Tetakawi', 'Balcón con terraza, sala de madera', 'cocina con barra y dos recámaras', 'Reserva tu fin de semana', 'por WhatsApp']
TS = [(0.4, 2.1), (2.1, 4.6), (4.8, 6.7), (6.7, 8.7), (9.1, 10.2), (10.2, 11.3)]
fc = fc.replace('[v];', ',' + ','.join(f"drawtext=fontfile={F}:text='{t}':fontsize=34:fontcolor=white:borderw=3:bordercolor=black@0.6:x=(w-text_w)/2:y=h*0.83:enable='between(t,{a},{b})'" for t, (a, b) in zip(SUBS, TS)) + '[v];')
voz = (VOZ / 'f0.wav').exists()
if voz:
    fc += ''.join(f'[{k + 1 + i}:a]adelay={int(INI[i] * 1000)}|{int(INI[i] * 1000)},volume=1.3[o{i}];' for i in range(3)) + '[o0][o1][o2]amix=inputs=3:normalize=0[vo];'
    fc += f'[{k}:a]atrim=0:{T:.3f},volume=0.35,afade=t=in:d=0.2,afade=t=out:st={T - 0.8:.3f}:d=0.8[m];[m][vo]amix=inputs=2:normalize=0:duration=first[a]'
else:
    fc += f'[{k}:a]atrim=0:{T:.3f},afade=t=in:d=0.2,afade=t=out:st={T - 0.8:.3f}:d=0.8[a]'
out = A.parent / f'VillaBahia3C_ritmo_{V}.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-i', MUS] + (sum([['-i', str(VOZ / f'f{i}.wav')] for i in range(3)], []) if voz else []) + ['-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '19',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)], check=True)
print('listo', out, round(T, 1), 's,', k, 'cortes')
