"""Manda un archivo con texto a CUALQUIER chat, con reintentos.
Uso: python3 herramientas/enviar_a.py CHAT_ID RUTA "texto"
Es `enviar_seguro.py` pero sin el chat de Carlos fijo. Ejemplos de chat:
Carlos 44522318905388@lid · Papá 161177321656327@lid (= 631 130 1667)
Un número suelto se convierte a chat con la acción `get-number-id`."""
import sys, os, base64, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wa import accion

chat, ruta, cap = sys.argv[1], sys.argv[2], sys.argv[3]
if '@' not in chat:  # vino un número: resolverlo primero
    r = accion('get-number-id', {'number': chat if chat.startswith('52') else '52' + chat})
    chat = r['data']['data']['numberId']['_serialized']
    print('chat resuelto:', chat)
b = base64.b64encode(open(ruta, 'rb').read()).decode()
for i in range(5):
    r = accion('send-media', {'chatId': chat, 'mediaBase64': b,
                              'mediaName': os.path.basename(ruta), 'mediaCaption': cap})
    if r and r.get('data', {}).get('status') == 'success':
        print('ok', ruta); break
    print('reintento', i + 1, json.dumps(r)[:200]); time.sleep(10 * (i + 1))
else:
    print('fallo', ruta)
