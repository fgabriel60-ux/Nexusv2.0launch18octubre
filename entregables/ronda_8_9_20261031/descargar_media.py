import json,sys,time,urllib.request,mimetypes,re,shutil,datetime
from pathlib import Path
sys.path.insert(0,'herramientas');from wa import accion
P=Path('entregables/ronda_8_9_20261031');a=json.loads((P/'mensajes_normalizados.json').read_text());sel=[]
def add(n,pred,limit=None):
 xs=[x for x in a if x['chat']==n and pred(x)];sel.extend(xs[-limit:] if limit else xs)
add('Jesus_Puertas',lambda x:not x['fromMe'] and x['type']=='ptt',3)
add('Ignacio',lambda x:not x['fromMe'] and x['type']=='image' and x['t']>1792368000)
add('BYD_Rafael',lambda x:not x['fromMe'] and x['type'] in ['image','video'])
add('BYD_Rafael',lambda x:not x['fromMe'] and x['type']=='ptt',7)
add('Fernando',lambda x:not x['fromMe'] and x['type']=='audio',1)
add('Fernando',lambda x:not x['fromMe'] and x['type']=='image',2)
add('Guillermo',lambda x:not x['fromMe'] and x['type']=='ptt',3)
add('Guillermo',lambda x:x['fromMe'] and x['type']=='video' and 1793327100<x['t']<1793327700)
add('Lisbeth',lambda x:not x['fromMe'] and x['type']=='image',1)
add('Victor',lambda x:x['fromMe'] and x['type']=='video',2)
add('Tatuador',lambda x:not x['fromMe'] and x['type']=='video' and x['t']>1793380000)
add('Tatuador',lambda x:not x['fromMe'] and x['type']=='document')
add('Veronica',lambda x:not x['fromMe'] and x['type']=='ptt',2)
add('Blanca',lambda x:not x['fromMe'] and x['type']=='ptt',1)
# Índice local por fecha: permite reutilizar archivos ya descargados sin otra consulta a WaAPI.
local=list(Path('clientes').rglob('*'))+list(Path('entregables').glob('**/*.ogg'))
local=[p for p in local if p.is_file() and P not in p.parents]
records=[];mf=P/'media_manifest.json'
old={x['id']:x for x in json.loads(mf.read_text())} if mf.exists() else {}
for i,x in enumerate(sel):
 if x['id'] in old and old[x['id']].get('ruta') and Path(old[x['id']]['ruta']).exists():records.append(old[x['id']]);continue
 d=x['data'];dt=datetime.datetime.fromtimestamp(x['t'],datetime.timezone.utc);dest=P/'media'/x['chat'];dest.mkdir(parents=True,exist_ok=True)
 rec={k:x[k] for k in ['chat','id','fromMe','type','t']};rec['fecha_utc']=dt.isoformat();rec['caption']=d.get('caption','');rec['filename_original']=d.get('filename','')
 patterns=[dt.strftime('%m%d_%H%M%S'),dt.strftime('%d_%H%M%S'),dt.strftime('%Y%m%d_%H%M%S')]
 candidates=[p for p in local if any(t in p.name for t in patterns) and (x['chat'].split('_')[0].lower() in str(p).lower() or x['chat']=='Tatuador' and 'Tatuador' in str(p))]
 if candidates:
  src=candidates[0];target=dest/(dt.strftime('%Y%m%d_%H%M%S')+'_'+x['id'].split('_')[-1]+src.suffix);shutil.copy2(src,target);rec.update(ruta=str(target.resolve()),origen_local=str(src.resolve()),estado='copiado local, fecha coincidente')
 else:
  try:
   r=accion('download-media',{'messageId':x['id']});m=((r or {}).get('data',{}).get('data',{}) or {}).get('media',{})
   if not m.get('url'):raise RuntimeError('API no devolvió URL de media')
   ext=Path(d.get('filename','')).suffix or mimetypes.guess_extension(m.get('mimetype','').split(';')[0]) or {'ptt':'.ogg','audio':'.ogg','image':'.jpg','video':'.mp4'}.get(x['type'],'.bin')
   target=dest/(dt.strftime('%Y%m%d_%H%M%S')+'_'+x['id'].split('_')[-1]+ext)
   with urllib.request.urlopen(m['url'],timeout=100) as f:blob=f.read(210*1024*1024+1)
   if len(blob)>210*1024*1024:raise RuntimeError('media supera 210 MB')
   target.write_bytes(blob);rec.update(ruta=str(target.resolve()),estado='descargado WaAPI',bytes=len(blob))
  except Exception as e:rec.update(ruta=None,estado='falló: '+str(e))
  time.sleep(6)
 records.append(rec);mf.write_text(json.dumps(records,ensure_ascii=False,indent=2));print(i+1,len(sel),x['chat'],rec['estado'],flush=True)
print('FIN',len(records),flush=True)
