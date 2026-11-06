"""Baja y transcribe los audios que mandaron clientes y prospectos desde el 28 sep (chats_crudos.json) → audios.json {msg_id: texto}. Reanuda si se corta."""
import json, subprocess, sys, time, urllib.request
from pathlib import Path
import numpy as np
sys.path.insert(0, '/tmp/claude-0'); from wa import accion
from faster_whisper import WhisperModel
AQUI = Path(__file__).resolve().parent
d = json.load(open(AQUI / 'chats_crudos.json'))
SAL = AQUI / 'audios.json'; hechos = json.load(open(SAL)) if SAL.exists() else {}
m = WhisperModel('small', device='cpu', compute_type='int8')
PERSONAL = {'Isa', 'Rosy', 'Stefani', 'Silvia', 'Lupita Ranchito', 'Bæ🪶🦋', 'EML💕', '😚', 'Paulina', 'Hija Alberto'}
for cid, v in d.items():
    if v['nombre'] in PERSONAL: continue
    for x in v['msgs']:
        if x['yo'] or x['tipo'] not in ('ptt', 'audio') or x['id'] in hechos: continue
        u = None
        for _ in range(3):
            r = accion('download-media', {'messageId': x['id']}); u = (((r or {}).get('data') or {}).get('data') or {}).get('media', {}).get('url')
            if u: break
            time.sleep(8)
        if not u: hechos[x['id']] = '[no se pudo bajar]'; continue
        try:
            b = urllib.request.urlopen(u, timeout=120).read()
            pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', '-', '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], input=b, capture_output=True).stdout
            s, _ = m.transcribe(np.frombuffer(pcm, np.int16).astype(np.float32) / 32768, language='es')
            hechos[x['id']] = ' '.join(t.text.strip() for t in s)
        except Exception as e:
            hechos[x['id']] = f'[error {e}]'
        json.dump(hechos, open(SAL, 'w'), ensure_ascii=False); print(v['nombre'], len(hechos), flush=True)
        time.sleep(5)
print('FIN', len(hechos))
