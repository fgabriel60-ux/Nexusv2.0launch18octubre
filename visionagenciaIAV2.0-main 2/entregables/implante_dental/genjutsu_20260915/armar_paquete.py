"""Arma el paquete para Genjutsu cuando termina el render de movimiento: 2 tramos de ≤30 s con 1 s encimado,
imágenes numeradas por tramo, prompts, voz y un ZIP por tramo. Uso: python3 armar_paquete.py"""
import shutil, subprocess, time, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VIDEO = AQUI / 'MOVIMIENTO_COMPLETO_0001-1050.mp4'
IMG = AQUI / 'IMAGENES'
VOZ = AQUI.parent / 'voz_fish' / 'IMPLANTE_VOZ_35s.mp3'
TRAMOS = {'A': (0, 18, ['01', '02', '03', '04', '05']), 'B': (17, 35, ['05', '06', '07', '08', '09', '10'])}

# Esperar a que Blender suelte el archivo (el log termina con "Blender quit")
while 'Blender quit' not in (AQUI / 'render_movimiento.log').read_text(errors='replace'):
    time.sleep(10)

dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(VIDEO)]))
print('video completo', round(dur, 2), 's')
montaje = AQUI / 'MONTAJE'; montaje.mkdir(exist_ok=True)
shutil.copy(VIDEO, montaje / 'RECORRIDO_BLENDER_COMPLETO_35s.mp4')
shutil.copy(VOZ, montaje / VOZ.name)

for letra, (ini, fin, nums) in TRAMOS.items():
    d = AQUI / ('TRAMO_' + letra); d.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ini), '-to', str(min(fin, dur)), '-i', str(VIDEO), '-an',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart',
                    str(d / ('00_VIDEO_TRAMO_%s.mp4' % letra))], check=True)
    for n in nums:
        src = next(IMG.glob(n + '_*.png'))
        shutil.copy(src, d / src.name)
    shutil.copy(AQUI / ('PROMPT_TRAMO_%s.txt' % letra), d)
    with zipfile.ZipFile(AQUI / ('TRAMO_%s_IMAGENES.zip' % letra), 'w') as z:
        for f in sorted(d.glob('*.png')):
            z.write(f, f.name)
    print('tramo', letra, 'listo:', sorted(p.name for p in d.iterdir()))
