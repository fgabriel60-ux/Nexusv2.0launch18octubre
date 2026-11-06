from pathlib import Path
import json,subprocess,concurrent.futures
from PIL import Image
P=Path('entregables/ronda_8_9_20261031')
def check(f):
 try:
  if not f.stat().st_size:return {'ruta':str(f),'ok':False,'error':'vacío'}
  if f.suffix.lower() in ['.jpg','.jpeg','.png','.webp']:
   with Image.open(f) as im:im.verify()
  else:
   r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)],capture_output=True,text=True,timeout=30)
   if r.returncode or not r.stdout.strip():return {'ruta':str(f),'ok':False,'error':r.stderr[-300:]}
  return {'ruta':str(f),'ok':True,'bytes':f.stat().st_size}
 except Exception as e:return {'ruta':str(f),'ok':False,'error':str(e)}
fs=list((P/'media').glob('**/*'));fs=[f for f in fs if f.is_file()]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(check,fs))
(P/'verificacion_media.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('archivos',len(rows),'correctos',sum(x['ok'] for x in rows),'fallidos',[(x['ruta'],x.get('error')) for x in rows if not x['ok']])
