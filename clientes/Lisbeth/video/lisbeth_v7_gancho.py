"""Lisbeth v7 · gancho como Kelsie (DbvIz5iRf_M) EN EL MISMO terreno que se ve desde arriba: de cuerpo completo en el borde de SU terreno junto a la carretera
de su foto de calle (la misma carretera y loma de su foto aérea), hablando natural y, al decir «¡Míralo desde arriba!», levanta el brazo señalando arriba como Kelsie, labios con su voz → la cámara sube desde ahí hasta SU foto
aérea real. 704×1280. Uso: python3 lisbeth_v7_gancho.py  (luego armar_lisbeth_v7.py)"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
NUEVAS = AQUI.parent / 'whatsapp' / 'nuevas_1024'
V7 = AQUI / 'v7'
CARA = 'Conserva EXACTAMENTE la cara de esta mujer: mismos ojos, cejas, nariz, boca, edad, tono de piel y cabello oscuro recogido. '
CUADROS = {'C_borde': (['lisbeth', 'calle'], CARA + 'Ella está de pie de CUERPO COMPLETO (de los pies a la cabeza) sobre la tierra de ESTE mismo terreno, en el borde junto a '
                       'ESTA misma carretera con línea amarilla, con el mismo pasto, los mismos árboles secos y la misma loma detrás, cielo azul limpio. Vestido negro '
                       'elegante sin mangas, las manos relajadas a los lados, sonrisa segura mirando a cámara. Luz cálida de tarde, foto vertical 9:16 '
                       'cinematográfica, lente de 24 mm, colores vivos, nítida, sin texto, sin letras, sin celulares.')}
HABLA = ('Vertical cinematic full-body shot by the roadside on the dry land plot: the woman talks to the camera in Spanish with natural lip movement matching '
         'the speech, calm and confident, her hands relaxed with only small natural movements while she talks. On the last words she raises her right arm high and '
         'points up to the sky, like Kelsie inviting the viewer to look from above. Warm smile, light breeze in her hair, slow handheld push-in, warm afternoon light. '
         'Keep her face exactly. No phone, no text. Audio: clear female voice speaking Spanish.')
SUBE = ('Continuous single drone shot, no cut, horizon always level and sky at the top: the woman by the road keeps her right arm raised pointing up while the camera rises '
        'smoothly and fast from her, flying up '
        'over the same road and land until it settles into the stable aerial view of the same hill, land and curving road. She stays on the ground and gets small. '
        'No phone, no rotation. No text. Audio: soft wind, no speech.')

if __name__ == '__main__':
    V7.mkdir(exist_ok=True)
    refs = {'lisbeth': (AQUI.parent / 'whatsapp' / 'del_cliente' / '20261022_161302_image.jpg').read_bytes(), 'calle': (NUEVAS / '24_130407_image.jpg').read_bytes()}
    listos = {'L3_aereo_v': (AQUI / 'v3' / 'L3_aereo_v.png').read_bytes()}
    voces = {'L_gancho': (AQUI / 'voz' / 'L_gancho.wav').read_bytes()}
    tomas = [('L7_habla', 'C_borde', HABLA, 4.52, None, 'L_gancho'), ('L7_sube', 'C_borde', SUBE, 4.0, 'L3_aereo_v')]
    with app.run():
        res = escenas.remote('lisbeth_v7', refs, CUADROS, tomas, 12, listos, voces, (704, 1280))
    for n, b in res.items():
        (V7 / n).write_bytes(b); print('guardado', n, flush=True)
