"""Estáticos 4:5 actualizados (13 oct): Jesús (Meta), Marcos (Ortega) y Omar (logo + RIR)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
NEG = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NOR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1080, 1350
VERDE_WA = (37, 211, 102)


def cubrir(ruta, dy=0.3):
    im = Image.open(ruta).convert('RGB')
    esc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x = (im.width - W) // 2; y = int((im.height - H) * dy)
    return im.crop((x, y, x + W, y + H))


def velo(img, color, arriba=(0, 560), abajo=(880, H), a1=225, a2=245):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for y in range(*arriba):
        d.line([(0, y), (W, y)], fill=(*color, int(a1 * (1 - (y - arriba[0]) / (arriba[1] - arriba[0])))))
    for y in range(*abajo):
        d.line([(0, y), (W, y)], fill=(*color, int(a2 * (y - abajo[0]) / (abajo[1] - abajo[0]))))
    return Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')


def ajus(d, t, fuente, ancho, tam):
    while d.textlength(t, font=ImageFont.truetype(fuente, tam)) > ancho:
        tam -= 2
    return ImageFont.truetype(fuente, tam)


def bloque(d, lineas, y, tam, color, fuente=NEG, centrado=True):
    for l in lineas:
        f = ajus(d, l, fuente, W - 120, tam)
        x = (W - d.textlength(l, font=f)) / 2 if centrado else 60
        d.text((x, y), l, font=f, fill=color, stroke_width=2 if fuente == NEG else 0, stroke_fill=(0, 0, 0))
        y += int(f.size * 1.2)
    return y


def boton(d, texto, y=H - 150):
    f = ajus(d, texto, NEG, W - 220, 46)
    a = d.textlength(texto, font=f) + 100
    d.rounded_rectangle(((W - a) / 2, y, (W + a) / 2, y + 100), 50, fill=VERDE_WA)
    d.text(((W - a) / 2 + 50, y + 24), texto, font=f, fill=(255, 255, 255))


def pieza(foto, dy, color, arriba, sub, boton_txt, salida, extra=None, logo=None):
    img = velo(cubrir(foto, dy), color)
    if logo is not None:
        img.paste(logo, ((W - logo.width) // 2, 40), logo if logo.mode == 'RGBA' else None)
    d = ImageDraw.Draw(img)
    y = bloque(d, arriba, 170 if logo is not None else 90, 62 if logo is not None else 74, (255, 255, 255))
    y = bloque(d, sub, max(y + 10, 1030), 42, (255, 225, 140), NEG)
    if extra:
        bloque(d, extra, y + 6, 32, (235, 235, 235), NOR)
    boton(d, boton_txt)
    img.save(AQUI / salida, quality=92)
    print(salida)


# --- Jesús · Rar~Amore (lenguaje aprobado por Meta) ---
J = E / '360salud_cartilago_20261013' / 'cuadros'
VJ = (8, 30, 20)
pieza(J / 'J5.png', 0.2, VJ, ['MANTÉN TU RITMO', 'TODOS LOS DÍAS'], ['Rar~Amore · Apoya la nutrición de tus articulaciones'],
      'Pide por WhatsApp 81 8466 8456', 'Jesus_RarAmore_1.jpg', ['Colágeno · Magnesio · Calcio · Vitamina D · Envíos a todo México'])
pieza(J / 'J3.png', 0.3, VJ, ['NUTRICIÓN DIARIA', 'PARA TUS ARTICULACIONES'], ['Colágeno, boswelia, magnesio y vitamina D'],
      'Pide por WhatsApp 81 8466 8456', 'Jesus_RarAmore_2.jpg', ['Suplemento alimenticio · 2 cápsulas al día'])
pieza(E / '360salud_videos_20261012' / 'imagenes' / 'jesus' / 'C4.png', 0.3, VJ, ['PROMOCIÓN', 'POR TIEMPO LIMITADO'],
      ['Cápsulas $1,392 · Bálsamo $895 · Dúo precio especial'], 'Pide por WhatsApp 81 8466 8456', 'Jesus_RarAmore_3.jpg',
      ['Envíos a todo México'])

# --- Marcos · Ortega ---
M = E / 'marcos_ortega_20261012' / 'v_chica' / 'cuadros'
VM = (10, 20, 48)
pieza(M / 'K1.png', 0.2, VM, ['¿TE QUEDASTE', 'SIN TRABAJO?'], ['Tu Afore te puede dar hasta $35,192'],
      'Escríbenos por WhatsApp', 'Marcos_Ortega_1.jpg', ['Soluciones Previsionales Ortega · Asesoría sin costo'])
pieza(M / 'K2.png', 0.2, VM, ['SIN ANTICIPOS'], ['Pagas cuando recibes tu dinero'], 'Escríbenos por WhatsApp',
      'Marcos_Ortega_2.jpg', ['Desempleo · Negativas de pensión · RFC · Semanas cotizadas · Mejoravit'])
pieza(M / 'K3.png', 0.2, VM, ['NO ESTÁS SOLO'], ['Te acompañamos en todo tu trámite'], 'Escríbenos por WhatsApp',
      'Marcos_Ortega_3.jpg', ['Estrategias 100% legales · Atención personalizada'])

# --- Omar · Red Natura (logo + RIR) ---
O = E / 'omar_20261013'
logo = Image.open(O / 'refs' / 'logo_blanco.png').convert('RGBA')
logo = logo.resize((360, int(logo.height * 360 / logo.width)), Image.LANCZOS)
VO = (12, 40, 100)
for i, (foto, dy, arriba, sub, extra) in enumerate([
        (O / 'omar_foto.jpg', 0.0, ['¿CONOCES EL', 'MULTINIVEL?'], ['Tu libertad financiera puede empezar hoy'], None),
        (O / 'cuadros' / 'O1_logo.png', 0.0, ['+50 PRODUCTOS', 'PARA TODA LA FAMILIA'], ['Control de peso · Detox · Nutrición'], None),
        (O / 'cuadros' / 'O2_logo.png', 0.2, ['ÚNETE A', 'MI EQUIPO'], ['Te explico paso a paso cómo empezar'], None)], 1):
    pieza(foto, dy, VO, arriba, sub, 'WhatsApp 56 5587 4031', f'Omar_RedNatura_{i}.jpg',
          ['Omar · Distribuidor independiente · RIR 225430'], logo)
