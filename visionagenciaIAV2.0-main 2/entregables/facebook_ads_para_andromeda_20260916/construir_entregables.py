"""Prepara los datos de Meta Ads para Andromeda Lab, según el encargo de Astra en
`PARA_CLAUDE_METRICAS_ANDROMEDA.md`.

Entra: las dos extracciones de Windsor.ai ya guardadas en disco (métricas diarias por anuncio y catálogo de
creativos). Sale: raw, enriquecido, CSV normalizado, catálogo de creativos y VALIDACION.md.

Reglas que se respetan (del encargo):
  - Ausente no es cero: solo se pone 0 cuando el anuncio SÍ tuvo entrega ese día (impresiones > 0) y Meta omitió
    la acción, que es como Meta representa «cero ocurrencias». Queda documentado.
  - No se inventa `idea`: si el anuncio no trae texto del creativo, la fila no entra al CSV de modelado.
  - El objetivo no se traduce a ciegas: solo se mapea cuando el objetivo de campaña y el evento de optimización
    concuerdan. Si no, la fila se excluye conservando el valor original.
  - Nada de tokens en los entregables.
Uso: python3 construir_entregables.py
"""
import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TR = Path('/home/codespace/.claude/projects/-workspaces-visionagenciaIAV2-0/bf91dc0b-63b8-4914-b0e7-caed831e8c9b/tool-results')
F_METRICAS = TR / 'mcp-claude_ai_Windsor_ai-get_data-1789523012326.txt'
F_CREATIVOS = TR / 'mcp-claude_ai_Windsor_ai-get_data-1789523110751.txt'

CUENTA = '684865860329838'
MONEDA = 'MXN'
ZONA = 'America/Tijuana'
ATRIBUCION = 'default_7d_click_1d_view'
METRICA_MENSAJES = 'actions_onsite_conversion_messaging_conversation_started_7d'
EXTRAIDO = '2026-09-16'
RANGO = ('2026-04-01', '2026-09-15')

# objetivo de campaña -> (objetivo del simulador, evento de optimización que debe coincidir, result_type, campo)
MAPEO = {
    'MESSAGES': ('messages', {'CONVERSATIONS'}, 'conversacion_iniciada', METRICA_MENSAJES),
    'LEAD_GENERATION': ('leads', {'LEAD_GENERATION'}, 'lead', 'actions_lead'),
    'LINK_CLICKS': ('traffic', {'LINK_CLICKS', 'LANDING_PAGE_VIEWS'}, 'link_click', 'link_clicks'),
}


def cargar(p):
    return json.loads(p.read_text(encoding='utf-8'))['result']


def limpiar(t, n=600):
    if not t:
        return ''
    return re.sub(r'\s+', ' ', str(t)).strip()[:n]


def idea_de(c):
    """Descripción fiel del creativo: gancho/texto + título + oferta + CTA + formato. Sin texto no hay idea."""
    cuerpo = limpiar(c.get('body'))
    if not cuerpo:
        return None
    partes = [cuerpo]
    if c.get('title'):
        partes.append('Título: ' + limpiar(c['title'], 120))
    if c.get('call_to_action_type'):
        partes.append('CTA: ' + c['call_to_action_type'])
    if c.get('object_type'):
        partes.append('Formato: ' + c['object_type'])
    return ' | '.join(partes)


