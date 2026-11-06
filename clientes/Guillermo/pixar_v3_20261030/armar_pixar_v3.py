"""v3 (30 oct): tomas de Carlos relipsync con su voz mejorada (mejores tomas de 4, pixar_v3_20261030); tomas de Guillermo de la v2. Arma el Pixar v2 de Guillermo: 8 clips H3 (salida/) + voz de cada frase + subtítulo por frase → Guillermo_Pixar_v2.mp4 (H.264 Main 720p)."""
import json, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont

AQUI = pathlib.Path(__file__).resolve().parent
V2 = AQUI.parent / 'pixar_v2_20261030'
RAIZ = AQUI.parents[2]
FUENTE = str(RAIZ / 'visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf')
TMP = AQUI / 'tmp_v3'; TMP.mkdir(exist_ok=True)
TEXTO = {
    'g_urge': 'Ya me urge volver a cotizar… ya quiero seguir agarrando',
    'c_1': 'Guillermo hace zaguanes, cortinas, puertas y pérgolas',
    'c_2': 'Le hicimos su estrategia, sus volantes y su primer video',
    'g_fregon': '¡Se ve muy, muy fregón, eh!',
    'c_3': 'Todo con sus fotos reales: esto se logra con inteligencia artificial',
    'g_mensaje': 'Quiero que me llegue el mensaje, cotizar y cerrar',
    'c_4': '4 videos al mes por $500',
    'c_5': 'Comenta el video y te mando el link de tu llamada gratis',
}


def ff(a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def sub(txt, ruta):
    im = Image.new('RGBA', (720, 1280)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FUENTE, 46); f.set_variation_by_name('Black') if hasattr(f, 'set_variation_by_name') else None
    lineas, l = [], ''
    for w in txt.upper().split():
        if d.textlength((l + ' ' + w).strip(), font=f) > 600: lineas.append(l); l = w
        else: l = (l + ' ' + w).strip()
    lineas.append(l)
    y = 1010 - 30 * (len(lineas) - 1)
    for ln in lineas:
        d.text((360, y), ln, font=f, fill='white', anchor='mm', stroke_width=6, stroke_fill='black'); y += 60
    im.save(ruta)


plan = json.load(open(V2 / 'plan.json'))
segs = []
for i, (n, c, p, s, fin, voz) in enumerate(plan['tomas']):
    wav = AQUI / 'voz' / f'{voz}.wav' if voz.startswith('c_') else RAIZ / 'clientes/Guillermo/obrero_20261029/voz' / f'{voz}.wav'
    t = dur(wav) + 0.25
    sub(TEXTO[voz], TMP / f's{i}.png')
    seg = TMP / f'seg{i}.mp4'
    ff(['-i', str((AQUI if voz.startswith('c_') else V2) / 'salida' / f'{n}.mp4'), '-i', str(wav), '-i', str(TMP / f's{i}.png'),
        '-filter_complex', f'[0:v]scale=720:1280,fps=30,tpad=stop_mode=clone:stop_duration=2[b];[b][2:v]overlay[v];[1:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]',
        '-map', '[v]', '-map', '[a]', '-t', f'{t:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '128k', str(seg)])
    segs.append(seg)
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
final = RAIZ / 'clientes/Guillermo/Guillermo_Pixar_v3_zaguanes.mp4'
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '23',
    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(final)])
print(final, round(dur(final), 1), 's', final.stat().st_size // 1024, 'KB')
