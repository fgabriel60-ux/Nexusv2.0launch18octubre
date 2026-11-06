"""Vigilante de fabelagabriel645 (Carlos, 29 oct): usar SOLO el crédito gratis ($30/mes). Al quedar menos de MARGEN de crédito, apaga el sandbox nexus-claude y detiene las apps efímeras.
Uso: nohup python3 vigilar_645.py > vigilante_645.log &   (el límite real hay que fijarlo también en modal.com → Settings → Usage & Billing)"""
import json, os, re, subprocess, time

CREDITO, MARGEN = 30.0, 0.5
ENV = dict(os.environ, MODAL_PROFILE='fabelagabriel645')


def modal(*a):
    r = subprocess.run(['modal', *a], env=ENV, capture_output=True, text=True)
    return r.stdout + r.stderr


def usado():
    t = modal('billing', 'summary')
    c = re.search(r'Credits:\s*-([\d.]+)', t); f = re.search(r'Billed Cost:\s*\$?([\d.]+)', t)
    return (float(c.group(1)) if c else 0.0), (float(f.group(1)) if f else 0.0)


def apagar():
    import modal as m
    try:
        m.Sandbox.from_name('nexus-claude', 'nexus-claude').terminate(); print('sandbox apagado', flush=True)
    except Exception as e:
        print('sandbox:', str(e)[:80], flush=True)
    for a in json.loads(modal('app', 'list', '--json') or '[]'):
        if a.get('state') == 'ephemeral':
            modal('app', 'stop', '-y', a['app_id']); print('detenida', a['description'], flush=True)


while True:
    cred, fact = usado()
    print(time.strftime('%H:%M:%S'), f'crédito usado ${cred:.2f} de ${CREDITO:.0f} · facturado ${fact:.2f}', flush=True)
    if cred >= CREDITO - MARGEN or fact > 0:
        os.environ['MODAL_PROFILE'] = 'fabelagabriel645'; apagar(); print('LÍMITE: crédito gratis agotado, todo detenido', flush=True); break
    time.sleep(180)
