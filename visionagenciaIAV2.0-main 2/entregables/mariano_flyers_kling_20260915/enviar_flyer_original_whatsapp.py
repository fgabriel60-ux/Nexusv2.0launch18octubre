import base64,json,urllib.request
from pathlib import Path
root=Path('/workspaces/visionagenciaIAV2.0');here=root/'entregables/mariano_flyers_kling_20260915';env={}
for l in (root/'visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env').read_text().splitlines():
 if '=' in l and not l.startswith('#'):
  k,v=l.split('=',1);env[k.strip()]=v.strip().strip('"').strip("'")
f=here/'flyer_1.jpg';body={'chatId':env['CARLOS_TEL']+'@c.us','mediaBase64':base64.b64encode(f.read_bytes()).decode(),'mediaName':f.name,'asDocument':False,'mediaCaption':'Flyer original de Mariano · referencia completa con texto'}
u=env['WAAPI_BASE']+'/instances/'+env['WAAPI_INSTANCE']+'/client/action/send-media';req=urllib.request.Request(u,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+env['WAAPI_TOKEN'],'Content-Type':'application/json'})
with urllib.request.urlopen(req,timeout=300) as r: d=json.load(r)
(here/'recibo_whatsapp_original.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));print((d.get('data') or {}).get('status'))
