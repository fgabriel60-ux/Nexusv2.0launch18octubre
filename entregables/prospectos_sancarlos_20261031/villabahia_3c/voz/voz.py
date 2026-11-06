import os,subprocess,numpy as np,requests,json,re,unicodedata
from faster_whisper import WhisperModel
K=os.environ['FISH_API_KEY']; ID='5e816f5a0658460b960881a24733c418'
F=["Villa Bahía, en San Carlos. Vista al mar y al cerro Tetakawi.","Balcón con terraza, sala de madera, cocina con barra y dos recámaras.","Reserva tu fin de semana por WhatsApp."]
def norm(t):
    t=unicodedata.normalize('NFD',t.lower()); t=''.join(c for c in t if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9 ]','',t).split()
m=WhisperModel('medium',compute_type='int8')
res={}
for i,f in enumerate(F):
    best=None
    for k,mod in enumerate(['s2-pro','s2-pro','s1','s1']):
        r=requests.post('https://api.fish.audio/v1/tts',headers={'Authorization':'Bearer '+K,'model':mod},json={'text':f.replace('WhatsApp','uatsap'),'format':'wav','reference_id':ID},timeout=120)
        p=f'f{i}_{k}.wav'; open(p,'wb').write(r.content)
        au=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768; s,_=m.transcribe(au,language='es'); t=' '.join(x.text for x in s)
        a,b=norm(f.replace('WhatsApp','whatsapp')),norm(t.replace('WhatsApp','whatsapp'))
        ok=sum(1 for w in a if w in b)/len(a)
        print(i,k,mod,round(ok,2),t,flush=True)
        if best is None or ok>best[0]: best=(ok,p,t)
    res[i]=best
    os.system(f'cp {best[1]} f{i}.wav')
json.dump(res,open('elegidas.json','w'),ensure_ascii=False,indent=1)
