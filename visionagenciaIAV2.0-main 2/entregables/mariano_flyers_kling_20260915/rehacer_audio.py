"""Rehace SOLO el audio de los flyers que salieron con el sonido genérico viejo (el 1 de Astra y el 2), con el
diseño sonoro por flyer. No vuelve a generar el video de Kling: cuesta $0.01 por flyer.
Los archivos viejos NO se borran; el nuevo sale como ..._CON_SFX_v2.mp4.
Uso: python3 rehacer_audio.py            (1 y 2)
     python3 rehacer_audio.py 2          (solo el 2)"""
import json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import kling_flyer_endframe as k

# flyer -> (video sin audio, salida con el sonido nuevo)
FUENTES = {
    '1': (AQUI / 'FLYER_5S_TEXTO_ANIMADO_SIN_AUDIO.mp4', AQUI / 'FLYER1_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4'),
    '2': (AQUI / 'FLYER2_5S_TEXTO_ANIMADO_SIN_AUDIO.mp4', AQUI / 'FLYER2_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4'),
    # Carlos (16 sep): «en la mexicana un mejor sonido» — se rehace con la versión más rica
    '3': (AQUI / 'FLYER3_5S_TEXTO_ANIMADO_SIN_AUDIO.mp4', AQUI / 'FLYER3_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4'),
}


def rehacer(n):
    fuente, salida = FUENTES[n]
    if salida.exists():
        print('ya existe:', salida.name); return
    if not fuente.exists():
        print('FALTA el video sin audio de', n, ':', fuente.name); return
    sonido = k.SONIDOS[n]
    job_f = AQUI / ('sfx_flyer%s_v2_job.json' % n)
    sj = json.loads(job_f.read_text())['id'] if job_f.exists() else k.post(
        k.SFX, {'video': k._video_uri(fuente), 'prompt': sonido, 'duration': 5, 'num_samples': 1, 'seed': -1})
    job_f.write_text(json.dumps({'id': sj, 'model': k.SFX, 'prompt': sonido}, indent=2))
    k.bajar(k.esperar(sj, 'sfx%s' % n), salida)
    print('listo:', salida.name)


if __name__ == '__main__':
    for n in sys.argv[1:] or ['1', '2']:
        rehacer(n)
