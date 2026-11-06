"""Consulta a Glimmer (Muse-Glimmer-30B en Modal, perfil fabelagabriel645) sobre una versión del gancho estilo Spiderman de Mariano.
Glimmer no acepta video: se mandan 4 cuadros de la referencia + cuadros cada 1.5 s de la versión, y en el texto el guion con tiempos y el audio.
Uso: python3 glimmer_spiderman.py vN ["notas de lo que cambió en esta ronda"]  → spiderman/glimmer_vN.txt"""
import json, os, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
SP = AQUI / 'spiderman'
FF = imageio_ffmpeg.get_ffmpeg_exe()
GLIMMER = Path('/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal')
CAPAC = Path('/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/glimmer_consultas_20261020/capacidades_video.txt')
REF = AQUI.parent / 'referencia' / 'gancho_spiderman.mp4'
from spiderman_voces import FRASES


def cuadro(v, t, ruta):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(v), '-frames:v', '1', '-vf', 'scale=432:-2', '-q:v', '3', str(ruta)], check=True)


def main():
    ver = sys.argv[1]; notas = sys.argv[2] if len(sys.argv) > 2 else ''
    v = AQUI / f'Vizcaino_v5_gancho_spiderman_{ver}.mp4'
    tiempos = json.loads((SP / f'tiempos_{ver}.json').read_text())
    carp = SP / f'glimmer_{ver}'; carp.mkdir(exist_ok=True)
    fotos = []
    for t in (0.5, 1.5, 3.0, 7.5):
        r = carp / f'ref_{t:04.1f}.jpg'; cuadro(REF, t, r); fotos.append(str(r))
    t = 0.3; ts = []
    while t < tiempos['TOTAL'] - 0.2:
        r = carp / f'v_{t:04.1f}.jpg'; cuadro(v, t, r); fotos.append(str(r)); ts.append(t); t += 1.5
    tl = ', '.join(f'{n} {s:.1f}s' for n, s in tiempos.items())
    prompt = (CAPAC.read_text() + '\n\n'
        'Eres director creativo de Reels inmobiliarios virales y media buyer de Meta Ads en México. Te paso imágenes en este orden: (1) 4 cuadros de un reel '
        'de REFERENCIA viral (a 0.5, 1.5, 3.0 y 7.5 s: el agente cae desde el techo de una casa, aterriza tipo Spiderman frente a cámara, habla con '
        'tipografía animada y luego vienen tomas rápidas de casas); (2) ' + str(len(ts)) + ' cuadros de NUESTRA versión para Mariano Herrera, asesor de '
        'Vizcaíno Residencial (Rosarito, B.C., Grupo Lagsa), tomados cada 1.5 s (' + ', '.join(f'{x:.1f}' for x in ts) + f' s; duración total {tiempos["TOTAL"]:.1f} s).\n'
        f'Secciones (inicio): {tl}.\n'
        'Audio: voz clonada de Mariano. Gancho con labios sincronizados: «' + FRASES['gancho'] + '». En off sobre recorridos REALES de cada modelo: «'
        + ' '.join(FRASES[k] for k in ('sotol', 'bugambilia', 'benjamina', 'salvia', 'privada')) + '». Cierre con labios: «' + FRASES['cta'] + '». '
        'Música: beat propio 124 BPM, suave bajo la voz del gancho, riser y DROP con whoosh justo cuando entra el dron; golpe/boom al aterrizar; whoosh en '
        'cada cambio de modelo; la música baja cuando habla. Subtítulos virales palabra por palabra (Playfair) en el gancho, la frase de privada y el cierre; '
        'tarjeta con nombre y precio en cada modelo; botón verde de WhatsApp en el cierre; tarjeta final con los 4 precios. '
        'Los precios son reales y no se pueden cambiar. Las tomas de dron y de noche son visualizaciones con IA y llevan la etiqueta «Visualización».\n'
        + (f'Cambios de esta ronda: {notas}\n' if notas else '') +
        'Califica de 1 a 10 cada criterio: a) Gancho en los primeros 3 s, b) Claridad de la oferta, c) Confianza/credibilidad, d) Calidad visual '
        '(incluye si la cara, las manos o el cuerpo se ven deformes o artificiales), e) CTA, f) Ritmo/edición comparado con la referencia. Da el promedio. '
        'Luego lista de 5 a 8 mejoras CONCRETAS y ejecutables con las capacidades de arriba, ordenadas por impacto, con segundos exactos. '
        'Si algo ya está en 10 dilo. Responde solo la respuesta final, en español, sin mostrar razonamiento.')
    (carp / 'prompt.txt').write_text(prompt)
    env = dict(os.environ, MODAL_PROFILE='fabelagabriel645')
    r = subprocess.run(['modal', 'run', 'glimmer_modal.py', '--prompt', prompt, '--fotos', ','.join(fotos), '--tokens', '6000'],
                       cwd=GLIMMER, capture_output=True, text=True, env=env)
    out = r.stdout + ('\n' + r.stderr[-3000:] if r.returncode else '')
    (SP / f'glimmer_{ver}.txt').write_text(out); print(out[-6000:])


if __name__ == '__main__':
    main()
