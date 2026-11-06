"""Recordatorio cada 10 min por WhatsApp (pedido de Carlos, 4 nov 2026): que elija en el
tablero el video mejor calificado de cada cliente. Se detiene solo al llegar al tope, o
cuando aparece el archivo de paro.

    nohup python3 herramientas/recordatorio_seleccion.py &        # arranca
    touch /tmp/claude-1000/parar_recordatorio                      # lo detiene
"""
import json, pathlib, sys, time
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/herramientas')
from wa import accion

CARLOS = '44522318905388@lid'
PARO = pathlib.Path('/tmp/claude-1000/parar_recordatorio')
TABLERO = 'https://charlyfavela666--tablero-nexus-web.us-east.modal.run/?k=i7_8usCbRdED_8lp'
DATOS = pathlib.Path('/workspaces/Nexusv2.0launch18octubre/entregables/tablero/datos.json')
CADA = 600
TOPE = 18          # 3 horas; después deja de insistir solo


def pendientes():
    """Clientes cuyo mejor video todavía no está elegido."""
    try:
        datos = json.loads(DATOS.read_text())
    except Exception:
        return []
    return [c['cliente'] for c in datos
            if c.get('tipo') == 'Cliente' and not c.get('elegido_por_carlos')]


def main():
    for i in range(1, TOPE + 1):
        if PARO.exists():
            accion('send-message', {'chatId': CARLOS, 'message': '🔕 Listo, ya no te recuerdo lo de elegir los videos.'})
            return
        faltan = pendientes()
        cuantos = len(faltan)
        lista = ', '.join(faltan[:6]) + ('…' if cuantos > 6 else '')
        msg = (f'⏰ Recordatorio {i}/{TOPE} · elige el video MEJOR CALIFICADO de cada cliente\n\n'
               f'{TABLERO}\n\n'
               f'Arriba de cada cliente está el mejor calificado con su plan para llegar a 8; '
               f'los demás quedan escondidos en «Ver las otras versiones».\n'
               f'Te faltan {cuantos}: {lista}\n\n'
               f'Dime «para los recordatorios» cuando ya no los quieras.')
        accion('send-message', {'chatId': CARLOS, 'message': msg})
        print('recordatorio', i, 'enviado', flush=True)
        time.sleep(CADA)


if __name__ == '__main__':
    main()
