"""Servilin v4 obra fina: 5 escenas de limpieza post-construcción en casas/deptos nuevos con el uniforme real (Qwen-Image-Edit + H3), en seco.
Uso: python3 victor_v4_obra.py (genera a video/v4/)"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
UNI = ('Usa EXACTAMENTE el uniforme de los trabajadores de las imágenes: camisa y pantalón azul rey con franjas naranjas, chaleco amarillo fluorescente reflejante, '
       'guantes rojos, y personas mexicanas reales como las de la referencia. ')
SECO = ' Todo seco: sin agua, sin charcos, sin líquidos, sin espuma. Foto vertical 9:16, realista, documental, nítida, luz natural, sin texto, sin letras, sin logotipos.'
FIN = (' Keep the people, the blue uniforms with orange stripes, yellow reflective vests and red gloves exactly as in the first frame. Everything stays dry: no water, '
       'no puddles, no liquid, no foam. Very slow, gentle movement only. Realistic documentary look, natural light. No text. Audio: soft ambient, no speech.')
CU = {
 'O1_piso': (['trapeo', 'equipo'], UNI + 'Un trabajador se arrodilla en el piso de porcelanato claro de una casa nueva recién terminada y retira con una espátula restos secos de cemento y polvo blanco de obra; '
             'el piso tiene polvo de construcción y manchas secas de cemento, al fondo muros recién pintados.' + SECO),
 'O2_ventanal': (['trapeo', 'equipo'], UNI + 'Una trabajadora raspa con un raspador de navaja salpicaduras secas de pintura blanca de un ventanal grande de un departamento nuevo, sostiene un jalador de hule en la otra mano; '
                 'el vidrio tiene motas de pintura seca y polvo.' + SECO),
 'O3_aspirar': (['trapeo', 'equipo'], UNI + 'Un trabajador aspira el polvo fino con una aspiradora industrial en una sala amplia y vacía de un departamento recién entregado, piso de porcelanato, muros blancos, ventanales con luz.' + SECO),
 'O4_plastico': (['trapeo', 'equipo'], UNI + 'Una trabajadora retira el plástico protector transparente de la puerta de una cocina integral nueva con cubierta de cuarzo blanco, en un departamento recién terminado; el plástico se despega en una esquina.' + SECO),
 'O5_listo': (['trapeo', 'equipo'], UNI + 'Un departamento nuevo vacío totalmente impecable y listo para entregar: piso de porcelanato brillante sin polvo, ventanales cristalinos, cocina integral blanca; '
              'un supervisor con tableta y una trabajadora sonriendo al fondo, de pie, revisando el resultado.' + SECO),
}
TOMAS = [('O1_piso', 'O1_piso', 'Vertical shot: the worker gently scrapes dried cement bits off the porcelain floor, slow push-in.' + FIN, 5.5),
         ('O2_ventanal', 'O2_ventanal', 'Vertical shot: the worker slowly scrapes paint specks off the large window glass with a blade scraper, slow push-in.' + FIN, 5.5),
         ('O3_aspirar', 'O3_aspirar', 'Vertical shot: the worker slowly vacuums the fine dust across the empty apartment floor, slow lateral camera move.' + FIN, 5.5),
         ('O4_plastico', 'O4_plastico', 'Vertical shot: the worker slowly peels the protective plastic film off the new kitchen cabinet door, slow push-in.' + FIN, 5.5),
         ('O5_listo', 'O5_listo', 'Vertical shot: slow gentle push-in on the spotless empty apartment, the supervisor nods holding the tablet while the worker smiles.' + FIN, 5.5)]

if __name__ == '__main__':
    refs = {'trapeo': (AQUI / 'v2' / 'S1_trapeo.png').read_bytes(), 'equipo': (AQUI / 'cuadros' / 'f_8.jpg').read_bytes()}
    with app.run():
        res = escenas.remote('servilin_v4', refs, CU, TOMAS, 6)
    (AQUI / 'v4').mkdir(exist_ok=True)
    for n, b in res.items():
        (AQUI / 'v4' / n).write_bytes(b); print('guardado', n)
