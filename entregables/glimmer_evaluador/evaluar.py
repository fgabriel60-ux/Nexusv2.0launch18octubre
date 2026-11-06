"""Regla de Carlos (30 oct): cada anuncio de cliente va con la calificación de Glimmer y su explicación de por qué funciona.
Regla de Carlos (4 nov): además de la nota, Glimmer entrega CÓMO SUBIR CADA RUBRO (escenas, ganchos, cambios con IA) para agilizar llegar a 8.
Arma un lote para glimmer_modal.py a partir de videos terminados: 2 hojas de 15 cuadros con el segundo de cada uno + transcripción con tiempos.
  python3 evaluar.py anuncios.json salida_dir [extra.json]      # anuncios.json = [{"nombre", "video", "cliente"}]  (cliente = datos reales del negocio)
  GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote <salida_dir>/lote.json --tokens 2500
Las respuestas quedan junto a lote.json (ver glimmer_modal.py)."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CAP = Path('/workspaces/Nexusv2.0launch18octubre/clientes/Giovanni/glimmer_101010_20261028/capacidades_video.txt')


def dur(v):
    # ffprobe no está instalado en el sandbox; la duración sale de `ffmpeg -i` (stderr).
    import re
    err = subprocess.run(['ffmpeg', '-i', str(v)], capture_output=True, text=True).stderr
    m = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', err)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def hojas(video, dest, n=30):
    d = dur(video); ts = [d * (i + .5) / n for i in range(n)]; cuadros = []
    for t in ts:
        b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', str(video), '-frames:v', '1', '-vf', 'scale=240:426', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        im = Image.frombytes('RGB', (240, 426), b) if len(b) == 240 * 426 * 3 else Image.new('RGB', (240, 426))
        ImageDraw.Draw(im).text((8, 6), f'{t:.1f}s', fill='yellow', stroke_width=2, stroke_fill='black', font=ImageFont.load_default(22))
        cuadros.append(im)
    rutas = []
    for h in range(2):
        hoja = Image.new('RGB', (240 * 5, 426 * 3))
        for i, im in enumerate(cuadros[h * 15:(h + 1) * 15]): hoja.paste(im, ((i % 5) * 240, (i // 5) * 426))
        r = dest / f'{video.stem}_hoja{h + 1}.jpg'; hoja.save(r, quality=88); rutas.append(str(r))
    return d, rutas


def transcribir(video, modelo):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    s, _ = modelo.transcribe(np.frombuffer(b, np.int16).astype(np.float32) / 32768, language='es', vad_filter=True)
    return '\n'.join(f'[{x.start:5.1f}-{x.end:5.1f}s] {x.text.strip()}' for x in s)


PROMPT = """Eres estratega de anuncios de Meta (Facebook/Instagram) y director de video para negocios en México. Da SOLO la respuesta final, en español claro para el dueño del negocio, sin mostrar tu razonamiento. Usa SOLO los datos de abajo; si falta algo, marca [CONFIRMAR]. No inventes precios, tiempos, distancias ni garantías.

NEGOCIO: {cliente}
Objetivo: campaña de mensajes a WhatsApp con mensajes baratos y CALIFICADOS (gente que sí compra).

VIDEO DEL ANUNCIO ({d:.1f} s, 9:16). Imágenes adjuntas = 30 cuadros repartidos en TODO el video (2 hojas de 15, con el segundo de cada cuadro arriba a la izquierda). Los subtítulos y tarjetas son capas de texto exactas.
TRANSCRIPCIÓN DE LO QUE SE DICE (con tiempos):
{tr}

Responde EXACTAMENTE con este formato:
CALIFICACIÓN TOTAL: X/10
NOTAS: Gancho X/10 · Oferta X/10 · Confianza X/10 · Claridad X/10 · Calidad visual X/10 · Políticas de Meta X/10 · Mensajes baratos X/10 · Mensajes calificados X/10
POR QUÉ FUNCIONA: 3 a 5 viñetas cortas, cada una señalando el segundo exacto del video y por qué hace que la gente escriba.
QUÉ LO FRENA: 1 a 3 viñetas con el segundo exacto y el arreglo concreto (solo arreglos viables con las capacidades de abajo).
VEREDICTO: «Subir ya», «Subir con cambios» o «No subir», y la calificación proyectada con los cambios.
CÓMO SUBIR CADA NOTA: una línea por CADA rubro de NOTAS (Gancho, Oferta, Confianza, Claridad, Calidad visual, Políticas de Meta, Mensajes baratos, Mensajes calificados), en este formato:
  <Rubro> X→Y: <el cambio exacto> · <segundo o rango donde va> · <con qué se hace: corte/texto en capa/voz clonada/Qwen-Image-Edit/MiniMax H3/material que debe mandar el cliente>
  Si un rubro ya está en 8 o más, escribe «ya está, no tocar».
3 GANCHOS ALTERNATIVOS para los primeros 3 segundos, palabra por palabra, cada uno con la escena que lo acompaña (de lo que YA existe o generable con Qwen/MiniMax) y a quién filtra.
2 ESCENAS NUEVAS CON IA que más subirían la nota: qué se ve, con qué modelo se hace, qué foto o toma real hace falta de base, y cuántos segundos dura cada una.
LO MÁS RÁPIDO: de todo lo anterior, los 3 cambios que suben más nota con menos trabajo, en orden.

{cap}"""


def main():
    anuncios = json.loads(Path(sys.argv[1]).read_text()); dest = Path(sys.argv[2]); dest.mkdir(parents=True, exist_ok=True)
    from faster_whisper import WhisperModel
    m = WhisperModel('medium', device='cpu', compute_type='int8')
    cap = CAP.read_text() if CAP.exists() else ''
    lote = []
    for a in anuncios:
        v = Path(a['video']); d, fotos = hojas(v, dest); tr = transcribir(v, m)
        (dest / f"{a['nombre']}_transcripcion.txt").write_text(tr)
        lote.append({'nombre': a['nombre'], 'fotos': fotos, 'prompt': PROMPT.format(cliente=a['cliente'], d=d, tr=tr, cap=cap)})
        print('listo', a['nombre'], f'{d:.1f}s', flush=True)
    if len(sys.argv) > 3: lote += json.loads(Path(sys.argv[3]).read_text())  # consultas extra (estrategias) en la misma carga de Glimmer
    (dest / 'lote.json').write_text(json.dumps(lote, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
