"""BD Pro v2 · antes y después más impactante, como su referencia «El proceso vs. El resultado»: cada toma arranca en SU pista real vacía (cuadro de sus
videos) y se transforma en la fiesta que generamos (Qwen-Image-Edit hace el después con la MISMA pista; H3 anima del primer al último cuadro). 704×1280.
Uso: python3 bdpro_v2_escenas.py  (luego armar_bdpro_v2.py)"""
import io, sys
from pathlib import Path
from PIL import Image, ImageOps
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
MAT = AQUI.parent / 'material'
V2 = AQUI / 'v2'
IGUAL = 'Conserva EXACTAMENTE la misma pista de baile (mismo diseño, colores, patrón y tamaño), el mismo lugar y el mismo encuadre. '
FIN = ' Foto vertical 9:16, cinematográfica, realista, nítida, colores vivos, sin texto, sin letras.'
PARES = {  # nombre: (cuadro real de su video, cómo es el después, cómo se transforma)
    'D1_talavera': ('14_1024_0029_f', IGUAL + 'Ahora es de noche y es una boda elegante en este patio: guirnaldas de focos cálidos, velas, la pareja de novios bailando al centro de la pista '
                    'talavera y dos fuentes de chispas frías doradas a los lados, invitados alrededor con celulares.' + FIN,
                    'Magical time-lapse transformation: day turns into night, warm string lights switch on, cold-spark fountains burst on both sides and the bride and groom '
                    'appear dancing in the center of the same talavera dance floor. Smooth slow push-in. No text. Audio: crowd cheering, no speech.'),
    'D2_ajedrez': ('16_1024_0029_f', IGUAL + 'Ahora el salón está en plena fiesta de XV años: humo bajo blanco como nube sobre la pista de ajedrez rojo y blanco, la quinceañera con vestido '
                   'de gala rojo bailando el vals con su chambelán, luces cálidas y candelabros, invitados alrededor.' + FIN,
                   'Magical time-lapse transformation: low white cloud fog rolls over the same red and white checkered dance floor, warm lights glow and the quinceañera in a red '
                   'ball gown waltzes with her partner. Smooth slow orbit. No text. Audio: soft waltz ambience, no speech.'),
    'D3_monograma': ('20_1024_0029_f', IGUAL + 'Ahora es de noche en el mismo jardín con las montañas al fondo: la pista blanca con el monograma está LLENA de invitados bailando, focos '
                     'colgantes cálidos sobre la pista, mesas con velas alrededor.' + FIN,
                     'Time-lapse transformation: sunset turns into night in the same garden, warm lights turn on and the white monogram dance floor fills with dancing guests, '
                     'the camera rises smoothly to a high angle. No text. Audio: party crowd, no speech.'),
    'D4_iluminada': ('42_1024_0031_f', IGUAL + 'Ahora la pista blanca está ENCENDIDA con luz LED cálida desde abajo, es una fiesta de noche con invitados bailando sobre ella, confeti dorado '
                     'cayendo y luces de escenario.' + FIN,
                     'Time-lapse transformation: the room goes dark, the white dance floor lights up from below, golden confetti falls and guests start dancing on it. '
                     'Smooth slow push-in. No text. Audio: party crowd, no speech.'),
}


def vertical(ruta):
    im = ImageOps.fit(ImageOps.exif_transpose(Image.open(ruta)).convert('RGB'), (720, 1280), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()


if __name__ == '__main__':
    V2.mkdir(exist_ok=True)
    refs, listos, cuadros, tomas = {}, {}, {}, []
    for n, (foto, despues, mover) in PARES.items():
        refs[n] = listos[f'{n}_antes'] = vertical(MAT / f'{foto}.jpg')
        cuadros[f'{n}_despues'] = ([n], despues)
        tomas.append((n, f'{n}_antes', mover, 5.0, f'{n}_despues'))
    with app.run():
        res = escenas.remote('bdpro_v2', refs, cuadros, tomas, 13, listos, None, (704, 1280))
    for n, b in res.items():
        (V2 / n).write_bytes(b); print('guardado', n, flush=True)
