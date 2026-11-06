"""Servilin (Víctor) v3: 2 escenas NUEVAS de limpieza en obra fina, EN SECO (sin agua, sin charcos ni líquidos raros como la máquina de la v2),
con el uniforme real de su equipo. Usa el productor genérico (Qwen-Image-Edit + H3). Uso: python3 victor_v3_escenas.py"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
UNIFORME = ('Usa EXACTAMENTE el uniforme de los trabajadores de las imágenes: camisa y pantalón azul rey con franjas naranjas, chaleco amarillo fluorescente reflejante, '
            'guantes rojos, y personas mexicanas reales como las de la referencia. ')
SECO = ' Todo seco: sin agua, sin charcos, sin líquidos, sin espuma. Foto vertical 9:16, realista, documental, nítida, luz natural, sin texto, sin letras, sin logotipos.'
FIN = (' Keep the people, the blue uniforms with orange stripes, yellow reflective vests and red gloves exactly as in the first frame. Everything stays dry: no water, '
       'no puddles, no liquid, no foam. Realistic documentary look, natural light. No text. Audio: soft ambient, no speech.')
CUADROS = {
    'C_obra': (['trapeo', 'equipo'], UNIFORME + 'Dos trabajadores limpian un departamento nuevo recién terminado, vacío, con piso de porcelanato claro, paredes blancas recién pintadas '
               'y ventanales: uno aspira el polvo de obra del piso con una aspiradora industrial de tambor, el otro sacude el marco de la ventana con un paño de microfibra.' + SECO),
    'C_vidrio': (['trapeo', 'equipo'], UNIFORME + 'Plano medio: una trabajadora retira con una espátula de navaja una gota de pintura seca del vidrio de una ventana nueva de aluminio, '
                 'en un departamento recién construido, con la luz del día entrando.' + SECO),
}
TOMAS = [('S5_obra', 'C_obra', 'Vertical shot: one worker slowly vacuums construction dust from the dry porcelain floor while the other wipes the window frame with a cloth, '
          'slow gentle push-in.' + FIN, 4.3),
         ('S6_vidrio', 'C_vidrio', 'Vertical shot: the worker carefully scrapes a dry paint drop off the new window glass with a blade scraper, the glass looks spotless, '
          'slow push-in.' + FIN, 4.3)]

if __name__ == '__main__':
    refs = {'trapeo': (AQUI / 'v2' / 'S1_trapeo.png').read_bytes(), 'equipo': (AQUI / 'cuadros' / 'f_8.jpg').read_bytes()}
    with app.run():
        res = escenas.remote('servilin_v3', refs, CUADROS, TOMAS, 6)
    (AQUI / 'v3').mkdir(exist_ok=True)
    for n, b in res.items():
        (AQUI / 'v3' / n).write_bytes(b); print('guardado', n)
