"""Intenta bajar los audios (ptt) del chat 360 Salud para transcribirlos."""
import json, base64
from pathlib import Path
from leer_chat import accion

AQUI = Path(__file__).resolve().parent
CHAT = '31606932787332@lid'

res = json.loads((AQUI / 'crudo_mensajes.json').read_text())
audios = [it for it in res['data']['data']
          if it['message']['_data'].get('type') in ('ptt', 'audio')]
print(f'{len(audios)} audios en el hilo')
print('media en el primero:', repr(audios[0].get('media'))[:200])

# probar variantes de la peticion con descarga de media
for cuerpo in ({'chatId': CHAT, 'limit': 60, 'downloadMedia': True},
               {'chatId': CHAT, 'limit': 60, 'media': True}):
    r = accion('fetch-messages', cuerpo)
    if r.get('_http_error'):
        print(list(cuerpo)[-1], '-> HTTP', r['_http_error'], r['_body'][:200])
        continue
    datos = (r.get('data') or {}).get('data') or []
    con = [it for it in datos
           if it['message']['_data'].get('type') in ('ptt', 'audio') and it.get('media')]
    print(list(cuerpo)[-1], f'-> {len(con)} audios con media')
    if con:
        (AQUI / 'crudo_con_media.json').write_text(json.dumps(r, ensure_ascii=False))
        print('guardado crudo_con_media.json')
        break
