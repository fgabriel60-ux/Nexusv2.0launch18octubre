"""Comparación reproducible de titulares, sin publicar ni producir imágenes."""
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LAB = ROOT / 'visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/andromeda-lab'
sys.path.insert(0, str(LAB))
from engine import run

source = ROOT / 'entregables/propuesta_agencia_20260916/entrada_motor.json'
base = json.loads(source.read_text())
headlines = [
    'Tu marca merece vender.',
    'Tu marca merece vender más.',
    'Tu negocio merece más clientes.',
    'Dale a tu marca la campaña que merece.',
    'Tu próximo anuncio empieza con una muestra gratis.',
]
body = ('Nosotros creamos la campaña. Tú recibes los clientes. '
        'Por solo $500 al mes — sin letras pequeñas. '
        'En solo 4 horas tienes tu campaña corriendo. '
        'Video gratis de muestra: creamos un video profesional de tu marca '
        'para que conozcas nuestro trabajo antes de empezar.')
records = []
for i, headline in enumerate(headlines, 1):
    idea = {
        'name': f'A{i}: {headline}',
        'text': (f'Titular: {headline} Texto en la pieza: {body} '
                 'Formato propuesto: imagen cuadrada negra y naranja con tres tarjetas '
                 'de precio, plazo y muestra. Sin texto principal externo. '
                 'CTA: Chatea en Messenger. Destinos Messenger y WhatsApp. '
                 'Saludo: ¡Hola! ¿Cómo podemos ayudarte? '
                 'Concepto escrito, sin generar imagen. Condiciones comerciales históricas; '
                 'no se verificó su vigencia. No es garantía de clientes ni ventas.')
    }
    payload = copy.deepcopy(base)
    payload['ideas'] = [idea]
    payload['settings'].update(budget=966.63, days=19, seed=42, allocation='equal', tolerance=0)
    result = run(payload)
    assert result['status'] == 'ok', result
    records.append({'id': f'A{i}', 'titular': headline, 'cuerpo': body, 'entrada': payload, 'resultado': result})

metrics = ('results', 'cpa', 'spend', 'scenario_fraction_near_benchmark')
same = all(all(r['resultado']['ideas'][0][k] == records[0]['resultado']['ideas'][0][k]
               for k in metrics) for r in records)
summary = {
    'comparacion': 'Corridas individuales alternativas, cada una con presupuesto completo. No se suman.',
    'engine_sha256': hashlib.sha256((LAB / 'engine.py').read_bytes()).hexdigest(),
    'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'metricas_identicas': same,
    'validacion': records[0]['resultado']['validation'],
    'variantes': [{
        'id': r['id'], 'titular': r['titular'],
        **{k: r['resultado']['ideas'][0][k] for k in metrics}
    } for r in records],
    'limite': 'No permite elegir un titular ganador. El texto no modifica las tasas; 70% es frecuencia simulada, no probabilidad calibrada.'
}
assert same, 'Revisar diferencias numéricas antes de interpretar.'
(OUT / 'corridas.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
(OUT / 'resumen.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
lines = [
    '# Variantes cercanas al anuncio ganador — 17 septiembre 2026', '',
    'Se ejecutaron cinco corridas individuales de 600 réplicas: 966.63 MXN y 19 días por alternativa, semilla 42. No se generaron imágenes ni se publicaron anuncios.', '',
    'Todas conservan una propuesta cuadrada negra/naranja, tres tarjetas y la oferta histórica. Solo cambia el titular entre variantes. El cuerpo aclara que la muestra permite conocer el trabajo; esa redacción difiere del original, que decía ver resultados antes de empezar. A1 conserva el titular original, pero no es una reproducción exacta de la pieza.', '',
    'Texto común:', '', body, '',
    '| Variante | Titular | Conversaciones: mediana (P10–P90) | Costo: mediana (P10–P90), MXN |',
    '|---|---|---:|---:|'
]
for r in records:
    v = r['resultado']['ideas'][0]
    n, c = v['results'], v['cpa']
    lines.append(f"| {r['id']} | {r['titular']} | {n['median']:.0f} ({n['p10']:.0f}–{n['p90']:.0f}) | {c['median']:.2f} ({c['p10']:.2f}–{c['p90']:.2f}) |")
lines += ['',
    'En todas, el 70% de réplicas iguala o mejora el costo histórico de 11.5075 MXN. No es una probabilidad validada de éxito. Los percentiles son marginales, no parejas de una misma réplica.', '',
    'El contexto tiene dos anuncios de una campaña y cero campañas evaluadas en validación temporal. El modelo textual permanece desactivado. La igualdad numérica se verificó expresamente; no hay ranking predictivo de titulares.', '',
    'Prioridad editorial: A1 como referencia de titular y A2 como cambio mínimo. A3 adapta marca a negocio; A4 enfatiza el servicio; A5 enfatiza la muestra y podría cambiar la calidad de los contactos. Estas son hipótesis, no hallazgos del simulador.', '',
    'No se verificó la vigencia de precio/plazo ni si los 500 MXN incluyen pauta. Conversaciones no equivalen a ventas.']
(OUT / 'ANUNCIOS_Y_RESULTADOS.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))
