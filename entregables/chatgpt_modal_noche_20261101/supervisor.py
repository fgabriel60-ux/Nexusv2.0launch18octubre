"""Supervisor secuencial de Codex; corre dentro de Modal con estado persistente."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path('/workspaces/Nexusv2.0launch18octubre')
OUT = ROOT / 'entregables/chatgpt_modal_noche_20261101'
OUT.mkdir(parents=True, exist_ok=True)
lock = (OUT / 'supervisor.lock').open('w')
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit('Ya hay supervisor activo')

def estado(**data):
    data['fecha_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    tmp = OUT / 'supervisor_estado.tmp'
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    tmp.replace(OUT / 'supervisor_estado.json')
    print(json.dumps(data, ensure_ascii=False), flush=True)

env = os.environ.copy()
env['CODEX_HOME'] = '/vol/claude-config/codex'
env['GASTO_PERFIL'] = 'carlosfavelajeje'
env['MODAL_PROFILE'] = 'carlosfavelajeje'
encargo = (OUT / 'encargo.md').read_text()
deadline = time.monotonic() + 10 * 3600
estado(estado='arrancando', pid=os.getpid(), orden=['lisbeth', 'doctora', 'fernando'])
for cliente in ['lisbeth', 'doctora', 'fernando']:
    for intento in range(1, 4):
        remaining = deadline - time.monotonic()
        if remaining < 120:
            estado(estado='limite_nocturno', cliente=cliente)
            raise SystemExit(0)
        resultado = OUT / f'{cliente}_resultado.json'
        if resultado.exists():
            try:
                r = json.loads(resultado.read_text())
                if (r.get('completo') and r.get('enviado_carlos')
                    and isinstance(r.get('calificacion_actual'), (float, int))
                    and r['calificacion_actual'] >= 8
                    and Path(r.get('video', '')).is_file()
                    and Path(r.get('glimmer_log', '')).is_file()):
                    estado(estado='cliente_completo', cliente=cliente, resultado=str(resultado))
                    break
            except (ValueError, TypeError):
                pass
        prompt = encargo + f'\n\nCLIENTE ASIGNADO EN ESTA SESIÓN: {cliente}. Intento {intento}. Haz SOLO este cliente; retoma estado y logs sin duplicar producción/envíos. No termines con un plan. Ejecuta el trabajo y guarda el resultado con datos comprobados. Si una revisión Glimmer sigue corriendo, espérala y continúa. Si has agotado crédito o falta un dato indispensable, documenta el bloqueo y guarda resultado incompleto.\n'
        logpath = OUT / f'{cliente}_intento_{intento}.jsonl'
        with logpath.open('a') as log:
            p = subprocess.Popen(['codex', 'exec', '--skip-git-repo-check',
                '--dangerously-bypass-approvals-and-sandbox', '--json', '-C', str(ROOT), '-'],
                stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                env=env, cwd=ROOT, start_new_session=True, text=True)
            p.stdin.write(prompt)
            p.stdin.close()
            start = time.monotonic()
            estado(estado='trabajando', cliente=cliente, intento=intento, codex_pid=p.pid, log=str(logpath))
            while p.poll() is None:
                if time.monotonic() >= deadline or time.monotonic() - start > 3 * 3600:
                    os.killpg(p.pid, signal.SIGTERM)
                    try:
                        p.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(p.pid, signal.SIGKILL)
                        p.wait()
                    break
                time.sleep(15)
            estado(estado='sesion_terminada', cliente=cliente, intento=intento, codigo=p.returncode)
        tail = logpath.read_text(errors='replace')[-8000:].lower()
        if p.returncode and any(x in tail for x in ['usage limit', 'usage_limit', 'refresh_token_reused', 'authentication failed']):
            estado(estado='bloqueo_acceso_o_cuota', cliente=cliente, log=str(logpath))
            raise SystemExit(1)
        if resultado.exists():
            # El agente deja bloqueo concreto: pasar al siguiente en vez de repetir gasto.
            try:
                r = json.loads(resultado.read_text())
                if not r.get('completo') and r.get('pendiente'):
                    estado(estado='cliente_pendiente', cliente=cliente, detalle=r['pendiente'])
                    break
            except ValueError:
                pass
        time.sleep(10)
estado(estado='recorrido_terminado', carpeta=str(OUT))
