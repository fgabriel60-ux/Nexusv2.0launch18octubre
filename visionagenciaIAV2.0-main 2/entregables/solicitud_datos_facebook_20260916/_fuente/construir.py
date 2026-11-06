"""Arma los entregables de SOLICITUD_A_CLAUDE_DATOS_FACEBOOK.md a partir de las consultas guardadas en _fuente/.

Uso: python3 _fuente/construir.py   (desde la carpeta solicitud_datos_facebook_20260916)
"""
import csv, json, re, collections, glob, os
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F = RAIZ / '_fuente'
CUENTA, MONEDA, ZONA = '684865860329838', 'MXN', 'America/Tijuana'
ATRIB = '7d_click_1d_view'
EXTRAIDO = '2026-09-16'
C = 'actions_onsite_conversion_messaging_conversation_started_7d'
MSG_DEST = {'WHATSAPP', 'MESSENGER', 'MESSAGING_MESSENGER_WHATSAPP'}


def cargar(n):
    return json.load(open(F / n, encoding='utf-8'))


PAGINA_PROPIA = '112035195330595'  # Visión Agencia


def es_propio(c):
    """Solo anuncios publicados desde la página de Visión Agencia y que no promocionan a un cliente."""
    pagina = (c.get('effective_object_story_id') or '').split('_')[0]
    nombre = c.get('campaign') or ''
    return pagina == PAGINA_PROPIA and 'LEQ' not in nombre and 'Amy' not in nombre


cfg_todo = {x['ad_id']: x for x in cargar('q2_configuracion_creativos.json')['result']}
CAMPANAS_PROPIAS = {c['campaign_id'] for c in cfg_todo.values() if c.get('campaign') and es_propio(c)}
# las filas sin nombre de campaña (objetos sin entrega) solo cuentan si su campaña es propia
cfg = {a: c for a, c in cfg_todo.items() if c['campaign_id'] in CAMPANAS_PROPIAS and es_propio(c) or (not c.get('campaign') and c['campaign_id'] in CAMPANAS_PROPIAS)}
met_todo = cargar('q1_metricas_diarias.json')['result']
met = [m for m in met_todo if m['ad_id'] in cfg]
IDS_PROPIOS = {PAGINA_PROPIA, CUENTA} | {v for c in cfg.values() for v in (c['ad_id'], c['adset_id'], c['campaign_id'])}
IDS_AJENOS = {v for a, c in cfg_todo.items() if a not in cfg for v in (a, c['adset_id'], c['campaign_id'])}
seg_log = [x for x in cargar('q5_cambios_segmentacion_2026.json')['result'] if x['activity_object_id'] in IDS_PROPIOS]
assets = {a: t for a, t in cargar('q8_textos_por_asset.json')['result'].items() if a in cfg}
desc = {k: v for k, v in cargar('descripciones_visuales.json').items() if not k.startswith('_')}
descargas = cargar('descargas_creativos_log.json')


def fecha_hora(s):
    m = re.match(r'(\d+)/(\d+)/(\d{4}) a las? (\d+):(\d+)\W*([ap])', s)
    d, mo, y, h, mi, ap = m.groups()
    h = int(h) % 12 + (12 if ap == 'p' else 0)
    return datetime(int(y), int(mo), int(d), h, int(mi))


# ---------- objetivo ----------
def mapear(obj, opt, dest):
    if opt == 'CONVERSATIONS' and dest in MSG_DEST and obj in ('MESSAGES', 'OUTCOME_ENGAGEMENT'):
        return 'messages', 'conversacion_iniciada', C, None
    if opt == 'CONVERSATIONS' and dest in MSG_DEST and obj in ('LINK_CLICKS', 'OUTCOME_TRAFFIC'):
        return 'traffic', 'conversacion_iniciada', C, None
    if obj == 'LEAD_GENERATION' and opt == 'LEAD_GENERATION':
        return 'leads', 'lead', 'actions_lead', None
    if obj in ('LINK_CLICKS', 'OUTCOME_TRAFFIC') and opt == 'LINK_CLICKS':
        return 'traffic', 'link_click', 'link_clicks', None
    if obj in ('LINK_CLICKS', 'OUTCOME_TRAFFIC') and opt == 'LANDING_PAGE_VIEWS':
        return 'traffic', 'landing_page_view', 'actions_landing_page_view', None
    return None, None, None, f'objetivo {obj} + optimización {opt} + destino {dest}: sin mapeo seguro'


# ---------- audiencia por día desde el historial de segmentación ----------
CLAVES_AUD = ['Lugar:', 'Edad:', 'Edad mínima:', 'Idioma:', 'Intereses:', 'Personas que coinciden con:',
              'Público personalizado:', 'Público personalizado Advantage+:', 'Público similar Advantage+:',
              'Segmentación detallada Advantage+:', 'Público Advantage+:']


