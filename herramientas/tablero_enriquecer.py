"""Enriquece entregables/tablero/datos.json (4 nov 2026) con tres señales que Carlos pidió:
  trabajo  · cuántas veces se mencionó esa versión en TODAS las sesiones de Claude (sandbox de Modal + codespace)
             → la más mencionada es la que más se trabajó, que casi siempre es la que Carlos escogió
  enviado  · el último video que de verdad se le mandó al cliente por WhatsApp, con su texto y fecha
  hoy      · cuántos mensajes mandó el cliente hoy, y el último que escribió
Uso: python3 herramientas/tablero_enriquecer.py <trabajo.json> <barrido.json>
"""
import json, re, sys, datetime, pathlib

R = pathlib.Path('/workspaces/Nexusv2.0launch18octubre')
TZ = datetime.timezone(datetime.timedelta(hours=-7))
HOY = datetime.datetime.now(TZ).date()

# tablero → chat del barrido
CHATS = {'giovanni':'Giovanni','jesus-rimo':'Jesus_Puertas','victor-servilin':'Victor','ruben-quiropraxia':'Ruben',
 'fernando':'Fernando','mariano-vizcaino':'Mariano','guillermo-vicens':'Guillermo','tatuador':'Tatuador',
 'alberto-doctora-angeles':'Alberto','israel-sirled':'Israel','rafael':'BYD_Rafael','lisbeth':'Lisbeth',
 'andres':'Andres','ivan-fumicam':'Ivan','manuel-xv':'Manuel','uriel':'Uriel','jose-grupo-jr':'Jose',
 'adrian':'Tatuador','rachel':'Rachel','bd-pro':'BDPro','veronica':'Veronica','blanca':'Blanca'}


def tok(version):
    """token de versión: GIOVANNI_v5 → v5 ; 'v7i · 11-03' → v7i"""
    b = version.split(' · ')[0].strip()
    m = re.findall(r'v\d+[a-z]?', b, re.I)
    return m[-1].lower() if m else b.lower()


def main():
    trabajo_f, barrido_f = sys.argv[1:3]
    men = {}
    for k, n in json.loads(pathlib.Path(trabajo_f).read_text()).items():
        cli, _, ver = k.partition('||'); men[(cli, ver)] = n
    barrido = json.loads(pathlib.Path(barrido_f).read_text())

    datos = json.loads((R / 'entregables/tablero/datos.json').read_text())
    for c in datos:
        b = barrido.get(CHATS.get(c['slug'], ''), {})
        ue = b.get('ult_envio') or {}
        cap = (ue.get('cap') or ue.get('texto') or '').strip()
        if cap.startswith('/9j/'): cap = ''                   # base64 de una imagen, no es texto
        c['enviado'] = ({'fecha': datetime.datetime.fromtimestamp(ue['t'], TZ).strftime('%d/%m %H:%M'),
                         'texto': cap[:220]} if ue.get('t') else None)
        uc = b.get('ult_cliente') or {}
        c['cliente_ultimo'] = ({'fecha': datetime.datetime.fromtimestamp(uc['t'], TZ).strftime('%d/%m %H:%M'),
                                'texto': (uc.get('texto') or uc.get('tipo') or '')[:160]} if uc.get('t') else None)
        c['hoy'] = len(b.get('mensajes_cliente_hoy') or [])

        # señal de trabajo por versión + cuál se mandó
        tope = 0
        for v in c['versiones']:
            v['trabajo'] = men.get((c['cliente'], v['version']), 0)
            tope = max(tope, v['trabajo'])
            v['mandada'] = bool(cap) and tok(v['version']) in cap.lower()
        for v in c['versiones']:
            v['mas_trabajada'] = bool(tope) and v['trabajo'] == tope
        c['trabajo'] = tope
        # la elegida: la que se mandó; si no, la más trabajada con mejor nota
        eleg = [v for v in c['versiones'] if v.get('mandada')] or \
               sorted([v for v in c['versiones'] if v.get('mas_trabajada')],
                      key=lambda v: -(v.get('actual') or 0))
        c['elegida'] = eleg[0]['version'] if eleg else None

    (R / 'entregables/tablero/datos.json').write_text(json.dumps(datos, ensure_ascii=False))
    hablaron = [(c['cliente'], c['hoy']) for c in datos if c['hoy']]
    print('clientes:', len(datos), '· hablaron hoy:', sorted(hablaron, key=lambda x: -x[1]))
    for c in datos:
        print(f"  {c['cliente']:28s} elegida={str(c['elegida'])[:26]:28s} trabajo={c['trabajo']:4d} hoy={c['hoy']:2d}")


if __name__ == '__main__':
    main()
