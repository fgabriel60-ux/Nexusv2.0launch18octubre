"""Prueba endpoints de waapi para bajar el media de un mensaje de voz."""
import json
from pathlib import Path
from leer_chat import accion

AQUI = Path(__file__).resolve().parent
res = json.loads((AQUI / 'crudo_mensajes.json').read_text())
audios = [it['message']['_data'] for it in res['data']['data']
          if it['message']['_data'].get('type') in ('ptt', 'audio')]
mid = audios[0]['id']['_serialized']
print('mensaje de prueba:', mid, audios[0].get('duration'), 's')

for nombre, cuerpo in [
    ('get-message-by-id', {'messageId': mid}),
    ('download-media', {'messageId': mid}),
    ('get-media', {'messageId': mid}),
    ('download-message-media', {'messageId': mid}),
]:
    r = accion(nombre, cuerpo)
    if r.get('_http_error'):
        print(f'{nombre:28} HTTP {r["_http_error"]}  {r["_body"][:120]}')
    else:
        s = json.dumps(r, ensure_ascii=False)
        print(f'{nombre:28} OK  len={len(s)}  {s[:200]}')
