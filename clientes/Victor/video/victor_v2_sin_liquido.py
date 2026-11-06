"""Servilin v2 sin el líquido raro: Qwen-Image-Edit limpia el piso del primer cuadro de la escena de la máquina (S3) — misma gente, misma máquina y misma
nave, pero el piso seco y brillante — y H3 la vuelve a animar sin agua. El resto de la v2 no cambia. Uso: python3 victor_v2_sin_liquido.py"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
CUADROS = {'S3_seco': (['s3'], 'Quita TODO el líquido café, el agua, los charcos y las manchas del piso: el piso de la nave queda seco, limpio y brillante. Deja EXACTAMENTE '
                       'igual a las personas, sus caras, uniformes azules con franjas naranjas, chalecos amarillos y guantes rojos, la máquina y la nave. '
                       'Foto vertical 9:16, realista, nítida, sin texto.')}
TOMAS = [('S3_maquina_seca', 'S3_seco', 'Vertical shot: the worker guides the floor cleaning machine slowly forward over the DRY, clean, shiny floor while the team watches. '
          'Everything stays dry: no water, no puddles, no liquid, no foam, no stains appear. Keep the people, uniforms, vests and gloves exactly as in the first frame. '
          'Slow tracking shot, realistic documentary look. No text. Audio: soft machine hum, no speech.', 4.3)]

if __name__ == '__main__':
    with app.run():
        res = escenas.remote('servilin_v2_seco', {'s3': (AQUI / 'v2' / 'S3_primer_cuadro.png').read_bytes()}, CUADROS, TOMAS, 11)
    for n, b in res.items():
        (AQUI / 'v2' / n).write_bytes(b); print('guardado', n, flush=True)
