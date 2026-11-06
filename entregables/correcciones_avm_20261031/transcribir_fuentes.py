from pathlib import Path
import subprocess,json,numpy as np
from faster_whisper import WhisperModel
D=Path(__file__).resolve().parent;R=D.parents[1]
m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4)
for name,p in [('manuel_completa',R/'clientes/XV/voz_manuel/voz_manuel_completa.ogg'),('manuel_cierre',R/'clientes/XV/voz_manuel/voz_manuel_cierre.ogg'),('victor',R/'entregables/victor_guillermo_20261031/Victor_toma0.wav')]:
 b=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','s16le','-ac','1','-ar','16000','-'])
 s,_=m.transcribe(np.frombuffer(b,np.int16).astype(np.float32)/32768,language='es',word_timestamps=True)
 a=[dict(text=x.text,start=x.start,end=x.end,words=[dict(word=w.word,start=w.start,end=w.end) for w in x.words]) for x in s]
 (D/f'{name}_fuente.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));print(name,a,flush=True)