def etiqueta(spec):
    partes = []
    for it in spec:
        if it.get('content') in CLAVES_AUD:
            hijos = '/'.join(str(h) for h in it.get('children') or [])
            partes.append(f"{it['content'].rstrip(':')}={hijos}")
    return '; '.join(sorted(partes))


cambios = collections.defaultdict(list)
for x in seg_log:
    if x['activity_event_type'] != 'update_ad_set_target_spec':
        continue
    e = json.loads(x['activity_extra_data'] or '{}')
    cambios[x['activity_object_id']].append((fecha_hora(x['activity_date_time_in_timezone']), e.get('old_value') or [], e.get('new_value') or []))
for v in cambios.values():
    v.sort(key=lambda t: t[0])


def audiencia(adset_id, dia):
    evs = cambios.get(adset_id, [])
    if any(t.strftime('%Y-%m-%d') == dia and old for t, old, new in evs):
        return None, 'la segmentación cambió ese mismo día (el día mezcla dos configuraciones)'
    previos = [new for t, old, new in evs if t.strftime('%Y-%m-%d') <= dia]
    if not previos:
        return None, 'sin registro de segmentación vigente ese día'
    return etiqueta(previos[-1]), None


# ---------- textos e ideas ----------
def textos(ad):
    c = cfg.get(ad, {})
    if ad in assets:
        return assets[ad], 'body_asset_text'
    if c.get('body'):
        return [c['body']], 'body'
    return [], None


def idea(ad):
    c = cfg[ad]
    t, _ = textos(ad)
    d = desc.get(ad, {})
    visual = d.get('desc') if d.get('legible') else None
    if not t and not visual:
        return None
    partes = []
    if t:
        partes.append('Texto del anuncio: ' + re.sub(r'\s+', ' ', t[-1]).strip())
    else:
        partes.append('Texto del anuncio: no disponible en la API')
    if d:
        pre = '[Video: descripción solo de la miniatura; sin transcripción] ' if d['tipo'] == 'miniatura_video' or c['object_type'] == 'VIDEO' else ''
        partes.append('Visual: ' + pre + d['desc'])
    if c.get('title'):
        partes.append('Título: ' + c['title'])
    if c.get('call_to_action_type'):
        partes.append('CTA: ' + c['call_to_action_type'])
    return ' | '.join(partes)


def num0(v, impresiones):
    """Meta omite la acción cuando no ocurrió; con impresiones > 0 eso es 0 confirmado por la API."""
    if v is None:
        return (0, True) if impresiones > 0 else (None, False)
    return (v, False)


# ---------- 03 historial simulador ----------
filas, excl = [], collections.Counter()
excl_ads = collections.defaultdict(set)
ceros = 0
for m in sorted(met, key=lambda x: (x['date'], x['ad_id'])):
    ad = m['ad_id']; c = cfg[ad]
    razon = None
    obj, rtype, campo, r = mapear(c['campaign_objective'], c['adsset_optimization_goal'], c['adset_destination_type'])
    if (m['impressions'] or 0) == 0:
        razon = 'sin entrega ese día (0 impresiones)'
    elif r:
        razon = r
    aud, ra = audiencia(c['adset_id'], m['date'])
    if not razon and ra:
        razon = ra
    ide = idea(ad)
    if not razon and not ide:
        razon = 'sin texto ni visual legible: no se puede describir la idea sin inventarla'
    if razon:
        excl[razon] += 1; excl_ads[razon].add(ad); continue
    res, z1 = num0(m.get(campo), m['impressions'])
    lc, z2 = num0(m.get('link_clicks'), m['impressions'])
    ceros += z1 + z2
    filas.append(dict(ad_id=ad, campaign_id=m['campaign_id'], date_start=m['date'], date_end=m['date'], idea=ide,
                      account_id=CUENTA, currency=MONEDA, objective=obj, result_type=rtype, attribution=ATRIB,
                      placement='mixed', audience=aud, spend=f"{m['spend']:.2f}", impressions=m['impressions'],
                      link_clicks=lc, results=res))
CAB = ['ad_id', 'campaign_id', 'date_start', 'date_end', 'idea', 'account_id', 'currency', 'objective', 'result_type',
       'attribution', 'placement', 'audience', 'spend', 'impressions', 'link_clicks', 'results']
