from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
R=Path('/workspaces/Nexusv2.0launch18octubre'); A=R/'clientes/Jose/armado_20261029'; T=A/'tmp_v9f'; T.mkdir(exist_ok=True)
font=str(R/'visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf')
def panel(name,lines):
 im=Image.new('RGBA',(720,1280));d=ImageDraw.Draw(im)
 for y,text,size,color in lines:
  f=ImageFont.truetype(font,size);f.set_variation_by_name('Bold')
  while d.textlength(text,font=f)>660: size-=1;f=ImageFont.truetype(font,size);f.set_variation_by_name('Bold')
  d.rounded_rectangle((20,y-12,700,y+size+22),14,fill=(8,29,78,245))
  d.text(((720-d.textlength(text,font=f))/2,y),text,font=f,fill=color)
 im.save(T/name)
white='white';yellow='#ffd63c'
clips=['V7_lluvia','V2_cubetas','V4_primario','V5_poliuretano','V6_terminada','V8_cierre']
texts=[['¿Se te filtra el agua','cuando llueve?','En Grupo JR lo resolvemos.'],['Usamos poliuretano acrílico','de 12 años + primario','fibratado elástico.'],['Primero el primario,','para una base sólida.'],['Luego la protección continua,','sin uniones.'],['Tu losa queda lista para','la temporada de lluvias.'],['Mándanos fotos de tu azotea','por WhatsApp y te cotizamos hoy.']]
parts=[]
for k,c in enumerate(clips):
 lines=[(120,'GRUPO JR · PUEBLA',34,yellow)]
 if k:lines += [(240,'Desde $150 por m²',43,yellow),(306,'WhatsApp 221 573 3127',40,white)]
 lines += [(865+i*58,s,34,white) for i,s in enumerate(texts[k])]
 if k==5:lines += [(1080,'Fotos + zona para cotizar',32,yellow)]
 panel(f'p{k}.png',lines);out=T/f's{k}.mp4';parts.append(out)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(A/'tmp_v9d'/f'{c}.mp4'),'-i',str(T/f'p{k}.png'),'-filter_complex','[0:v]scale=720:1280[b];[b][1:v]overlay=0:0','-an','-c:v','libx264','-preset','fast','-crf','21',str(out)],check=True)
# cierre completo
panel('card.png',[(200,'GRUPO JR · PUEBLA',48,yellow),(350,'Desde $150 por m²',54,white),(450,'Sellador + 2 capas',38,white),(560,'10% de descuento',44,yellow),(625,'en más de 100 m²',35,white),(790,'Mándanos fotos de tu azotea',32,white),(850,'y te cotizamos hoy',36,white),(1000,'WhatsApp',38,yellow),(1070,'221 573 3127',60,white)])
# opaque background
im=Image.open(T/'card.png');bg=Image.new('RGBA',im.size,(8,29,78,255));bg.alpha_composite(im);bg.convert('RGB').save(T/'card.png')
card=T/'card.mp4';subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',str(T/'card.png'),'-t','3.2','-r','30','-c:v','libx264','-pix_fmt','yuv420p',str(card)],check=True);parts.append(card)
(T/'list.txt').write_text(''.join(f"file '{p}'\n" for p in parts))
out=R/'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9f.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(T/'list.txt'),'-i',str(A/'tmp_v9d/voz.wav'),'-map','0:v','-map','1:a','-af','apad','-shortest','-c:v','libx264','-profile:v','main','-level','3.1','-pix_fmt','yuv420p','-preset','fast','-crf','22','-c:a','aac','-movflags','+faststart',str(out)],check=True)
print(out)
