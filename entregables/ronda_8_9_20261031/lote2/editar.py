from pathlib import Path
import subprocess,json,sys
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path.cwd();D=R/'entregables/ronda_8_9_20261031/lote2'
FONT=R/'visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
def ff(a):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-threads','2',*map(str,a)],check=True)
def panel(name,lines,y,bg=(12,15,23,245),sizes=None):
 im=Image.new('RGBA',(720,1280));d=ImageDraw.Draw(im);height=sum((sizes or [45]*len(lines)))+len(lines)*18+28;d.rounded_rectangle((30,y,690,y+height),22,fill=bg)
 yy=y+14
 for t,s in zip(lines,sizes or [45]*len(lines)):
  f=ImageFont.truetype(str(FONT),s);f.set_variation_by_axes([800])
  while d.textlength(t,font=f)>620:s-=1;f=ImageFont.truetype(str(FONT),s);f.set_variation_by_axes([800])
  d.text((360,yy),t,font=f,anchor='mt',fill='white');yy+=s+18
 p=D/(name+'.png');im.save(p);return p
enc=['-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart']
def overlays(src,out,items):
 ins=['-i',src];flt='';cur='0:v'
 for i,(p,a,b) in enumerate(items):
  ins+=['-loop','1','-i',p];flt+=f"[{cur}][{i+1}:v]overlay=0:0:enable='between(t,{a},{b})'[o{i}];";cur=f'o{i}'
 ff(ins+['-filter_complex_threads','1','-filter_complex',flt.rstrip(';'),'-map',f'[{cur}]','-map','0:a','-shortest',*enc,'-c:a','copy',out])
def replace(src,out,parts,fx=None):
 # parts = (start,end,replacement image or video,start in replacement,zoom)
 ins=['-i',src];flt='';cur='0:v';n=1
 for a,b,p,ss,z in parts:
  isimg=p.suffix.lower() in ['.jpg','.png'];ins+=['-loop','1','-i',p] if isimg else ['-ss',str(ss),'-i',p]
  f=f'[{n}:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,setsar=1'
  if z:f+=f",scale=1440:2560,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=720x1280:fps=30"
  f+=f',trim=duration={b-a},setpts=PTS-STARTPTS+{a}/TB[r{n}];';flt+=f+f"[{cur}][r{n}]overlay=0:0:enable='gte(t,{a})*lt(t,{b})':eof_action=pass[o{n}];";cur=f'o{n}';n+=1
 audio='0:a'
 if fx:
  ins+=['-i',R/'clientes/Guillermo/video/sfx/whoosh.wav'];flt+=f'[{n}:a]asplit={len(fx)}'+''.join(f'[s{i}]' for i in range(len(fx)))+';'
  for i,t in enumerate(fx):flt+=f'[s{i}]volume=0.20,adelay={int(t*1000)}:all=1[f{i}];'
  flt+='[0:a]'+''.join(f'[f{i}]' for i in range(len(fx)))+f'amix=inputs={len(fx)+1}:duration=first:normalize=0[a];';audio='[a]'
 ff(ins+['-filter_complex_threads','1','-filter_complex',flt.rstrip(';'),'-map',f'[{cur}]','-map',audio,*enc,'-c:a','aac','-b:a','160k',out])
def giovanni():
 src=R/'clientes/Giovanni/Giovanni_video_v5.mp4';out=src.with_name('Giovanni_video_v5b.mp4')
 overlays(src,out,[(panel('g_exp',['15 AÑOS','DE EXPERIENCIA'],660,sizes=[60,35]),7.5,9.5),(panel('g_wa',['WhatsApp','624 136 3328'],910,bg=(15,123,65,255),sizes=[32,62]),19.5,25.6)])
