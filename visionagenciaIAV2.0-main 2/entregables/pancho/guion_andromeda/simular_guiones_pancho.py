"""Guiones de Pancho Mecanico en el simulador de Andromeda Lab (engine.run), con el mismo
historial y contexto de la campana ganadora (entrada_motor.json). No publica nada."""
import copy, json, sys
from pathlib import Path

ROOT = Path('/workspaces/visionagenciaIAV2.0')
LAB = ROOT / 'visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/andromeda-lab'
sys.path.insert(0, str(LAB))
from engine import run

OUT = Path(__file__).resolve().parent
base = json.loads((ROOT / 'entregables/propuesta_agencia_20260916/entrada_motor.json').read_text())

FORMATO = (' Formato: video vertical 9:16 de unos 20 segundos con la voz clonada de Pancho, el mecanico, '
           'caminando hacia la camara en su taller real. CTA: Enviar mensaje por WhatsApp. '
           'Saludo: Hola Pancho, te mando foto de mi carro.')
GUIONES = {
    'ACTUAL (historia)': (
        'Aprendi a reparar en el taller de mi papa con prueba y error. Un carro no se arregla con piezas '
        'caras, se arregla con quien entiende. Por eso no cambio partes al azar. Te digo que tiene y te lo '
        'dejo andando. Manda foto por WhatsApp y te paso el precio hoy.'),
    'A · Antes de pagar': (
        'Te quieren cambiar medio carro? Antes de pagar, escuchame. Hay talleres que cambian piezas hasta '
        'atinarle, y tu pagas cada intento. Yo primero encuentro la falla. Aqui un carro se arregla '
        'entendiendolo, no cambiandole todo. Mandame por WhatsApp una foto o un '
        'audio del ruido, y hoy te digo que tiene y cuanto cuesta.'),
    'B · Ese ruido': (
        'Ese ruido no se va a quitar solo, y cada semana sale mas caro. Grabalo con tu celular y mandamelo '
        'por WhatsApp. Yo lo escucho y te digo que es, antes de que toques un peso. Soy Pancho, mecanico. '
        'Te digo que tiene, cuanto cuesta, y te lo dejo andando.'),
    'C · La regla del taller': (
        'En mi taller hay una regla: si no sabes que tiene el carro, no le cambies nada. Asi trabajo. '
        'Primero encuentro la falla, luego te digo el precio, y solo cambio lo que de verdad falla. Tu '
        'decides con el precio en la mano. Manda foto por WhatsApp y hoy mismo te paso el precio.'),
}

resultados = []
for nombre, texto in GUIONES.items():
    p = copy.deepcopy(base)
    p['ideas'] = [{'name': nombre, 'text': 'Guion de voz: ' + texto + FORMATO}]
    p['settings'].update(budget=966.63, days=19, seed=42, allocation='equal', tolerance=0)
    r = run(p)
    assert r['status'] == 'ok', r
    i = r['ideas'][0]
    resultados.append({'guion': nombre, 'texto': texto, 'conversaciones': i['results'], 'costo': i['cpa'],
                       'evidencia': i.get('evidence'), 'vecinos': i.get('neighbors', [])[:2]})
val = r['validation']
json.dump({'validacion': val, 'avisos': r['warnings'], 'resultados': resultados},
          open(OUT / 'resultado_simulacion.json', 'w'), ensure_ascii=False, indent=2)
print('modelo textual activo:', val.get('text_model_enabled'))
for x in resultados:
    n, c = x['conversaciones'], x['costo']
    print(f"{x['guion']:28s} conv {n['median']:.0f} ({n['p10']:.0f}-{n['p90']:.0f})  costo {c['median']:.2f} ({c['p10']:.2f}-{c['p90']:.2f})  | {x['evidencia']}")
