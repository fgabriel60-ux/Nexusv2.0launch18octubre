"""Mariano v4 · rehace 2 tomas: en el cierre Qwen lo dejó SIN camisa y en «presenta» sin su saco. Ahora la ropa sale de su propia toma caminando
(saco azul claro y camisa blanca). Uso: python3 mariano_v4_rehacer.py"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas
from mariano_v4_escenas import CARA, DORADA, HABLA

AQUI = Path(__file__).resolve().parent
V4 = AQUI / 'v4'
ROPA = ('Viste EXACTAMENTE como en la segunda imagen: saco azul claro de vestir puesto y camisa blanca abotonada, completamente vestido, ropa formal. ')
CUADROS = {
    'C3_presenta2': (['mariano', 'camina'], CARA + ROPA + 'Plano medio de la cintura para arriba frente a la fachada de ESTAS casas, él mira a cámara y presenta con la mano abierta. ' + DORADA),
    'C6_cierre2': (['mariano', 'camina'], CARA + ROPA + 'Plano medio del pecho para arriba, sonriente, mirando a cámara y apuntando con el dedo hacia la cámara, con ESTAS casas '
                   'desenfocadas atrás. ' + DORADA),
}

if __name__ == '__main__':
    d = [float(x) for x in '2.37 5.14 4.61 3.73 3.28 5.89'.split()]
    tomas = [('M4_presenta', 'C3_presenta2', 'Vertical medium shot, slow dolly in, he presents the houses with an open hand, fully dressed in a light blue blazer and white shirt.' + HABLA, d[2], None, 'f2'),
             ('M4_cierre', 'C6_cierre2', 'Vertical medium close-up, slow push-in, he smiles and points at the camera, fully dressed in a light blue blazer and white shirt.' + HABLA, d[5], None, 'f5')]
    refs = {'mariano': (AQUI.parent / 'fotos' / 'mariano_luz_final.png').read_bytes(), 'camina': (V4 / 'C1_camina.png').read_bytes()}
    voz = {f'f{i}': (V4 / 'voz' / f'f{i}.wav').read_bytes() for i in (2, 5)}
    with app.run():
        res = escenas.remote('mariano_v4b', refs, CUADROS, tomas, 9, None, voz, (704, 1280))
    for n, b in res.items():
        (V4 / n).write_bytes(b); print('guardado', n, flush=True)
