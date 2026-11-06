"""Crea/reutiliza un sandbox nocturno de ChatGPT en carlosfavelajeje."""
import json
import os
from pathlib import Path
os.environ['MODAL_PROFILE'] = 'carlosfavelajeje'
import modal
BASE = Path(__file__).resolve().parent
ROOT = '/workspaces/Nexusv2.0launch18octubre'
REMOTE = '/vol' + ROOT + '/entregables/chatgpt_modal_noche_20261101'
vol = modal.Volume.from_name('nexus-workspace')
app = modal.App.lookup('nexus-chatgpt-noche', create_if_missing=True)
try:
    sb = modal.Sandbox.from_name('nexus-chatgpt-noche', 'chatgpt-noche')
    print(json.dumps({'sandbox_id': sb.object_id, 'reutilizado': True}), flush=True)
except modal.exception.NotFoundError:
    with vol.batch_upload(force=True) as batch:
        for name in ['encargo.md', 'supervisor.py']:
            batch.put_file(BASE / name, REMOTE.removeprefix('/vol') + '/' + name)
    image = (modal.Image.from_registry('node:22-bookworm-slim', add_python='3.12')
        .apt_install('ffmpeg', 'git', 'curl', 'ripgrep', 'fonts-dejavu-core', 'fonts-liberation', 'libgomp1')
        .run_commands('npm install -g @openai/codex@0.166.0')
        .pip_install('modal', 'requests', 'pillow', 'numpy', 'faster-whisper', 'python-dotenv', 'soundfile', 'scipy', 'opencv-python-headless'))
    bootstrap = ('set -eu\nmkdir -p /workspaces\n'
                 f'ln -s /vol{ROOT} {ROOT}\n'
                 f'cd {ROOT}\n'
                 f'exec python3 -u {REMOTE}/supervisor.py >> {REMOTE}/supervisor.log 2>&1\n')
    with modal.enable_output():
        sb = modal.Sandbox.create('bash', '-c', bootstrap, app=app, name='chatgpt-noche',
            image=image, timeout=11 * 3600, cpu=1, memory=4096,
            volumes={'/vol': vol}, secrets=[modal.Secret.from_name('nexus-env')],
            env={'CODEX_HOME': '/vol/claude-config/codex', 'GASTO_PERFIL': 'carlosfavelajeje'})
    data = {'sandbox_id': sb.object_id, 'cuenta': 'carlosfavelajeje', 'timeout_horas': 11}
    (BASE / 'sandbox.json').write_text(json.dumps(data, indent=2))
    print(json.dumps(data), flush=True)
