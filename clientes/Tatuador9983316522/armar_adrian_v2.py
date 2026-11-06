"""Adrián (tatuador Cancún) · v2 del video que él grabó el 3 nov (pedido de Carlos, 4 nov 2026).

Glimmer calificó el original 6/10 → 8/10 con estos cambios, todos de edición (no vuelve a grabar):
  Gancho 5→8    · tarjeta con precio y referencia de ubicación en los primeros segundos
  Oferta 4→8    · «Sesiones desde $1,000 · Diseño único y personalizado» sobre el plano del tatuaje
  Claridad 7→9  · el cierre mandaba al DM de Instagram y la campaña es a WhatsApp: se tapa y se pone el número
  Confianza 7→8 · se repite su propia frase real («las citas se agendan con anticipación»), sin inventar prueba social
  Calidad visual· acercamiento suave sobre el plano del tatuaje

Uso: python3 clientes/Tatuador9983316522/armar_adrian_v2.py
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

R = Path('/workspaces/Nexusv2.0launch18octubre')
A = R / 'clientes/Tatuador9983316522'
ORIG = A / 'whatsapp/del_cliente/20261103_144218_video_91A5CB79.mp4'
D = A / 'v2_20261104'; T = D / 'tmp'; T.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W, H = 1080, 1920
TEL = '998 331 6522'


def tarjeta(nombre, lineas, ancho=W, pad=26, fondo=(0, 0, 0, 205), colores=None, tam=58):
    """Bloque de texto centrado sobre fondo oscuro, como PNG con transparencia."""
    colores = colores or ['white'] * len(lineas)
    f = ImageFont.truetype(FB, tam)
    fs = [ImageFont.truetype(FB, tam if i == 0 else int(tam * .78)) for i in range(len(lineas))]
    alto = pad * 2 + sum(int(ff.size * 1.32) for ff in fs)
    im = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, ancho - 1, alto - 1], radius=26, fill=fondo)
    y = pad
    for t, ff, col in zip(lineas, fs, colores):
        while d.textlength(t, font=ff) > ancho - 48:
            ff = ImageFont.truetype(FB, ff.size - 2)
        d.text(((ancho - d.textlength(t, font=ff)) / 2, y), t, font=ff, fill=col,
               stroke_width=3, stroke_fill='black')
        y += int(ff.size * 1.32)
    p = T / f'{nombre}.png'; im.save(p); return p, alto


def main():
    gancho, h1 = tarjeta('gancho', ['TATUAJES EN CANCÚN CENTRO',
                                    'Frente al Palacio Municipal'],
                         ancho=W - 80, tam=62, colores=['white', (255, 214, 0)])
    oferta, h2 = tarjeta('oferta', ['SESIONES DESDE $1,000',
                                    'Diseño único y personalizado'],
                         ancho=W - 80, tam=60, colores=[(255, 214, 0), 'white'])
    anticip, h3 = tarjeta('anticip', ['Las citas se agendan con anticipación'],
                          ancho=W - 120, tam=48)
    cierre, h4 = tarjeta('cierre', [f'WhatsApp {TEL}', 'Escribe «CITAS» y te aparto lugar'],
                         ancho=W, tam=64, colores=['white', (120, 255, 180)], fondo=(0, 0, 0, 235), pad=34)

    # El cierre original lleva quemado «AGENDA AL DM @adrian.santanaink»: se tapa con una
    # banda opaca del mismo alto antes de poner el CTA de WhatsApp.
    tapa = Image.new('RGBA', (W, 400), (8, 8, 10, 255)); tapa.save(T / 'tapa.png')

    ent = ['-i', str(ORIG),
           '-loop', '1', '-i', str(gancho),      # 1
           '-loop', '1', '-i', str(oferta),      # 2
           '-loop', '1', '-i', str(anticip),     # 3
           '-loop', '1', '-i', str(T / 'tapa.png'),  # 4
           '-loop', '1', '-i', str(cierre)]      # 5

    # Sin acercamiento: zoompan sobre 1080x1920 se llevó 45 min en el sandbox y es el arreglo
    # de menos peso (Calidad visual 6→8). Los cuatro cambios que mueven la nota son de texto,
    # van abajo y renderizan en un minuto. El push-in se puede añadir luego con MiniMax H3.
    fc = f"[0:v]scale={W}:{H},setsar=1,fps=30[base];"
    fc += f"[base][1:v]overlay=x=40:y=H-{h1}-170:enable='between(t,0.15,4.6)'[b1];"
    fc += f"[b1][2:v]overlay=x=40:y=250:enable='between(t,7.9,11.2)'[b2];"
    fc += f"[b2][3:v]overlay=x=60:y=250:enable='between(t,11.4,14.4)'[b3];"
    fc += f"[b3][4:v]overlay=x=0:y=40:enable='gte(t,15.0)'[b4];"
    fc += f"[b4][5:v]overlay=x=0:y=90:enable='gte(t,15.0)'[v]"

    out = D / 'Adrian_tatuador_v2.mp4'
    # -t con la duración del original: los PNG entran con -loop 1 y sin esto ffmpeg
    # seguiría generando cuadros para siempre (así se fue un render de 45 minutos).
    import re as _re
    err = subprocess.run([FF, '-i', str(ORIG)], capture_output=True, text=True).stderr
    m = _re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 17.3
    subprocess.run([FF, '-v', 'error', '-y'] + ent + ['-filter_complex', fc,
                    '-map', '[v]', '-map', '0:a', '-t', f'{dur:.2f}',
                    '-c:v', 'libx264', '-profile:v', 'main',
                    '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'fast', '-c:a', 'aac',
                    '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart', str(out)], check=True)
    print(out)


if __name__ == '__main__':
    main()
