import base64,json,urllib.request
from pathlib import Path
root=Path('/workspaces/visionagenciaIAV2.0'); here=root/'entregables/mariano_flyers_kling_20260915'; env={}
for line in (root/'visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env').read_text().splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  k,v=line.split('=',1);env[k.strip()]=v.strip().strip('"').strip("'")
file=here/'FLYER_5S_TEXTO_ANIMADO_CON_SFX.mp4'
body={'chatId': ''.join(c for c in env.get('CARLOS_TEL','5216312470486') if c.isdigit())+'@c.us','mediaBase64':base64.b64encode(file.read_bytes()).decode(),'mediaName':file.name,'asDocument':False,'mediaCaption':'Versión corregida · texto aparece y termina en el flyer original · Kling 5 s + SFX'}
url=env['WAAPI_BASE']+'/instances/'+env['WAAPI_INSTANCE']+'/client/action/send-media'
req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+env['WAAPI_TOKEN'],'Content-Type':'application/json'})
with urllib.request.urlopen(req,timeout=300) as r: result=json.load(r)
(here/'recibo_whatsapp_flyer.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
