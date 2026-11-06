from pathlib import Path
import os,json,urllib.request,concurrent.futures,subprocess,re,difflib
from faster_whisper import WhisperModel
import numpy as np
ROOT=Path('/workspaces/Nexusv2.0launch18octubre'); D=ROOT/'entregables/jose_v9d_20261031'; A=ROOT/'clientes/Jose/armado_20261029'
env=dict(os.environ)
for l in ((ROOT/'.env').read_text().splitlines() if (ROOT/'.env').exists() else []):
 if '=' in l and not l.lstrip().startswith('#'):
  k,v=l.split('=',1);env[k.strip()]=v.strip().strip('\"\'')
m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4)
def tr(p):
 b=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True,check=True).stdout
 s,_=m.transcribe(np.frombuffer(b,np.int16).astype(np.float32)/32768,language='es',word_timestamps=True)
 return [{'text':x.text,'start':x.start,'end':x.end,'words':[{'word':w.word,'start':w.start,'end':w.end,'probability':w.probability} for w in x.words]} for x in s]
orig=tr(ROOT/'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9c.mp4');(D/'original_whisper.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2));print('ORIGINAL',orig,flush=True)
text='Mándanos fotos de tu azotea por WhatsApp y te cotizamos hoy.'
def gen(i):
 p=D/f'cierre_toma{i}.wav'
 if not p.exists():
  req=urllib.request.Request('https://api.fish.audio/v1/tts',data=json.dumps({'text':text,'format':'wav','reference_id':'74cae190c2c84b0caaca073f42f5de54'}).encode(),headers={'Authorization':'Bearer '+env['FISH_API_KEY'],'Content-Type':'application/json','model':'s2-pro'})
  p.write_bytes(urllib.request.urlopen(req,timeout=300).read())
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: paths=list(ex.map(gen,range(1,5)))
norm=lambda s:re.sub(r'[^a-záéíóúñü0-9]','',s.lower())
res=[]
for p in paths:
 t=tr(p); said=' '.join(x['text'] for x in t); words=[w for x in t for w in x['words']]; score=difflib.SequenceMatcher(None,norm(text),norm(said)).ratio();conf=sum(w['probability'] for w in words)/max(1,len(words));res.append({'file':str(p),'text':said,'match':score,'confidence':conf,'segments':t});print('TOMA',p.name,said,score,conf,flush=True)
(D/'tomas_whisper.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
best=max(res,key=lambda r:(r['match'],r['confidence']))
if best['match']<1:raise SystemExit('Ninguna toma coincide exactamente')
V=A/'voz_v9d';V.mkdir(exist_ok=True)
import shutil
for p in (A/'voz_v8').glob('*'): 
 if p.is_file():shutil.copy2(p,V/p.name)
subprocess.run(['ffmpeg','-v','error','-y','-i',best['file'],'-c:a','libmp3lame','-q:a','2',str(V/'s5_0.mp3')],check=True)
s=(A/'armar_jose_v9.py').read_text().replace("'tmp_v9c'","'tmp_v9d'").replace("'voz_v8'","'voz_v9d'").replace('Jose_GrupoJR_Pixar_obrero_v9c.mp4','Jose_GrupoJR_Pixar_obrero_v9d.mp4')
(A/'armar_jose_v9d.py').write_text(s);(D/'seleccion.json').write_text(json.dumps(best,ensure_ascii=False,indent=2))
print('ELEGIDA',best['file'],flush=True)