with open(RAIZ / '03_historial_simulador.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, CAB); w.writeheader(); w.writerows(filas)

# ---------- 02 original ----------
bundle = {'fuente': 'Windsor.ai, conector facebook (Meta Ads). Solo lectura.', 'extraido_el': EXTRAIDO, 'cuenta': CUENTA,
          'moneda': MONEDA, 'zona_horaria': ZONA,
          'atribucion_consultas': 'opción attribution_window=default del conector = ["7d_click","1d_view"]',
          'consultas': {}}
bundle['nota_filtro'] = ('Solo anuncios propios de Visión Agencia (página 112035195330595). Por instrucción del anunciante se '
                        'quitaron de esta exportación las campañas de clientes u otras páginas; los registros propios no se modificaron.')
for n in sorted(glob.glob(str(F / 'q*.json'))):
    d = json.load(open(n, encoding='utf-8'))
    for k in ('result',) if 'q9_' not in n else ():  # 2024: solo hubo anuncios de Visión Agencia
        if isinstance(d.get(k), list):
            d[k] = [x for x in d[k] if (x.get('ad_id') in cfg if 'ad_id' in x else (x.get('activity_object_id') or x.get('objeto_id')) in IDS_PROPIOS)] if 'ad_id' in (d[k][0] if d[k] else {}) or 'activity_object_id' in (d[k][0] if d[k] else {}) or 'objeto_id' in (d[k][0] if d[k] else {}) else d[k]
    bundle['consultas'][Path(n).stem] = d
json.dump(bundle, open(RAIZ / '02_historial_original.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
campos = list(met[0].keys())
with open(RAIZ / '02_historial_original_diario.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, campos); w.writeheader(); w.writerows(met)

# ---------- 04 creativos ----------
ads_met = sorted({m['ad_id'] for m in met})
archivos = collections.defaultdict(list)
for ad, campo, fn, n, ct, st in descargas:
    if ad in cfg and fn and os.path.exists(RAIZ / fn):
        archivos[ad].append(fn)
filas4 = []
for ad in ads_met:
    c = cfg[ad]; po = json.loads(c.get('adset_promoted_object') or '{}'); d = desc.get(ad, {})
    ts, fuente = textos(ad)
    for i, t in enumerate(ts or [None]):
        filas4.append(dict(
            ad_id=ad, variante=(i + 1) if ts else '', campaign_id=c['campaign_id'], adset_id=c['adset_id'],
            campaign_name=c['campaign'], adset_name=c['adset_name'], ad_name=c['ad_name'], creative_id=c['creative_id'],
            page_id=po.get('page_id', ''), formato=c['object_type'], creado=c['ad_created_time'], estado=c['effective_status'],
            objetivo_campana=c['campaign_objective'], optimizacion=c['adsset_optimization_goal'], destino_tipo=c['adset_destination_type'],
            whatsapp_destino=po.get('whatsapp_phone_number', ''), url_destino=c.get('website_destination_url') or '',
            texto_principal=t if t else 'no disponible', fuente_texto=fuente or 'no disponible',
            titulo=c.get('title') or 'no disponible', descripcion='no disponible (error #100 de Meta al pedir description_asset)',
            cta=c.get('call_to_action_type') or 'no disponible',
            tipo_visual=d.get('tipo', ''), visual_legible=d.get('legible', ''), descripcion_visual=d.get('desc', ''),
            transcripcion_video='no disponible (la API no entrega el archivo de video)' if c['object_type'] == 'VIDEO' or d.get('tipo') == 'miniatura_video' else 'no aplica',
            nota_visual='la imagen descargada es la miniatura de un video' if c['object_type'] == 'VIDEO' or d.get('tipo') == 'miniatura_video' else '',
            archivos=';'.join(sorted(archivos[ad])), vista_previa=c.get('ad_preview_shareable_link') or '',
            permalink_facebook=c.get('facebook_permalink_url') or '', permalink_instagram=c.get('instagram_permalink_url') or ''))
with open(RAIZ / '04_creativos.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(filas4[0].keys())); w.writeheader(); w.writerows(filas4)

# ---------- extras ----------
os.makedirs(RAIZ / 'extras', exist_ok=True)
def a_csv(nombre, filas_):
    with open(RAIZ / 'extras' / nombre, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(filas_[0].keys())); w.writeheader(); w.writerows(filas_)
a_csv('ubicaciones_anuncio_ganador.csv', cargar('q3_ubicaciones_ganadora.json')['result'])
a_csv('totales_periodo_ganador_y_video.csv', cargar('q6_totales_periodo_video_y_ganadora.json')['result'])
a_csv('compras_marcadas_en_chat.csv', [x for x in cargar('q10_compras_y_contactos.json')['result'] if x['ad_id'] in cfg])
a_csv('cambios_presupuesto_2026.csv', [x for x in cargar('q7_cambios_presupuesto.json')['result'] if x['objeto_id'] in IDS_PROPIOS])
seg_rows = []
for x in seg_log:
    e = json.loads(x['activity_extra_data'] or '{}')
    seg_rows.append(dict(fecha_hora=x['activity_date_time_in_timezone'], adset_id=x['activity_object_id'], adset=x['activity_object_name'],
                         antes=etiqueta(e.get('old_value') or []), despues=etiqueta(e.get('new_value') or []),
                         ubicaciones_despues=next((('/'.join(i['children'])) for i in e.get('new_value') or [] if i.get('content') == 'Ubicaciones:'), '')))
a_csv('cambios_segmentacion_2026.csv', seg_rows)
h = cargar('q9_historial_2024.json')
a_csv('historial_2024_diario.csv', h['metricas_diarias'])

# ---------- resumen para 05 ----------
ctx = collections.defaultdict(lambda: {'ads': set(), 'camps': set(), 'filas': 0, 'spend': 0.0, 'res': 0, 'ini': '9', 'fin': '0'})
camp_rng = collections.defaultdict(lambda: ['9', '0'])
for r in filas:
    k = (r['objective'], r['result_type'], r['audience'])
    z = ctx[k]; z['ads'].add(r['ad_id']); z['camps'].add(r['campaign_id']); z['filas'] += 1
    z['spend'] += float(r['spend']); z['res'] += r['results']
    cr = camp_rng[r['campaign_id']]; cr[0] = min(cr[0], r['date_start']); cr[1] = max(cr[1], r['date_start'])
previos = []
for r in filas:
    pass
por_camp = collections.defaultdict(set)
camp_ctx = {}
for r in filas:
    por_camp[r['campaign_id']].add(r['ad_id']); camp_ctx[r['campaign_id']] = (r['objective'], r['result_type'], r['audience'])
for cid, (o, rt, au) in camp_ctx.items():
    ini = camp_rng[cid][0]
    ant = {a for c2, ads in por_camp.items() if c2 != cid and camp_ctx[c2] == (o, rt, au) and camp_rng[c2][1] < ini for a in ads}
    ant_obj = {a for c2, ads in por_camp.items() if c2 != cid and camp_ctx[c2][:2] == (o, rt) and camp_rng[c2][1] < ini for a in ads}
    previos.append(dict(campaign_id=cid, nombre=cfg[next(iter(por_camp[cid]))]['campaign'], objetivo=o, evento=rt, inicio=ini, fin=camp_rng[cid][1],
                        anuncios=len(por_camp[cid]), anuncios_previos_mismo_contexto=len(ant), anuncios_previos_mismo_objetivo_evento_cualquier_audiencia=len(ant_obj)))
resumen = dict(
    filas_03=len(filas), anuncios_03=len({r['ad_id'] for r in filas}), campanas_03=len({r['campaign_id'] for r in filas}),
    filas_origen=len(met), anuncios_origen=len(ads_met), campanas_origen=len({m['campaign_id'] for m in met}),
    ajenos_quitados=dict(filas=len(met_todo) - len(met), anuncios=len({m['ad_id'] for m in met_todo}) - len(ads_met), campanas=len({m['campaign_id'] for m in met_todo}) - len({m['campaign_id'] for m in met})),
    rango_03=[min(r['date_start'] for r in filas), max(r['date_start'] for r in filas)],
    ceros_por_accion_omitida=ceros,
    excluidas={k: {'filas': v, 'anuncios': len(excl_ads[k])} for k, v in excl.items()},
    contextos=[dict(objective=k[0], result_type=k[1], audience=k[2], anuncios=len(z['ads']), campanas=len(z['camps']), filas=z['filas'],
                    gasto=round(z['spend'], 2), resultados=z['res']) for k, z in sorted(ctx.items(), key=lambda kv: (kv[0][0], kv[0][1], -len(kv[1]['ads'])))],
    historial_previo_por_campana=sorted(previos, key=lambda x: x['inicio']),
    por_objetivo=dict(collections.Counter((r['objective'], r['result_type']) for r in filas).items()),
    creativos_filas_04=len(filas4), anuncios_con_texto=sum(1 for a in ads_met if textos(a)[0]),
    anuncios_visual_legible=sum(1 for a in ads_met if desc.get(a, {}).get('legible')),
    anuncios_video=[a for a in ads_met if cfg[a]['object_type'] == 'VIDEO'],
    miniatura_video=[a for a in ads_met if desc.get(a, {}).get('tipo') == 'miniatura_video'],
)
resumen['por_objetivo'] = {f'{k[0]}/{k[1]}': v for k, v in resumen['por_objetivo'].items()}
json.dump(resumen, open(F / 'resumen_construccion.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in resumen.items() if k not in ('contextos', 'historial_previo_por_campana')}, ensure_ascii=False, indent=1))
