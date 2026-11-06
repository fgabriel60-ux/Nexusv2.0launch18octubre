from pathlib import Path
import subprocess,json
from PIL import Image,ImageOps
D=Path(__file__).resolve().parent;R=D.parents[1]
def ff(a):subprocess.run(['ffmpeg','-v','error','-y','-threads','2',*map(str,a)],check=True)
def dur(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
def tm(t):return f'0:{int(t)//60:02}:{t%60:05.2f}'
HEAD='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat,44,&H00FFFFFF,&H0000D7FF,&H00111111,&H70000000,-1,0,0,0,100,100,0,0,1,3,1,2,45,45,285,1
Style: Title,Montserrat,32,&H00FFFFFF,&H00FFFFFF,&H00111111,&H70000000,-1,0,0,0,100,100,0,0,3,2,0,8,45,45,85,1
Style: CTA,Montserrat,34,&H00FFFFFF,&H00FFFFFF,&H00111111,&H70000000,-1,0,0,0,100,100,0,0,3,2,0,2,45,45,125,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def line(a,b,sty,txt,layer=0):return f'Dialogue: {layer},{tm(a)},{tm(b)},{sty},,0,0,0,,{txt}\n'
def subtitles(words):
 groups=[];g=[]
 for w in words:
  g.append(w)
  if len(g)==4 or w['word'].strip().endswith(('.',',','?')):groups.append(g);g=[]
 if g:groups.append(g)
 result=''
 for g in groups:
  # Tiempos absolutos por palabra: los silencios no adelantan el resaltado.
  for active,w in enumerate(g):
   end=g[active+1]['start'] if active+1<len(g) else w['end']+.05
   txt=' '.join(('{\\c&H00D7FF&}'+x['word'].strip()+'{\\c&HFFFFFF&}') if k==active else x['word'].strip() for k,x in enumerate(g))
   result+=line(w['start'],end,'Sub',txt,2)
 return result

def segments(name,shots):
 paths=[]
 for i,(p,start,length) in enumerate(shots):
  out=D/f'{name}_seg{i}.mp4';inp=['-loop','1','-i',p] if p.suffix.lower() in ['.jpg','.png'] else ['-ss',start,'-i',p]
  ff([*inp,'-t',length,'-vf','scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=25,format=yuv420p','-an','-c:v','libx264','-preset','veryfast','-crf','20',out]);paths.append(out)
 lp=D/f'{name}_lista.txt';lp.write_text(''.join(f"file '{p}'\n" for p in paths));out=D/f'{name}_base.mp4';ff(['-f','concat','-safe','0','-i',lp,'-c','copy',out]);return out

def victor():
 P=R/'clientes/Victor/video';V=R/'entregables/victor_guillermo_20261031';total=dur(V/'Victor_toma0.wav')+.35
 # Prueba real al abrir y al hablar de supervisión; proceso y resultado existentes.
 shots=[(P/'cuadros/f_1.5.jpg',0,2.0),(P/'v4/O1_piso.mp4',.5,3.5),(P/'v4/O3_aspirar.mp4',.3,3.6),(P/'v4/O2_ventanal.mp4',.2,3.4),(P/'cuadros/f_15.jpg',0,1.6),(P/'v4/O5_listo.mp4',0,total-14.1)]
 # Último clip en bucle si excede su duración: alterna dos recortes del resultado.
 p,start,length=shots.pop();remaining=length
 while remaining>.01:
  take=min(3.8,remaining);shots.append((p,.15,take));remaining-=take
 base=segments('Victor_v7',shots)
 words=[w.copy() for s in json.loads((D/'victor_fuente.json').read_text()) for w in s['words']]
 for w in words:
  if 'Cervilín' in w['word']:w['word']=w['word'].replace('Cervilín','Servilin')
 # La C/S inicial es homófona en español mexicano; no es un error audible de voz.
 ass=HEAD+line(0,total,'Title','SERVILIN · LIMPIEZA DE OBRA FINA\\NSOLO EMPRESAS · NO ES VACANTE')+line(0,total,'CTA','WHATSAPP 56 3634 1441\\NTipo de inmueble + m²')+line(0,2,'Sub','{\\an5\\pos(360,500)}¿ERES CONSTRUCTORA\\NO DESARROLLADOR?',3)+subtitles(words)
 (D/'Victor_v7.ass').write_text(ass)
 out=P/'Servilin_obra_fina_v7.mp4'
 ff(['-i',base,'-i',R/'clientes/Victor/video/Servilin_obra_fina_v6d.mp4','-vf',f'ass={D}/Victor_v7.ass','-map','0:v','-map','1:a','-t',total,'-c:v','libx264','-profile:v','main','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',out]);return out

def manuel():
 P=R/'clientes/XV';src=P/'voz_manuel/voz_manuel_completa.ogg';ranges=[(1.10,4.40),(5.10,9.40),(10.10,15.86),(15.96,20.45),(20.38,26.10)]
 allwords=[w for s in json.loads((D/'manuel_completa_fuente.json').read_text()) for w in s['words']];words=[];offset=.2;inputs=[];filters=''
 for i,(a,b) in enumerate(ranges):
  inputs+=['-i',src];filters+=f'[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b-a-.025}:d=0.025,apad=pad_dur=0.18[p{i}];'
  for w in allwords:
   if a<=w['start']<b:words.append(dict(word=w['word'],start=offset+w['start']-a,end=offset+min(w['end'],b)-a))
  offset+=b-a+.18
 total=offset+1.1
 filters+=''.join(f'[p{i}]' for i in range(len(ranges)))+f'concat=n=5:v=0:a=1,highpass=f=80,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=7,adelay=200,apad,atrim=0:{total}[a]'
 ff([*inputs,'-filter_complex',filters,'-map','[a]','-ar','44100','-ac','1',D/'Manuel_voz.wav'])
 # Cortes limpios; se retiran las transiciones que emborronaban las caras.
 v3=P/'final/XV_reel_v3.mp4';v12=P/'final/XV_reel_v12_inicio_v3_fiesta_IA_sin_voz.mp4'
 shots=[(v3,0,3.6),(v3,5.2,2.6),(v3,8.6,2.7),(v3,11.0,2.2),(v12,17.0,2.1),(v3,17.0,2.4),(v3,20.1,2.5),(v3,6,2.8),(v3,9,2.4),(v3,17,total-23.3)]
 base=segments('Manuel_v20',shots)
 ass=HEAD+line(0,total,'Title','HUNAB KU FOTOGRAFÍA\\NXV AÑOS')+line(0,total,'CTA','WHATSAPP +1 520 313 6941')+line(19.0,total,'Title','HUNAB KU FOTOGRAFÍA\\NCotiza la cobertura de tus XV años',1)+line(19.0,total,'CTA','WHATSAPP +1 520 313 6941\\NEnvía fecha + ciudad de tu evento',1)+subtitles(words)
 (D/'Manuel_v20.ass').write_text(ass)
 logo=Image.open(R/'clientes/Manuel_fotografia/logo/hunab_ku_logotipo_manuel.png').convert('RGBA');logo=logo.crop(logo.getbbox());logo=ImageOps.contain(logo,(460,160));logo.save(D/'manuel_logo.png')
 out=P/'final/XV_reel_v20_manuel.mp4';music=R/'clientes/Guillermo/far12_v1/tmp/musica.wav'
 ff(['-i',base,'-i',D/'Manuel_voz.wav','-stream_loop','-1','-i',music,'-i',D/'manuel_logo.png','-filter_complex',f'[0:v]drawbox=x=100:y=400:w=520:h=210:color=white@0.88:t=fill:enable=\'gte(t,19)\'[b];[b][3:v]overlay=(W-w)/2:425:enable=\'gte(t,19)\',ass={D}/Manuel_v20.ass[v];[2:a]volume=0.045,atrim=0:{total},afade=t=out:st={total-1}:d=1[m];[1:a][m]amix=inputs=2:normalize=0:duration=first[a]','-map','[v]','-map','[a]','-t',total,'-c:v','libx264','-profile:v','main','-pix_fmt','yuv420p','-preset','veryfast','-crf','21','-c:a','aac','-b:a','128k','-movflags','+faststart',out]);(D/'Manuel_palabras.json').write_text(json.dumps(words,ensure_ascii=False,indent=2));return out
if __name__=='__main__':
 for f in [victor,manuel]:print('TERMINADO',f(),flush=True)