def adrian():
 src=R/'clientes/Tatuador9983316522/hardcut_v1/Tatuador_hardcut_v1.mp4';out=src.parent.parent/'hardcut_v1b/Tatuador_hardcut_v1b.mp4';out.parent.mkdir(exist_ok=True)
 wa=src.parent.parent/'whatsapp';photos=[wa/'1029_180319_el_image.jpg',wa/'1029_180322_el_image.jpg']
 # Una sola toma continua del pecho en todo el gancho, sin reinicios.
 p=D/'adrian_gancho.mp4';ff(['-ss','3','-i',wa/'1029_181224_el_video.mp4','-loop','1','-i',src.parent/'tmp/c0.png','-filter_complex','[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=contrast=1.18:saturation=1.12:brightness=-0.03[v];[v][1:v]overlay=0:0[o]','-map','[o]','-t','2.5','-an',*enc,p])
 replace(src,out,[(0,2.5,p,0,None),(2.6,3.56,photos[0],0,'1.05'),(4.6,5.56,photos[1],0,'1.07'),(17.6,22.1,src.parent/'tmp/tarjeta.png',0,None)])
def jesus():
 src=R/'entregables/jesus_puertas_20261028/Jesus_carpinteria_v3.mp4';out=src.with_name('Jesus_carpinteria_v4.mp4')
 # Reusa foto real y tarjeta, tres planos de 2.1 s con acercamiento progresivo.
 orig=R/'clientes/Jesus_Puertas/whatsapp/del_cliente/20261027_175651_image.jpg';im=Image.open(orig).convert('RGB');bg=ImageOps.fit(im,(720,1280));
 # Tarjeta original de oferta y subtítulo conservados desde el armado original.
 cap=Image.open(src.parent/'tmp_v3/c1.png').convert('RGBA');bg=Image.alpha_composite(bg.convert('RGBA'),cap);p=D/'jesus_parota.png';bg.convert('RGB').save(p)
 tmp=D/'jesus_edit.mp4';replace(src,tmp,[(5.7,7.8,p,0,'1.00+0.00045*on'),(7.8,9.9,p,0,'1.10+0.00045*on'),(9.9,12.0,p,0,'1.20+0.00045*on')],fx=[5.7,7.8,9.9])
 overlays(tmp,out,[(panel('j_wa',['WhatsApp · [CONFIRMAR]','Envía medidas y colonia'],715,bg=(13,130,67,255),sizes=[40,30]),25.5,30.4)])
def victor():
 sys.path.insert(0,str(R/'entregables/correcciones_avm_20261031'));import editar_vm as v
 src=R/'clientes/Victor/video/Servilin_obra_fina_v7.mp4';out=src.with_name('Servilin_obra_fina_v7b.mp4');base=v.D/'Victor_v7_base.mp4'
 ass=(v.D/'Victor_v7.ass').read_text();head=ass.split('[Events]')[0]+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 events=[]
 for l in ass.splitlines():
  if l.startswith('Dialogue:') and ',Sub,' not in l:events.append(l)
 # Frases completas, continuas a través de los cortes; tiempos del audio verificado.
 groups=[(0,2.26,'¿Eres constructora\\No desarrollador?'),(2.26,5.10,'En Servilin hacemos limpieza\\Nde obra fina para'),(5.10,7.38,'empresas. Retiramos polvo,'),(7.38,9.22,'cemento y restos de pintura.'),(9.22,10.94,'Limpiamos ventanas y pisos'),(10.94,12.68,'con personal uniformado,'),(12.68,14.26,'capacitado y supervisado.'),(14.26,15.86,'Tu obra lista para entregar.'),(15.86,18.68,'Solicita una propuesta\\Npor WhatsApp.'),(18.68,21.95,'Dinos qué tipo de inmueble\\Ny cuántos metros cuadrados.')]
 for a,b,t in groups:events.append(v.line(a,b,'Sub',t,2).strip())
 pa=D/'Victor_v7b.ass';pa.write_text(head+'\n'.join(events)+'\n')
 ff(['-i',base,'-i',src,'-i',R/'clientes/Guillermo/video/sfx/whoosh.wav','-filter_complex_threads','1','-filter_complex',f"[0:v]gblur=sigma=14:enable='between(t,12.9,13.7)',ass={pa}[v];[2:a]volume=0.15,adelay=12900:all=1[s];[1:a][s]amix=inputs=2:normalize=0:duration=first[a]",'-map','[v]','-map','[a]',*enc,'-c:a','aac','-b:a','160k',out])
if __name__=='__main__':
 for n in sys.argv[1:] or ['giovanni','adrian','jesus','victor']:
  print('INICIO',n,flush=True);globals()[n]();print('LISTO',n,flush=True)
