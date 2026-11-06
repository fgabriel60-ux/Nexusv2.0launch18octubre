"""Manda a Carlos (su chat consigo mismo) todo lo hecho el 27 oct 2026. Carlos lo pidió: «Mándame todo por WhatsApp». Guarda recibos y no repite lo aceptado."""
import base64, json, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/entregables/continuacion_claude_20261025')
from enviar_videos_carlos import call, failures
AQUI = Path(__file__).resolve().parent; R = Path('/workspaces/Nexusv2.0launch18octubre')
C = R / 'visionagenciaIAV2.0-main 2/entregables/cinthia_payan_logo_20261027'
DESTINO = '44522318905388@lid'
REC = AQUI / 'recibos.json'
PIEZAS = [
 ('texto', None, '*Entregas de hoy 27 oct* 📦\n1 Israel: guion para reenviar\n2 Guiones de la doctora\n3 Plan de Israel\n4-8 Cinthia: fondos, letras, logo y tarjeta animada\n9 Manuel v15\n10 Fernando v6\n11-15 Víctor: 4 videos «solo empresas» y filtro de empleo\nEn proceso: Fernando v7 y videos de referencia de la doctora.'),
 ('texto', None, (R / 'clientes/Israel/glimmer_101010_20261027/MENSAJE_PARA_ISRAEL.txt').read_text()),
 ('doc', R / 'clientes/Alberto/glimmer_101010_20261027/GUIONES_VENEERS_10_10_10.md', 'Doctora · guiones 10/10/10 de Glimmer (carillas, ortodoncia, tomografía, placas)'),
 ('doc', R / 'clientes/Israel/glimmer_101010_20261027/respuesta_final.md', 'Israel · plan de Glimmer para recrear los 3 reels'),
 ('media', C / 'tarjeta/comparacion_fondos.jpg', 'Cinthia · blanco / verde muy sutil / verde pastel (pidió ver el verde muy sutil)'),
 ('media', C / 'tarjeta/variantes_letra_verde.jpg', 'Cinthia · 3 letras: clásica, moderna, suave'),
 ('media', C / 'logos/logo_cinthia_b2p.png', 'Cinthia · logo con la peonía abierta del reverso'),
 ('media', C / 'tarjeta/tarjeta_cinthia_animada_verde.mp4', 'Cinthia · tarjeta digital animada con sonidos suaves (verde)'),
 ('media', C / 'tarjeta/tarjeta_cinthia_animada.mp4', 'Cinthia · tarjeta digital animada con sonidos suaves (blanca)'),
 ('media', R / 'clientes/XV/final/XV_reel_v15_voz_manuel.mp4', 'Manuel v15 · su voz limpia, escenas en orden del audio, subtítulos elegantes y logo Hunab Ku'),
 ('media', R / 'clientes/Fernando/video/Anegocios_Fernando_v6.mp4', 'Fernando v6 · plan 10/10/10 con su voz real (confirmar su WhatsApp de negocio en el cierre)'),
 ('media', R / 'clientes/Victor/video/Servilin_equipo_real_v1_cliente.mp4', 'Víctor 1/4 · Servicio para empresas · No es vacante'),
 ('media', R / 'clientes/Victor/video/Servilin_escenas_v2_cliente.mp4', 'Víctor 2/4 · Servicio para empresas · No es vacante'),
 ('media', R / 'clientes/Victor/video/Servilin_escenas_v2_sin_liquido_cliente.mp4', 'Víctor 3/4 · Servicio para empresas · No es vacante'),
 ('media', R / 'clientes/Victor/video/Servilin_obra_fina_v3_cliente.mp4', 'Víctor 4/4 · obra fina para empresas'),
 ('doc', R / 'clientes/Victor/FILTRO_EMPLEO.md', 'Víctor · texto del anuncio, mensaje de bienvenida y segmentación para filtrar buscadores de empleo'),
]
rec = json.loads(REC.read_text()) if REC.exists() else {}
for i, (tipo, ruta, texto) in enumerate(PIEZAS, 1):
    k = f'{i:02d}'
    if rec.get(k, {}).get('estado') == 'aceptado': continue
    try:
        if tipo == 'texto':
            r = call('/client/action/send-message', {'chatId': DESTINO, 'message': texto})
        else:
            assert ruta.stat().st_size < 16_000_000, ruta
            r = call('/client/action/send-media', {'chatId': DESTINO, 'mediaBase64': base64.b64encode(ruta.read_bytes()).decode(),
                                                   'mediaName': ruta.name, 'mediaCaption': texto, 'asDocument': tipo == 'doc'})
        err = failures(r)
        if err: raise RuntimeError(err)
        rec[k] = {'estado': 'aceptado', 'pieza': str(ruta or texto[:40])}; print('ok', k, ruta.name if ruta else 'texto', flush=True)
    except Exception as e:
        rec[k] = {'estado': 'error', 'error': str(e)[:300]}; print('ERROR', k, e, flush=True)
    REC.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    time.sleep(6)
