"""Prueba reproducible con el motor corregido y el historial propio de Claude."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LAB = ROOT / 'visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/andromeda-lab'
SOURCE = ROOT / 'entregables/historial_comparable_20260916/03_historial_simulador.csv'
sys.path.insert(0, str(LAB))
import engine

idea = {
    'name': 'Tu marca merece vender',
    'text': 'Pieza estática cuadrada negra y naranja para Visión Agencia IA. '
            'Gancho: TU MARCA MERECE VENDER. '
            'Tres tarjetas: Campaña desde $500 al mes; Lista en 4 horas; '
            'Video gratis de muestra. Escena: ejemplo visual de un negocio y '
            'su anuncio en un teléfono, claramente identificado como muestra, sin '
            'testimonios ni cifras de ventas inventadas. Oferta: creamos la campaña '
            'de tu marca y un video de muestra gratis. Texto propuesto: '
            'Dale a tu negocio una campaña hecha para que te conozcan y te escriban. '
            'Por $500 al mes preparamos tu campaña, lista en 4 horas. '
            'Primero conoce nuestro trabajo con un video gratis de muestra. '
            'Escríbenos MUESTRA y cuéntanos qué vendes. CTA: Enviar mensaje. '
            'Hipótesis editorial basada en la oferta histórica; precio, plazo y '
            'alcance pendientes de confirmar antes de publicar.'
}

with SOURCE.open(encoding='utf-8-sig', newline='') as fh:
    history = list(csv.DictReader(fh))
rows, duplicates = engine.parse_history(history)
winner_rows = [r for r in rows if r['ad_id'] == '120251563209080651']
contexts = [engine.context_of(r) for r in winner_rows]
assert contexts and all(c == contexts[0] for c in contexts)
context = contexts[0]
selected = [r for r in rows if engine.context_of(r) == context]
winner = engine.aggregate(winner_rows)[0]
payload = {
    'history': history, 'ideas': [idea], 'context': context,
    'benchmark_id': winner['ad_id'], 'benchmark_scope': 'ad',
    'exploratory_two_ads': True,
    'settings': {'budget': 966.63, 'days': 19, 'seed': 42, 'allocation': 'equal', 'tolerance': 0}
}
result = engine.run(payload)
audit = {
    'source': str(SOURCE.relative_to(ROOT)),
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'engine_sha256': hashlib.sha256((LAB / 'engine.py').read_bytes()).hexdigest(),
    'rows': len(rows), 'duplicates': duplicates,
    'comparable_rows': len(selected),
    'comparable_ads': [r['ad_id'] for r in engine.aggregate(selected)],
    'comparable_campaigns': [r['campaign_id'] for r in engine.aggregate(selected, 'campaign_id')],
    'historical_ad_reference': {k: winner[k] for k in ('ad_id', 'campaign_id', 'spend', 'results', 'impressions', 'link_clicks')},
    'historical_cost_per_conversation': winner['spend'] / winner['results'],
    'temporal_validation_for_conversations': engine.backtest(selected, 'results'),
    'limitations': [
        'Exploración con dos anuncios autorizada por Carlos; no habilita el modelo textual.',
        'Evento corregido: conversacion_iniciada usa results, incluso con objective=traffic.',
        'Referencia seleccionada por anuncio: excluye las métricas del video.',
        'Se habilitó explícitamente el mínimo exploratorio de dos; no se cambiaron públicos, objetivos, IDs ni validación textual.'
    ]
}
for name, obj in [('propuesta.json', idea), ('entrada_motor.json', payload),
                  ('resultado_motor.json', result), ('auditoria.json', audit)]:
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'resultado': result, 'auditoria': audit}, ensure_ascii=False, indent=2))
