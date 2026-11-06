"""Baja los 4 reels de cada cliente/prospecto, arma una hoja (fila = idea, 4 cuadros) y el lote para que Glimmer escoja las 2 mejores ideas por cliente."""
import io, json, os, re, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont
ideas = json.load(open('ideas.json')); os.makedirs('v', exist_ok=True); F = ImageFont.load_default(28)
CTX = {'Guillermo · herrería': 'Herrero en Puebla: zaguanes, cortinas, puertas y pérgolas; ya tiene video Pixar y videos de proceso de techo.',
       'José · impermeabilización': 'Grupo JR, impermeabilización de azoteas en Puebla, poliuretano acrílico 12 años, desde $150/m²; ya tiene video Pixar de obrero.',
       'Giovanni · abogado divorcios': 'Abogado en Los Cabos, divorcio voluntario desde $20,000, trámite en línea; ya tiene video hablando a cámara.',
       'Víctor · limpieza empresas': 'Servilin, limpieza para empresas (no vacantes); ya tiene videos con alerta «no es oferta de empleo».',
       'BD Pro · pistas de baile': 'Renta de pistas de baile iluminadas en Monterrey; ya tiene video antes/después.',
       'Manuel · fotografía XV': 'Fotógrafo de XV años (Hunab Ku); ya tiene reel musical.',
       'Lisbeth · terrenos': 'Venta de 34 lotes en Tomatlán, Jalisco; ya tiene video de ella frente al terreno.',
       'Alberto · dental': 'Veneers Dental Nogales, Dra. Ángeles; implante desde $12,500; ya tiene reel de implantes con la doctora.',
       'Fernando · punto de venta': 'Anegocios, kit de punto de venta $3,500; ya tiene video de capacitación.',
       'Mariano · casas': 'Casas en Vizcaíno Residencial, Rosarito; ya tiene recorridos y gancho Spider-Man.',
       'Israel · pantallas LED': 'SIRLed, venta, instalación y reparación de pantallas LED para negocios; ya tiene video con sus tomas.',
       'Iván · fumigación': 'Fumicam, fumigación; ya tiene videos con su voz.',
       'Uriel · consultor': 'Consultor de procesos para dueños de negocio; ya tiene gancho con su cara.',
       'Rubén · quiropráctico': 'Alineación alphabiótica, $300 la sesión, Zinacantepec/Metepec; prospecto.',
       'Rachel · micropigmentación': 'Clou SPA, micropigmentación en Mexicali; prospecto.',
       'Verónica · inmobiliaria': 'Asesora inmobiliaria, Torre El Charro, Tampico; prospecto.',
       'Generadores · plantas de luz': 'Energy Controlled, generadores/plantas de luz; quiere ventas, no imágenes; prospecto.',
       'Blanca · terapia de lenguaje': 'Terapia de lenguaje para niños (Hablar…Hablando); prospecto.',
       'Mariachi': 'Mariachi en Guadalajara: serenatas, XV, eventos; prospecto.'}
def cuadro(v, t):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', v, '-frames:v', '1', '-vf', 'scale=270:480:force_original_aspect_ratio=decrease,pad=270:480:(ow-iw)/2:(oh-ih)/2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    return Image.open(io.BytesIO(b)) if b else Image.new('RGB', (270, 480))
lote = []
for n, d in ideas.items():
    slug = re.sub(r'\W+', '_', n.split(' ·')[0]).strip('_'); filas = []
    for k, x in enumerate(d['ideas'], 1):
        v = f'v/{slug}_{k}.mp4'
        try:
            if not os.path.exists(v): open(v, 'wb').write(urllib.request.urlopen(x['video'], timeout=120).read())
            du = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout or 1)
        except Exception as e:
            print('falla', v, e); continue
        x['local'] = v; x['duracion'] = round(du)
        H = Image.new('RGB', (1080, 480)); [H.paste(cuadro(v, du * f), (i * 270, 0)) for i, f in enumerate((.1, .35, .6, .9))]
        ImageDraw.Draw(H).text((8, 6), f'IDEA {k}', fill='yellow', stroke_width=3, stroke_fill='black', font=F); filas.append(H)
    S = Image.new('RGB', (1080, 480 * len(filas))); [S.paste(f, (0, i * 480)) for i, f in enumerate(filas)]; S.save(f'{slug}_hoja.jpg', quality=82)
    lista = '\n'.join(f"IDEA {k}: @{x['cuenta']} · {(x['vistas'] or 0):,} vistas · texto: {x['texto'][:150].replace(chr(10), ' ')}" for k, x in enumerate(d['ideas'], 1))
    lote.append({'nombre': slug, 'fotos': [os.path.abspath(f'{slug}_hoja.jpg')], 'prompt': f"""Eres estratega de anuncios de Meta y director de video para negocios en México. Da SOLO la respuesta final en español, breve, sin razonamiento.
NEGOCIO: {CTX.get(n, n)}
Estas son 4 ideas de reels de Instagram de su nicho (imagen: cada fila es una idea, 4 cuadros del inicio al final):
{lista}
Escoge las 2 MEJORES ideas para hacerle un video NUEVO a este negocio (si alguna no tiene que ver con su negocio, descártala). Responde EXACTAMENTE así:
ELEGIDAS: X y Y
IDEA X: (1 línea: por qué sirve) | ADAPTACIÓN: (1 línea: cómo la hacemos con sus fotos/voz o escenas generadas)
IDEA Y: (1 línea: por qué sirve) | ADAPTACIÓN: (1 línea)
CALIFICACIÓN PROYECTADA: X/10"""})
    print(n, len(filas), flush=True)
json.dump(ideas, open('ideas.json', 'w'), ensure_ascii=False, indent=1)
json.dump(lote, open('lote.json', 'w'), ensure_ascii=False, indent=1)