def main():
    metricas, creativos = cargar(F_METRICAS), cargar(F_CREATIVOS)
    cat = {c['ad_id']: c for c in creativos}

    # 1) RAW
    raw = {
        'extraido_el': EXTRAIDO, 'fuente': 'Windsor.ai, conector facebook (Meta Ads), lectura',
        'cuenta': CUENTA, 'moneda': MONEDA, 'zona_horaria': ZONA, 'atribucion': ATRIBUCION,
        'rango_solicitado': {'desde': RANGO[0], 'hasta': RANGO[1]},
        'consultas': [
            {'nombre': 'metricas_diarias_por_anuncio', 'granularidad': 'una fila por anuncio por día, agregada sobre ubicaciones',
             'campos': sorted(metricas[0].keys()), 'filas': len(metricas)},
            {'nombre': 'catalogo_creativos', 'granularidad': 'una fila por anuncio',
             'campos': sorted(creativos[0].keys()), 'filas': len(creativos)},
        ],
        'metricas_diarias': metricas, 'creativos': creativos,
    }
    (AQUI / 'facebook_ads_raw.json').write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding='utf-8')

    # 2) ENRIQUECIDO: métricas + creativo por ad_id, conservando ausencias
    enriquecido = []
    for m in metricas:
        c = cat.get(m['ad_id'], {})
        fila = dict(m)
        fila.update({
            'account_id': CUENTA, 'currency': MONEDA, 'timezone': ZONA, 'attribution': ATRIBUCION,
            'creative_id': c.get('creative_id'), 'object_type': c.get('object_type'),
            'body': c.get('body'), 'title': c.get('title'), 'call_to_action_type': c.get('call_to_action_type'),
            'image_url': c.get('image_url'), 'thumbnail_url': c.get('thumbnail_url'),
            'ad_preview_shareable_link': c.get('ad_preview_shareable_link'),
            'facebook_permalink_url': c.get('facebook_permalink_url'),
            'instagram_permalink_url': c.get('instagram_permalink_url'),
            'status': c.get('status'), 'effective_status': c.get('effective_status'),
            'ad_created_time': c.get('ad_created_time'), 'campaign_objective': c.get('campaign_objective'),
            'idea': idea_de(c), 'creativo_disponible': bool(c),
        })
        enriquecido.append(fila)
    (AQUI / 'facebook_ads_enriched.json').write_text(json.dumps(enriquecido, ensure_ascii=False, indent=1), encoding='utf-8')

    # 3) CREATIVOS
    catalogo = [{
        'ad_id': c['ad_id'], 'ad_name': c.get('ad_name'), 'creative_id': c.get('creative_id'),
        'campaign_id': c.get('campaign_id'), 'campaign_name': c.get('campaign'),
        'adset_id': c.get('adset_id'), 'adset_name': c.get('adset_name'),
        'formato': c.get('object_type'), 'texto_literal': c.get('body'), 'titulo_literal': c.get('title'),
        'cta': c.get('call_to_action_type'), 'imagen_url': c.get('image_url'), 'miniatura_url': c.get('thumbnail_url'),
        'vista_previa': c.get('ad_preview_shareable_link'), 'permalink_facebook': c.get('facebook_permalink_url'),
        'permalink_instagram': c.get('instagram_permalink_url'),
        'estado': c.get('status'), 'estado_efectivo': c.get('effective_status'), 'creado': c.get('ad_created_time'),
        'objetivo_campana': c.get('campaign_objective'), 'evento_optimizacion': c.get('adsset_optimization_goal'),
        'idea': idea_de(c),
        'nota': 'texto_literal y titulo_literal son del anuncio; la descripción visual no se redactó porque no se '
                'revisaron las piezas, solo se conservan sus URLs.',
    } for c in creativos]
    (AQUI / 'creativos.json').write_text(json.dumps(catalogo, ensure_ascii=False, indent=1), encoding='utf-8')

    # 4) NORMALIZADO
    COLS = ['ad_id', 'campaign_id', 'date_start', 'date_end', 'idea', 'account_id', 'currency', 'objective',
            'result_type', 'attribution', 'placement', 'audience', 'spend', 'impressions', 'link_clicks', 'results']
    filas, excluidas = [], defaultdict(list)
    ceros_explicitos = 0
    for m in metricas:
        ad = m['ad_id']
        c = cat.get(ad, {})
        obj_camp = m.get('objective')
        meta_obj = MAPEO.get(obj_camp)
        if not meta_obj:
            excluidas[f'objetivo {obj_camp} sin mapeo seguro'].append(ad); continue
        objetivo, metas_ok, result_type, campo = meta_obj
        if m.get('adsset_optimization_goal') not in metas_ok:
            excluidas[f'objetivo {obj_camp} con optimización {m.get("adsset_optimization_goal")}'].append(ad); continue
        idea = idea_de(c)
        if not idea:
            excluidas['sin texto del creativo, no se puede describir la idea'].append(ad); continue
        impresiones = float(m.get('impressions') or 0)
        if impresiones <= 0:
            excluidas['sin entrega ese día (0 impresiones)'].append(ad); continue

        res_v = m.get(campo)
        lc_v = m.get('link_clicks')
        if res_v is None:
            res_v, ceros_explicitos = 0, ceros_explicitos + 1
        if lc_v is None:
            lc_v, ceros_explicitos = 0, ceros_explicitos + 1
        filas.append({
            'ad_id': ad, 'campaign_id': m.get('campaign_id'), 'date_start': m['date'], 'date_end': m['date'],
            'idea': idea, 'account_id': CUENTA, 'currency': MONEDA, 'objective': objetivo,
            'result_type': result_type, 'attribution': ATRIBUCION, 'placement': 'mixed',
            'audience': limpiar(m.get('adset_name'), 80) or 'sin_nombre',
            'spend': round(float(m.get('spend') or 0), 2), 'impressions': int(impresiones),
            'link_clicks': int(float(lc_v)), 'results': int(float(res_v)),
        })
    with (AQUI / 'facebook_ads_normalizado.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(filas)

    resumen = {
        'filas_csv': len(filas), 'anuncios_csv': len({r['ad_id'] for r in filas}),
        'campanas_csv': len({r['campaign_id'] for r in filas}),
        'objetivos_csv': dict(Counter(r['objective'] for r in filas)),
        'filas_totales_extraidas': len(metricas), 'anuncios_totales': len({m['ad_id'] for m in metricas}),
        'creativos_con_texto': sum(1 for c in creativos if c.get('body')), 'creativos_totales': len(creativos),
        'excluidas': {k: {'filas': len(v), 'anuncios': len(set(v))} for k, v in excluidas.items()},
        'ceros_explicitos_por_accion_ausente': ceros_explicitos,
    }
    (AQUI / 'resumen_construccion.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
