"""Lee el chat de 360 Salud en WhatsApp via waapi.app y guarda lo de hoy."""
import json, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV = Path('/workspaces/Nexusv2.0launch18octubre/.env')

env = {}
for line in ENV.read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

BASE = 'https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/'


def accion(nombre, body=None):
    req = urllib.request.Request(
        BASE + nombre,
        data=json.dumps(body or {}).encode(),
        headers={'Authorization': 'Bearer ' + env['WAAPI_TOKEN'],
                 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {'_http_error': e.code, '_body': e.read().decode()[:500]}


if __name__ == '__main__':
    accion_pedida = sys.argv[1] if len(sys.argv) > 1 else 'get-chats'
    cuerpo = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    res = accion(accion_pedida, cuerpo)
    print(json.dumps(res, ensure_ascii=False, indent=2)[:4000])
