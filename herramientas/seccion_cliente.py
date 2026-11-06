"""Arma la sección de un cliente en la app Nexus (4 nov 2026, pedido de Carlos para Mariano).

Cada cliente entra con su propio enlace y ve: su último video, la calificación de Glimmer
más reciente con una barra por rubro, la lista de arreglos para llegar a 8 (marcables), y una
caja para decir qué quiere que se le cambie. Lo que manda cae en `buzon/para_nexus2/` y lo
ejecuta Claude.

    python3 herramientas/seccion_cliente.py <slug> <glimmer.log> <nombre_en_el_log> \
        --cliente "Mariano Herrera" --video clientes/Mariano/video/x.mp4 [--clave <clave>]

Genera `entregables/tablero/clientes/<slug>.json` y deja el video comprimido en
`entregables/tablero/cv/<slug>.mp4` si todavía no está. Después:
    modal volume put nexus-workspace entregables/tablero ... && modal deploy tablero_modal.py
"""
import argparse
import json
import pathlib
import re
import secrets
import subprocess

RAIZ = pathlib.Path('/workspaces/Nexusv2.0launch18octubre')
DEST = RAIZ / 'entregables/tablero'

# Glimmer escribe en jerga de anuncios; el cliente lee otra cosa.
CLARO = {
    'Gancho': 'el arranque, los primeros 3 segundos',
    'Oferta': 'lo que ofreces',
    'Confianza': 'qué tanta confianza das',
    'Claridad': 'qué tan claro se entiende',
    'Calidad visual': 'cómo se ve',
    'Políticas de Meta': 'reglas de Facebook',
    'Mensajes baratos': 'qué tan barato sale cada mensaje',
    'Mensajes calificados': 'si escribe gente que sí compra',
}


def respuesta(log: pathlib.Path, nombre: str) -> str:
    t = log.read_text(errors='ignore')
    i = t.find(f'######## {nombre}')
    if i < 0:
        raise SystemExit(f'No encontré «{nombre}» en {log}')
    t = t[i + len(nombre) + 9:]
    k = t.rfind('assistant to=user')
    if k >= 0:
        t = t[k + 17:]
    return t.split('Stopping app')[0].split('== Reporte Modal')[0].strip()


def trozo(txt: str, titulo: str, siguientes: list[str]) -> str:
    i = txt.find(titulo)
    if i < 0:
        return ''
    resto = txt[i + len(titulo):]
    cortes = [resto.find(s) for s in siguientes if resto.find(s) > 0]
    return (resto[:min(cortes)] if cortes else resto).strip(': \n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug'); ap.add_argument('log'); ap.add_argument('nombre')
    ap.add_argument('--cliente', required=True)
    ap.add_argument('--video', required=True, help='mp4 original del cliente')
    ap.add_argument('--clave', default=None)
    ap.add_argument('--fecha', default=None)
    ap.add_argument('--titulo', default=None)
    a = ap.parse_args()

    r = respuesta(pathlib.Path(a.log), a.nombre)
    m = re.search(r'CALIFICACIÓN TOTAL:\s*([\d.]+)', r)
    cal = float(m.group(1)) if m else None
    m = re.search(r'proyectada(?: con los cambios)?:?\s*([\d.]+)', r, re.I)
    proy = float(m.group(1)) if m else None

    rubros = []
    linea_notas = trozo(r, 'NOTAS', ['POR QUÉ FUNCIONA', 'QUÉ LO FRENA'])
    for parte in linea_notas.split('·'):
        mm = re.match(r'\s*([^0-9]+?)\s+([\d.]+)\s*/\s*10', parte)
        if mm:
            nom = mm.group(1).strip()
            rubros.append({'nombre': CLARO.get(nom, nom), 'valor': float(mm.group(2))})

    funciona = [l.strip('-• ').strip() for l in
                trozo(r, 'POR QUÉ FUNCIONA', ['QUÉ LO FRENA', 'VEREDICTO']).split('\n') if l.strip('-• ').strip()]

    arreglos = []
    for l in trozo(r, 'CÓMO SUBIR CADA NOTA', ['3 GANCHOS ALTERNATIVOS', '2 ESCENAS NUEVAS', 'LO MÁS RÁPIDO']).split('\n'):
        l = l.strip()
        if not l or 'ya está, no tocar' in l:
            continue
        mm = re.match(r'([A-Za-zÁÉÍÓÚáéíóúñÑ ]+?)\s*(\d+)\s*→\s*(\d+)\s*:\s*(.+)', l)
        if mm:
            nom = CLARO.get(mm.group(1).strip(), mm.group(1).strip())
            arreglos.append({'texto': mm.group(4).strip(),
                             'sube': f'sube {nom} de {mm.group(2)} a {mm.group(3)}'})
        elif len(l) > 25:
            arreglos.append({'texto': l.lstrip('-• '), 'sube': ''})

    rapido = [l.strip('-• ').strip() for l in trozo(r, 'LO MÁS RÁPIDO', ['3 GANCHOS', '2 ESCENAS']).split('\n')
              if l.strip('-• ').strip()]

    # video comprimido para la web
    (DEST / 'cv').mkdir(parents=True, exist_ok=True)
    web = DEST / 'cv' / f'{a.slug}.mp4'
    if not web.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(RAIZ / a.video), '-vf', 'scale=720:-2',
                        '-c:v', 'libx264', '-crf', '26', '-preset', 'veryfast',
                        '-c:a', 'aac', '-b:a', '96k', str(web), '-y'], check=True)

    (DEST / 'clientes').mkdir(parents=True, exist_ok=True)
    pj = DEST / 'clientes' / f'{a.slug}.json'
    viejo = json.loads(pj.read_text()) if pj.exists() else {}
    datos = {
        'cliente': a.cliente,
        'titulo': a.titulo or f'Anuncio de {a.cliente}',
        'intro': 'Aquí ves tu video, la calificación que le pone la IA de Facebook y exactamente qué '
                 'le falta para llegar a 8. Abajo de 8 Facebook casi no reparte mensajes y se paga por '
                 'vistas; de 8 para arriba empiezan a llegar mensajes baratos.',
        'regla': 'La nota de hoy es la de la izquierda. Con los arreglos de abajo llega a la de la derecha.',
        'clave': viejo.get('clave') or a.clave or secrets.token_urlsafe(9),
        'fecha': a.fecha or '',
        'calificacion': cal, 'proyectada': proy,
        'rubros': rubros, 'funciona': funciona[:5],
        'arreglos': arreglos[:10], 'rapido': rapido[:3],
        'video': f'/cv/{a.slug}.mp4',
        'video_ruta': a.video,
        'video_nota': '',
        'glimmer_crudo': r,
        'pedidos': viejo.get('pedidos', []),
        # regla de Carlos (4 nov 2026): si no contesta en 10 min, los cambios se aplican solos
        'propuesto_en': __import__('time').time(),
        'auto_hecho': None,
    }
    pj.write_text(json.dumps(datos, ensure_ascii=False, indent=1))
    print('sección lista:', pj)
    print('calificación:', cal, '→', proy, '| rubros:', len(rubros), '| arreglos:', len(arreglos))
    print('enlace: /c/%s?k=%s' % (a.slug, datos['clave']))


if __name__ == '__main__':
    main()
