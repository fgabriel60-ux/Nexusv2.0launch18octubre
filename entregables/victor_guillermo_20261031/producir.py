from pathlib import Path
import os,json,subprocess,urllib.request,concurrent.futures,re,unicodedata,difflib
import numpy as np
from faster_whisper import WhisperModel
R=Path('/workspaces/Nexusv2.0launch18octubre');D=R/'entregables/victor_guillermo_20261031'
J=[dict(n='Victor',id='fbea5ca5db5946f581a09678ae99f0a2',text='¿Eres constructora o desarrollador? En Servilín hacemos limpieza de obra fina para empresas. Retiramos polvo, cemento y restos de pintura. Limpiamos ventanas y pisos con personal uniformado, capacitado y supervisado. Tu obra lista para entregar. Solicita una propuesta por WhatsApp. Dinos qué tipo de inmueble y cuántos metros cuadrados.',out='clientes/Victor/video/Servilin_obra_fina_v6b.mp4',clips=['O1_piso','O3_aspirar','O2_ventanal','O5_listo'],cliente='Víctor · Servilin. Limpieza de obra fina PARA EMPRESAS, constructoras y desarrolladores. Personal uniformado, capacitado y supervisado. No es vacante. Sin precio confirmado. CTA WhatsApp con tipo de inmueble y m².'),dict(n='Guillermo',id='4f23cbd3089a4822b50eee260adb48f5',text='¿Tu casa necesita zaguán? En Puebla, Proyectos Metálicos Vicens hace zaguanes a la medida. Cuidamos los detalles, desde el armado hasta el acabado. Más de quince años de experiencia. Mándanos por WhatsApp una foto, las medidas y tu colonia para cotizar tu zaguán.',out='clientes/Guillermo/far12_v1/Vicens_far12_v4_voz.mp4',clips=['H_zaguan_se_arma','Z1_porton','H_zaguan_se_arma','N3_zaguan'],cliente='Guillermo · Proyectos Metálicos Vicens. Herrería en Puebla y alrededores, +15 años. Servicio principal en este anuncio: zaguanes a medida. WhatsApp 231 231 1066. Sin precio confirmado. Guion adaptado de recomendaciones de Glimmer 20261031b: gancho hablado, subtítulos palabra por palabra y un servicio principal. No se presenta como guion literal de Glimmer.')]
(D/'plan.json').write_text(json.dumps(J,ensure_ascii=False,indent=2))
def ff(args):subprocess.run(['ffmpeg','-v','error','-y','-threads','2',*map(str,args)],check=True)
def dur(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
def gen(t):
 j,i=t;p=D/f"{j['n']}_toma{i}.wav"
 if not p.exists():
  req=urllib.request.Request('https://api.fish.audio/v1/tts',data=json.dumps({'text':j['text'],'format':'wav','reference_id':j['id']}).encode(),headers={'Authorization':'Bearer '+os.environ['FISH_API_KEY'],'Content-Type':'application/json','model':'s2-pro' if i<2 else 's1'})
  p.write_bytes(urllib.request.urlopen(req,timeout=300).read())
 print('Generada',p.name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:list(e.map(gen,[(j,i) for j in J for i in range(4)]))
m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4)
def tr(p, prompt=None):
 b=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','s16le','-ac','1','-ar','16000','-'])
 s,_=m.transcribe(np.frombuffer(b,np.int16).astype(np.float32)/32768,language='es',word_timestamps=True,initial_prompt=prompt)
 return [dict(text=x.text,start=x.start,end=x.end,words=[dict(word=w.word,start=w.start,end=w.end,probability=w.probability) for w in x.words]) for x in s]
def norm(s):
 s=unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode().replace('15','quince').replace('saguan','zaguan').replace('cervilin','servilin')
 return re.sub('[^a-z0-9]','',s)
def tm(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
for j in J:
 cache=D/f"{j['n']}_tomas.json"
 results=json.loads(cache.read_text()) if cache.exists() else []
 for i in ([] if results else range(4)):
  p=D/f"{j['n']}_toma{i}.wav";s=tr(p,j['text']);said=' '.join(x['text'] for x in s);score=difflib.SequenceMatcher(None,norm(j['text']),norm(said)).ratio();results.append(dict(path=str(p),segments=s,said=said,match=score));print(j['n'],i,score,said,flush=True)
 (D/f"{j['n']}_tomas.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
 for x in results:x['match']=difflib.SequenceMatcher(None,norm(j['text']),norm(x['said'])).ratio()
 best=max(results,key=lambda x:(x['match'],np.mean([w['probability'] for s in x['segments'] for w in s['words']])))
 if best['match']<0.999:raise RuntimeError('Ninguna toma exacta: '+j['n'])
 voice=Path(best['path']);total=dur(voice)+.35
 words=[w.copy() for x in best['segments'] for w in x['words']]
 expected=j['text'].split()
 if len(words)==len(expected) and norm(' '.join(w['word'] for w in words))==norm(j['text']):
  for w,word in zip(words,expected):w['word']=word
 else:
  for w in words:w['word']=w['word'].replace('saguán','zaguán').replace('saguanes','zaguanes').replace('Cervilín','Servilín')
 ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 720','PlayResY: 1280','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Default,Montserrat,48,&H00FFFFFF,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4,1,2,48,48,280,1','Style: Title,Montserrat,38,&H00FFFFFF,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,3,2,0,8,35,35,85,1','Style: CTA,Montserrat,35,&H0066D325,&H0000D7FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,3,2,0,2,35,35,130,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
 # Three-word groups, karaoke highlighting one spoken word at a time.
 for k in range(0,len(words),3):
  group=words[k:k+3];text=' '.join('{\\kf%d}%s'%(max(1,round((w['end']-w['start'])*100)),w['word'].strip()) for w in group)
  ass.append(f"Dialogue: 2,{tm(group[0]['start'])},{tm(group[-1]['end'])},Default,,0,0,0,,{text}")
 title='SERVILIN · LIMPIEZA DE OBRA FINA\\NSOLO EMPRESAS · NO ES VACANTE' if j['n']=='Victor' else 'VICENS · ZAGUANES A LA MEDIDA\\NPUEBLA Y ALREDEDORES'
 cta='COTIZA POR WHATSAPP\\NTipo de inmueble + m²' if j['n']=='Victor' else 'WHATSAPP 231 231 1066\\NFoto + medidas + colonia'
 ass += [f'Dialogue: 1,0:00:00.00,{tm(total)},Title,,0,0,0,,{title}',f'Dialogue: 1,0:00:00.00,{tm(total)},CTA,,0,0,0,,{cta}']
 ap=D/f"{j['n']}.ass";ap.write_text('\n'.join(ass))
 seq=[]
 # Multiple short motion clips; last part shows finished work throughout CTA.
 for i in range(8):
  idx=min(i//2,3);name=j['clips'][idx];src=R/('clientes/Victor/video/v4' if j['n']=='Victor' else 'clientes/Guillermo/video/tomas_v3')/f'{name}.mp4'
  length=total/8;sp=dur(src);start=0 if i%2==0 else max(0,sp-length)
  out=D/f"{j['n']}_seg{i}.mp4"
  ff(['-stream_loop','-1','-ss',start,'-i',src,'-t',length,'-vf','scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=25,setsar=1','-an','-c:v','libx264','-preset','veryfast','-crf','21',out]);seq.append(out)
 lp=D/f"{j['n']}_lista.txt";lp.write_text(''.join(f"file '{p}'\n" for p in seq));base=D/f"{j['n']}_base.mp4";ff(['-f','concat','-safe','0','-i',lp,'-c','copy',base])
 music=R/'clientes/Guillermo/far12_v1/tmp/musica.wav'
 ff(['-i',base,'-i',voice,'-stream_loop','-1','-i',music,'-filter_complex',f'[0:v]ass={ap}[v];[1:a]apad,atrim=0:{total},loudnorm=I=-16:TP=-1.5[a];[2:a]volume=0.055,atrim=0:{total},afade=t=out:st={total-1}:d=1[b];[a][b]amix=inputs=2:duration=first:normalize=0[o]','-map','[v]','-map','[o]','-t',total,'-c:v','libx264','-profile:v','main','-pix_fmt','yuv420p','-preset','veryfast','-crf','21','-c:a','aac','-b:a','128k','-movflags','+faststart',R/j['out']])
 final=tr(R/j['out'],j['text']);(D/f"{j['n']}_final_whisper.json").write_text(json.dumps(final,ensure_ascii=False,indent=2));print('FINAL',j['out'],total,' '.join(s['text'] for s in final),flush=True)
 ff(['-i',R/j['out'],'-vf','fps=1/3,scale=180:320,tile=4x3','-frames:v','1',D/f"{j['n']}_hoja.jpg"])
(D/'anuncios.json').write_text(json.dumps([dict(nombre=j['n']+'_corregido_20261031',video=str(R/j['out']),cliente=j['cliente']) for j in J],ensure_ascii=False,indent=2))
