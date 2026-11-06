from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[1]
def ff(a):subprocess.run(['ffmpeg','-v','error','-y',*map(str,a)],check=True)
def tm(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
J=json.loads((D/'plan.json').read_text())
for j in J:
 n=j['n'];ass=(D/('Victor_v6c.ass' if n=='Victor' else 'Guillermo.ass')).read_text().splitlines();ass=[l for l in ass if not l.startswith('Dialogue: 2,')]
 # Segmentación por frase: evita unir el final de una oración con el inicio de otra.
 old=json.loads((D/f'{n}_tomas.json').read_text());take=next(t for t in old if Path(t['path']).name==f'{n}_toma0.wav');words=[w.copy() for s in take['segments'] for w in s['words']];expected=j['text'].split()
 if len(words)==len(expected):
  for w,t in zip(words,expected):w['word']=t
 else:
  for w in words:w['word']=w['word'].strip().replace('saguán','zaguán').replace('saguanes','zaguanes').replace('Cervilín','Servilín')
 groups=[];group=[]
 for w in words:
  group.append(w)
  if len(group)==4 or w['word'].endswith(('.', '?','!')):groups.append(group);group=[]
 if group:groups.append(group)
 for group in groups:
  txt=' '.join('{\\kf%d}%s'%(max(1,round((w['end']-w['start'])*100)),w['word']) for w in group)
  ass.append(f"Dialogue: 2,{tm(group[0]['start'])},{tm(group[-1]['end'])},Default,,0,0,0,,{txt}")
 ap=D/f'{n}_final.ass';ap.write_text('\n'.join(ass))
 if n=='Victor':
  out=R/'clientes/Victor/video/Servilin_obra_fina_v6d.mp4';audio=R/'clientes/Victor/video/Servilin_obra_fina_v6b.mp4';vf=f'ass={ap}'
 else:
  out=R/'clientes/Guillermo/far12_v1/Vicens_far12_v4b_voz.mp4';audio=R/'clientes/Guillermo/far12_v1/Vicens_far12_v4_voz.mp4'
  # Breve fundido separa la vista de proceso de la vista de resultado de cielo azul.
  vf=f"fade=t=out:st=10.60:d=0.20,fade=t=in:st=10.80:d=0.20,ass={ap}"
 ff(['-i',D/f'{n}_base.mp4','-i',audio,'-vf',vf,'-map','0:v','-map','1:a','-c:v','libx264','-profile:v','main','-pix_fmt','yuv420p','-preset','veryfast','-crf','21','-c:a','copy','-shortest','-movflags','+faststart',out])
 j['video_final']=str(out);print(out,flush=True)
(D/'finales.json').write_text(json.dumps(J,ensure_ascii=False,indent=2))
