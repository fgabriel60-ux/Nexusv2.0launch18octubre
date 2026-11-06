"""Manda los dos PDFs nuevos al WhatsApp de Carlos."""
import base64, json
from datetime import datetime
from pathlib import Path
from leer_chat import accion

AQUI = Path(__file__).resolve().parent
CARLOS = '5216312470486@c.us'
PIEZAS = [
    ('CARTEL_CAPSULAS_v4_CARTA.pdf', 'RarAmore_CAPSULAS_carta_v4.pdf',
     'Cartel de cápsulas con el frasco real, la ruedita de $1,392 y ¡POR TIEMPO LIMITADO!'),
    ('HOJA_BALSAMO_v5_CARTA.pdf', 'RarAmore_BALSAMO_carta_v5.pdf',
     'Hoja del bálsamo con el bote, la ruedita de $895 y ¡POR TIEMPO LIMITADO!. Los datos bancarios se quedaron, como pidió a las 11:29.'),
]

recibos = []
for archivo, nombre, pie in PIEZAS:
    ruta = AQUI / archivo
    r = accion('send-media', {
        'chatId': CARLOS,
        'mediaBase64': base64.b64encode(ruta.read_bytes()).decode(),
        'mediaName': nombre, 'asDocument': True, 'mediaCaption': pie})
    estado = ((r.get('data') or {}).get('data') or {}).get('status', r.get('data', {}).get('status'))
    print(nombre, '->', estado)
    recibos.append({'pieza': archivo, 'nombre': nombre, 'status': estado})

(AQUI / 'recibo_envio.json').write_text(json.dumps(
    {'pedido': 'Productos + ruedita de precio + tiempo limitado (Jesús, 17 sep)',
     'enviado_a': 'Carlos (%s)' % CARLOS, 'fecha': datetime.now().isoformat(timespec='seconds'),
     'piezas': recibos}, ensure_ascii=False, indent=2))
print('recibo_envio.json')
