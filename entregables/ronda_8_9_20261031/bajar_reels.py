from pathlib import Path
import json,re,subprocess
P=Path('entregables/ronda_8_9_20261031');a=json.loads((P/'mensajes_normalizados.json').read_text());out=[]
for n in ['Ignacio','BYD_Rafael','Blanca']:
 for x in a:
  if x['chat']!=n or x['type']!='chat':continue
  for code in re.findall(r'instagram.com/reel/([A-Za-z0-9_-]+)',x['body']):
   d=P/'media'/n;d.mkdir(parents=True,exist_ok=True);target=d/(code+'.mp4');url='https://www.instagram.com/reel/'+code+'/'
   try:
    if not target.exists():
     r=subprocess.run(['yt-dlp','--no-playlist','--no-warnings','--retries','1','--socket-timeout','12','-f','best[ext=mp4]/best','-o',str(target),url],capture_output=True,text=True,timeout=65)
    else:r=None
    out.append({'cliente':n,'url_exacta_mensaje':x['body'],'id':x['id'],'ruta':str(target.resolve()) if target.exists() else None,'estado':'descargado' if target.exists() else 'No descargado: '+r.stderr[-700:]})
   except Exception as e:out.append({'cliente':n,'id':x['id'],'url':url,'ruta':None,'estado':str(e)})
   (P/'reels_descarga.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(n,code,out[-1]['estado'][:80],flush=True)
