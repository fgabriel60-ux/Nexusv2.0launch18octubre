"""Recorridos premium plan B San Carlos (31 oct): gancho movido (1ª toma acelerada + zoom + whoosh) y luego escenas largas de gimbal; logo chico y CTA."""
import subprocess
from pathlib import Path
A = Path(__file__).parent; S = A / 'salida'
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; N = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
MUS = str(A.parent / 'musica/villa_s11.wav'); WH = '/workspaces/Nexusv2.0launch18octubre/clientes/Guillermo/video/sfx/whoosh.wav'
CASAS = {'VillaBahia4C': ('V I L L A   B A H Í A   4 C', [('4C1_aereo', 'Frente al Mar de Cortés'), ('4C2_alberca', 'Alberca entre palmeras'), ('4C3_sala', 'Sala con vista al mar'),
                                                        ('4C4_cocina', 'Cocina y comedor'), ('4C5_recamara', 'Recámaras amplias'), ('4C6_bano', 'Baño completo')]),
         'CaracolPeninsula506': ('C A R A C O L   P E N Í N S U L A', [('CP2_atardecer', 'Atardeceres desde tu terraza'), ('CP1_fachada', 'Villa en Península, San Carlos'), ('CP3_terraza', 'Terraza con vista a la bahía'),
                                                        ('CP4_vestibulo', 'Arcos y talavera'), ('CP5_sala', 'Sala con ventanales'), ('CP6_cocina', 'Cocina con isla'), ('CP7_recamara', 'Recámara principal')])}
for nombre, (logo, tomas) in CASAS.items():
    inp, fc, D = [], '', []
    for i, (t, txt) in enumerate(tomas):
        vel, d = (1.8, 1.8) if i == 0 else (1.0, 2.5)
        inp += ['-ss', '0.1', '-t', f'{d * vel + .1}', '-i', str(S / f'{t}_v.mp4')]; D.append(d)
        z = ",zoompan=z='1+0.006*on':d=1:s=720x1280:fps=30" if i == 0 else ''
        fc += f"[{i}:v]setpts=PTS/{vel},scale=720:1280,setsar=1,fps=30{z},trim=0:{d},setpts=PTS-STARTPTS,drawtext=fontfile={F}:text='{txt}':fontsize={min(40, int(1000 / len(txt)))}:fontcolor=white:borderw=4:bordercolor=black@0.6:x=(w-text_w)/2:y=h*0.80[v{i}];"
    k = len(tomas); T = sum(D)
    fc += ''.join(f'[v{i}]' for i in range(k)) + f'concat=n={k}:v=1:a=0,'
    fc += (f"drawtext=fontfile={F}:text='{logo}':fontsize=24:fontcolor=white@0.92:x=(w-text_w)/2:y=70:shadowcolor=black@0.4:shadowx=1:shadowy=1,"
           f"drawtext=fontfile={N}:text='S A N   C A R L O S  ·  S O N O R A':fontsize=13:fontcolor=white@0.85:x=(w-text_w)/2:y=102,"
           f"drawtext=fontfile={F}:text='Reserva tu fin de semana':fontsize=34:fontcolor=white:box=1:boxcolor=0x1a7f37@0.9:boxborderw=14:x=(w-text_w)/2:y=h*0.68:enable='gte(t,{T - 2.5})',"
           f"drawtext=fontfile={F}:text='Escribe por WhatsApp':fontsize=30:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.68+70:enable='gte(t,{T - 2.5})'[v];")
    fc += f"[{k}:a]atrim=0:{T},afade=t=out:st={T - 0.8}:d=0.8[m];[{k + 1}:a]volume=0.7[w];[m][w]amix=inputs=2:normalize=0:duration=first[a]"
    out = A.parent / f'{nombre}_recorrido_v1.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-i', MUS, '-i', WH, '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(out)], check=True)
    print('listo', out, round(T, 1))
