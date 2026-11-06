"""Lisbeth v6 · gancho con la calidad de la referencia de la realtor del campo de golf (DbvIz5iRf_M), pero ella SOBRE su terreno real: cuerpo completo,
luz cálida, lente 24 mm, habla moviendo las manos con los labios guiados por su voz, a 720×1280. Desde ese mismo cuadro la cámara sube como dron hasta
SU foto aérea real (sin IA, en vertical). Uso: python3 lisbeth_v6_gancho.py  (luego armar_lisbeth_v6.py)"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
NUEVAS = AQUI.parent / 'whatsapp' / 'nuevas_1024'
V6 = AQUI / 'v6'
CARA = ('Conserva EXACTAMENTE la cara de esta mujer: mismos ojos, cejas, nariz, boca, edad, tono de piel y cabello oscuro recogido. ')
CUADROS = {'C_campo': (['lisbeth', 'terreno'], CARA + 'Ella está de pie SOBRE ESTE mismo terreno (la misma tierra clara desmontada con ramas secas, los mismos árboles secos y '
                       'las mismas montañas al fondo, cielo azul), de cuerpo completo un poco más cerca de la rodilla para arriba, mirando a cámara con una sonrisa '
                       'segura, vestido negro elegante sin mangas, las manos abiertas a la altura de la cintura como explicando. Luz cálida de tarde que le da en la cara, '
                       'foto vertical 9:16 cinematográfica, lente de 24 mm, profundidad de campo, nítida, colores vivos, sin texto, sin letras, sin celulares.')}
HABLA = ('Vertical cinematic shot on the dry land plot: the woman talks to the camera in Spanish with natural lip movement matching the speech, she gestures '
         'naturally with both hands while she explains, opens her arms toward the land behind her, warm confident smile, a light breeze moves her hair. '
         'Slow handheld push-in, warm afternoon light, shallow depth of field. Keep her face exactly. No phone, no text. Audio: clear female voice speaking Spanish.')
SUBE = ('Continuous single drone shot, no cut, the horizon always level and the sky at the top: the camera rises smoothly and fast from the woman standing on the '
        'land, flying up and forward over the plot until it settles into the stable aerial view of the same hill, land and curving road. She stays on the ground '
        'and gets small below. No phone, no rotation. No text. Audio: soft wind, no speech.')

if __name__ == '__main__':
    V6.mkdir(exist_ok=True)
    refs = {'lisbeth': (AQUI.parent / 'whatsapp' / 'del_cliente' / '20261022_161302_image.jpg').read_bytes(),
            'terreno': (NUEVAS / '24_130210_image.jpg').read_bytes()}
    listos = {'L3_aereo_v': (AQUI / 'v3' / 'L3_aereo_v.png').read_bytes()}
    voces = {'L_gancho': (AQUI / 'voz' / 'L_gancho.wav').read_bytes()}
    tomas = [('L6_habla', 'C_campo', HABLA, 4.52, None, 'L_gancho'), ('L6_sube', 'C_campo', SUBE, 4.0, 'L3_aereo_v')]
    with app.run():
        res = escenas.remote('lisbeth_v6', refs, CUADROS, tomas, 8, listos, voces, (704, 1280))   # H3 pide múltiplos de 32: con 720 truena
    for n, b in res.items():
        (V6 / n).write_bytes(b); print('guardado', n, flush=True)
