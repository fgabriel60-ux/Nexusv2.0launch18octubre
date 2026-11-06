"""Reenvía a Carlos las 4 imágenes de la semana de Fernando que no salieron porque WhatsApp se desconectó."""
import sys, base64, time
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/entregables/continuacion_claude_20261025')
from enviar_videos_carlos import call, failures, find
from pathlib import Path
I = Path('/workspaces/Nexusv2.0launch18octubre/clientes/Fernando/posts_semana_20261028/imagenes')
P = [(I/'martes_historia.jpg', 'Martes · historia (agregar encuesta «Libreta / Excel» · «Sistema» en Instagram)'),
     (I/'miercoles_portada_reel.jpg', 'Miércoles · portada del reel v6 (7 pm)'),
     (I/'jueves_historia.jpg', 'Jueves · historia (agregar sticker de link a WhatsApp)'),
     (I/'viernes_oferta.jpg', 'Viernes · oferta (12 pm)')]
fin = time.time() + 1800
while time.time() < fin:
    try:
        st = find(call('/client/status'), 'instanceStatus')
    except Exception as e:
        st = str(e)
    print('estado', st, flush=True)
    if st == 'ready': break
    time.sleep(30)
else:
    print('WhatsApp no volvió en 30 min; no se envió nada'); sys.exit(1)
for p, c in P:
    r = call('/client/action/send-media', {'chatId': '44522318905388@lid', 'mediaBase64': base64.b64encode(p.read_bytes()).decode(), 'mediaName': p.name, 'mediaCaption': c, 'asDocument': False})
    print(failures(r) or 'ok', p.name, flush=True); time.sleep(6)
