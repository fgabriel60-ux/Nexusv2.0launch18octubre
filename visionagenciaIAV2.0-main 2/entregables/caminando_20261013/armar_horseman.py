"""Marcos y Omar caminando con subtítulos Horseman detrás de ellos."""
import sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / 'modelos_modal'))
from horseman import render

E = AQUI.parent
(AQUI / 'final').mkdir(exist_ok=True)
quien = sys.argv[1] if len(sys.argv) > 1 else 'ambos'
if quien in ('omar', 'ambos'):
    print(render([(AQUI / 'clips' / 'O1.mp4', AQUI / 'voz' / 'TO1.wav'), (AQUI / 'clips' / 'O2.mp4', AQUI / 'voz' / 'TO2.wav')],
                 AQUI / 'final' / 'Omar_caminando_horseman.mp4', cierre_png=E / 'omar_20261013' / 'tmp_armado' / 'tarjeta.png'))
if quien in ('marcos', 'ambos'):
    print(render([(AQUI / 'clips' / f'M{i}.mp4', AQUI / 'voz' / f'TM{i}.wav') for i in (1, 2, 3)],
                 AQUI / 'final' / 'Marcos_caminando_horseman.mp4', cierre_png=E / 'marcos_ortega_20261012' / 'v_marcos' / 'tmp_armado' / 'cierre.png'))
