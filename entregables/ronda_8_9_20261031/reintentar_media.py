import sys,json,time,urllib.request
from pathlib import Path
sys.path.insert(0,'herramientas');from wa import accion
P=Path('entregables/ronda_8_9_20261031');f=P/'media_manifest.json';items=json.loads(f.read_text());errors=[]
for x in items:
 if x.get('ruta'):continue
 for i in range(2):
  r=accion('download-media',{'messageId':x['id']});data=(r or {}).get('data',{});m=(data.get('data',{}) or {}).get('media',{})
  if m.get('url'):
   try:
    dest=P/'media'/x['chat']/(x['filename_original'] or 'media_recuperada.bin')
    with urllib.request.urlopen(m['url'],timeout=150) as resp:dest.write_bytes(resp.read())
    x.update(ruta=str(dest.resolve()),estado='descargado WaAPI tras reintento',bytes=dest.stat().st_size);break
   except Exception as e:errors.append(str(e))
  else:
   errors.append({'intento':i+1,'status':data.get('status'),'message':data.get('message'),'response_keys':list((r or {}).keys()),'data_keys':list(data.keys())})
  time.sleep(6)
 x['reintentos']=errors
f.write_text(json.dumps(items,ensure_ascii=False,indent=2));(P/'reintentos_media.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2));print('pendientes',sum(not x.get('ruta') for x in items))
