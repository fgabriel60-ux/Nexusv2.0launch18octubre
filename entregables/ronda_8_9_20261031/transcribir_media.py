import json,subprocess
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
P=Path('entregables/ronda_8_9_20261031');manifest=json.loads((P/'media_manifest.json').read_text());out=P/'transcripciones_media.json';done=json.loads(out.read_text()) if out.exists() else {};m=None
for x in manifest:
 if x['type'] not in ('ptt','audio') or not x.get('ruta') or x['id'] in done:continue
 if m is None:m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=2)
 b=subprocess.run(['ffmpeg','-v','error','-i',x['ruta'],'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
 if not b:continue
 segs,info=m.transcribe(np.frombuffer(b,np.int16).astype(np.float32)/32768,language='es',vad_filter=True)
 done[x['id']]={'chat':x['chat'],'ruta':x['ruta'],'modelo':'Whisper medium CPU int8','segmentos':[{'inicio':s.start,'fin':s.end,'texto':s.text.strip()} for s in segs]}
 out.write_text(json.dumps(done,ensure_ascii=False,indent=2));print(x['chat'],x['id'],flush=True)
