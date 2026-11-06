"""Resume cada chat de negocio (desde el 28 sep) en líneas cortas: texto del cliente, mensajes clave tuyos, conteo de medios y audios transcritos (audios.json) → digest/<nombre>.txt"""
import json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
AQUI = Path(__file__).resolve().parent; MX = timezone(timedelta(hours=-7))
d = json.load(open(AQUI / 'chats_crudos.json'))
au = json.load(open(AQUI / 'audios.json')) if (AQUI / 'audios.json').exists() else {}
PERSONAL = {'Isa', 'Rosy', 'Stefani', 'Silvia', 'Lupita Ranchito', 'Bæ🪶🦋', 'EML💕', '😚', 'Paulina', 'Taxi Ejecutivo', '+52 631 247 0486'}
CLAVE = re.compile(r'\$|\d{3,}|pag|precio|cobr|transf|deposit|cuenta|mes|campa|anunc|video|vídeo|muestra|gratis|resultado|mensaje|cliente|plan|cotiz|interes|gracias|no gracias|después|luego', re.I)
(AQUI / 'digest').mkdir(exist_ok=True)
for cid, v in d.items():
    if v['nombre'] in PERSONAL or not v['msgs']: continue
    out, media = [], 0
    for m in v['msgs']:
        dia = datetime.fromtimestamp(m['t'], MX).strftime('%m-%d %H:%M'); q = 'YO' if m['yo'] else 'EL'
        if m['tipo'] in ('ptt', 'audio') and not m['yo']:
            out.append(f"{dia} EL(audio): {au.get(m['id'], '[audio sin transcribir]')[:400]}"); continue
        if m['tipo'] in ('image', 'video', 'album', 'document', 'sticker', 'ptt', 'audio'):
            if m['txt'] and m['yo']: out.append(f"{dia} YO[{m['tipo']}]: {m['txt'][:140]}")
            elif not m['yo'] and m['tipo'] in ('image', 'video', 'document'): media += 1; out.append(f"{dia} EL[{m['tipo']}] {m['txt'][:100]}")
            continue
        if m['tipo'] != 'chat' or not m['txt']: continue
        if m['yo'] and not CLAVE.search(m['txt']): continue
        out.append(f"{dia} {q}: {m['txt'][:220]}")
    # comprime líneas consecutivas EL[image]
    comp = []
    for l in out:
        if comp and 'EL[image]' in l and 'EL[image]' in comp[-1].split(' x')[0]:
            comp[-1] = re.sub(r'( x\d+)?$', lambda k: f" x{int(k.group(0)[2:] or 1) + 1}" if k.group(0) else ' x2', comp[-1], 1); continue
        comp.append(l)
    nombre = re.sub(r'[^\w+ ]', '', v['nombre'] or cid)[:40].strip().replace(' ', '_')
    (AQUI / 'digest' / f"{nombre}__{cid.split('@')[0]}.txt").write_text(f"# {v['nombre']} ({cid}) · {len(v['msgs'])} mensajes\n" + '\n'.join(comp))
print('ok')
