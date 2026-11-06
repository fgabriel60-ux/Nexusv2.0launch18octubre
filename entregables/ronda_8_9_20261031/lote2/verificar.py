from pathlib import Path
import subprocess,json,numpy as np
from faster_whisper import WhisperModel
R=Path.cwd();D=Path(__file__).resolve().parent
paths=['clientes/Giovanni/Giovanni_video_v5b.mp4','clientes/Tatuador9983316522/hardcut_v1b/Tatuador_hardcut_v1b.mp4','entregables/jesus_puertas_20261028/Jesus_carpinteria_v4.mp4','clientes/Victor/video/Servilin_obra_fina_v7b.mp4']
model=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4)
for p in paths:
 name=Path(p).stem
 subprocess.run(['ffmpeg','-v','error','-y','-i',p,'-vf','fps=2,scale=120:-1,tile=10x7','-frames:v','1',str(D/f'{name}_hoja.jpg')],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',p,'-f','null','-'],check=True)
 b=subprocess.check_output(['ffmpeg','-v','error','-i',p,'-f','s16le','-ac','1','-ar','16000','-'])
 seg,info=model.transcribe(np.frombuffer(b,np.int16).astype(np.float32)/32768,language='es',word_timestamps=True,vad_filter=True)
 data=[dict(text=s.text,start=s.start,end=s.end,words=[dict(word=w.word,start=w.start,end=w.end) for w in s.words]) for s in seg]
 (D/f'{name}_whisper.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print(name,' '.join(s['text'] for s in data),flush=True)
