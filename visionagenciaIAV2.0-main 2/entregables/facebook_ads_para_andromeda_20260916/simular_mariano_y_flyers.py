"""Simula en Andromeda Lab el video de Catania de Mariano y los 6 flyers, contra la campaña ganadora de Carlos.

Carlos autorizó (16 sep) agrupar las 4 campañas de mensajes en un solo contexto: el motor exige 3 anuncios
comparables y cada campaña tenía uno solo, cada quien con su propia etiqueta de audiencia. Criterio de la
agrupación, para dejarlo documentado: mismo anunciante (Visión Agencia), mismo mercado (Nogales y alrededores),
mismo evento contado (conversación iniciada) y misma atribución. NO se mezclan objetivos: las de tráfico y las de
leads se quedan como estaban.

No se toca el CSV original ni el motor: se escribe un CSV aparte y se llama a `engine.run` en proceso, sin
levantar el servidor de Astra.
Uso: python3 simular_mariano_y_flyers.py
"""
import csv, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LAB = Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/andromeda-lab')
sys.path.insert(0, str(LAB))
from engine import run  # noqa: E402

ORIGINAL = AQUI / 'facebook_ads_normalizado.csv'
AGRUPADO = AQUI / 'facebook_ads_normalizado_agrupado.csv'
IDEAS = AQUI / 'ideas_mariano_y_flyers.json'
INFORME = AQUI / 'informe_simulacion_mariano_flyers.json'
ETIQUETA = 'Mensajes a WhatsApp y Messenger - Vision Agencia (agrupado)'


def main():
    filas = list(csv.DictReader(ORIGINAL.open(encoding='utf-8-sig')))
    enriquecido = json.loads((AQUI / 'facebook_ads_enriched.json').read_text(encoding='utf-8'))
    # campaign_id de la ganadora, para pedirla como referencia explícita
    ganadora = next(r['campaign_id'] for r in enriquecido if (r.get('campaign') or '').startswith('[8/6/2026]'))

    for f in filas:
        if f['objective'] == 'messages':
            f['audience'] = ETIQUETA
    with AGRUPADO.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)

    mensajes = [f for f in filas if f['objective'] == 'messages']
    print('filas de mensajes:', len(mensajes), '| anuncios:', len({f['ad_id'] for f in mensajes}),
          '| campañas:', len({f['campaign_id'] for f in mensajes}))
    print('campaña de referencia (ganadora):', ganadora)

    contexto = {'account_id': '684865860329838', 'currency': 'MXN', 'objective': 'messages',
                'result_type': 'conversacion_iniciada', 'attribution': 'default_7d_click_1d_view',
                'placement': 'mixed', 'audience': ETIQUETA}
    ideas = json.loads(IDEAS.read_text(encoding='utf-8'))
    payload = {'history': filas, 'ideas': ideas, 'context': contexto, 'benchmark_id': ganadora,
               'settings': {'budget': 1500, 'days': 7, 'allocation': 'equal', 'seed': 42}}

    res = run(payload)
    INFORME.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    if res.get('status') != 'ok':
        print('EL MOTOR NO SIMULÓ:', res.get('status'), '-', res.get('message')); return

    print('\nmodo:', res['mode'], '| filas usadas:', res['rows_used'], '| anuncios:', res['ads_used'],
          '| métrica:', res['metric'])
    b = res.get('benchmark')
    print('referencia:', json.dumps(b, ensure_ascii=False) if b else 'ninguna')
    v = res['validation']
    print('validación temporal:', json.dumps({k: v[k] for k in list(v)[:6]}, ensure_ascii=False))
    print('\n%-32s %10s %10s %10s %9s %s' % ('idea', 'result p10', 'mediana', 'p90', 'CPA med', 'evidencia'))
    for o in res['ideas']:
        r, c = o['results'], o['cpa']
        print('%-32s %10s %10s %10s %9s %s' % (
            o['name'][:32], r['p10'], r['median'], r['p90'],
            ('inf' if c['median'] is None or c['median'] == float('inf') else round(c['median'], 2)),
            o['evidence'][:44]))
    print('\ntotales:', json.dumps(res['totals'], ensure_ascii=False))
    print('\navisos del motor:')
    for w in res['warnings']:
        print('  -', w)


if __name__ == '__main__':
    main()
