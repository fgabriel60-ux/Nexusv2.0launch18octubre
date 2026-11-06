"""Flyer limpio -> Kling 5 s + diseño sonoro."""
import base64,json,os,time,urllib.request,urllib.error
from io import BytesIO
from pathlib import Path
from PIL import Image
ROOT=Path('/workspaces/visionagenciaIAV2.0'); HERE=ROOT/'entregables/mariano_flyers_kling_20260915'
ENV=ROOT/'visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env'
API='https://api.wavespeed.ai/api/v3'; MODEL='kwaivgi/kling-v2.6-pro/image-to-video'; SFX='mirelo-ai/sfx-1.6/video-to-video'
IMAGE=HERE/'fondo_flyer_1.png'; JOB=HERE/'kling_flyer_texto_job.json'; OUT=HERE/'FLYER_5S_TEXTO_ANIMADO_SIN_AUDIO.mp4'; SJOB=HERE/'sfx_flyer_job.json'; OUTSFX=HERE/'FLYER_5S_KLING_CON_SFX.mp4'
def key():
 for l in ENV.read_text().splitlines():
  if l.startswith('WAVESPEED_API_KEY='): return l.split('=',1)[1].strip().strip('"').strip("'")
 return ''
CAB={'Authorization':'Bearer '+key(),'Content-Type':'application/json'}
def uri(path):
 im=Image.open(path).convert('RGB'); im.thumbnail((1600,1600)); b=BytesIO(); im.save(b,'PNG'); return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
def post(model,body):
 req=urllib.request.Request(API+'/'+model,data=json.dumps(body).encode(),headers=CAB)
 try:
  with urllib.request.urlopen(req,timeout=300) as r:return json.load(r)['data']['id']
 except urllib.error.HTTPError as e: raise RuntimeError(e.read().decode()[:1500])
def wait(job,label):
 for i in range(300):
  req=urllib.request.Request(f'{API}/predictions/{job}/result',headers=CAB)
  with urllib.request.urlopen(req,timeout=60) as r:d=json.load(r).get('data') or {}
  if i%6==0: print(label,d.get('status'),flush=True)
  if d.get('status')=='completed': return d['outputs'][0]
  if d.get('status')=='failed': raise RuntimeError(label+' failed: '+str(d.get('error')))
  time.sleep(4)
 raise TimeoutError(label)
def fetch(url,path):
 with urllib.request.urlopen(url,timeout=600) as r:path.write_bytes(r.read())
def main():
 prompt=('Create a polished 5-second cinematic animation that starts clean and ends on the original flyer. Animate the exact final text and logos appearing in sequence, perfectly legible and locked to their positions.  from this clean real-estate flyer background. Preserve the exact composition, architecture, coastline, colors and vertical framing. Begin with a gentle forward camera push toward the central house, subtle layered parallax between foreground street, house facade, distant hills and ocean, slow natural leaves and barely moving clouds, warm late-afternoon sunlight gliding across the facade, refined lens flare near the horizon. End stable and premium. Do not add text, logos, numbers, prices, signs, watermarks, people, cars or new buildings. No warping, melting architecture, flicker, jitter or camera shake.')
 if OUT.exists(): print('Kling existe:',OUT)
 else:
  job=json.loads(JOB.read_text())['id'] if JOB.exists() else post(MODEL,{'image':uri(IMAGE),'end_image':uri(HERE/'flyer_1.jpg'),'prompt':prompt,'negative_prompt':'text, logo, watermark, letters, numbers, distorted architecture, melting, flicker, jitter, people, cars','duration':5,'sound':False})
  JOB.write_text(json.dumps({'id':job,'model':MODEL,'prompt':prompt},indent=2)); fetch(wait(job,'kling'),OUT); print('Kling listo',OUT)
 if OUTSFX.exists(): print('SFX existe:',OUTSFX); return
 sfx='Elegant cinematic real-estate reveal: soft airy whoosh following the forward camera push, distant coastal wind, subtle palm-leaf rustle, gentle warm shimmer as sunlight flare passes, quiet polished low impact on final settle. No music, voice or speech.'
 sj=json.loads(SJOB.read_text())['id'] if SJOB.exists() else post(SFX,{'video':uri(OUT),'prompt':sfx,'duration':5,'num_samples':1,'seed':-1})
 SJOB.write_text(json.dumps({'id':sj,'model':SFX,'prompt':sfx},indent=2)); fetch(wait(sj,'sfx'),OUTSFX); print('SFX listo',OUTSFX)
if __name__=='__main__': main()
