from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json
R=Path('/workspaces/Nexusv2.0launch18octubre'); D=R/'entregables/jose_v9e_20261031'; A=R/'clientes/Jose/armado_20261029'
font=str(R/'visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf')
def f(s):
 ft=ImageFont.truetype(font,s); ft.set_variation_by_name('Bold'); return ft
def center(d,t,y,s,col='white'):
 while d.textlength(t,font=f(s))>660:s-=1
 d.text(((720-d.textlength(t,font=f(s)))/2,y),t,font=f(s),fill=col)
p=Image.new('RGBA',(720,1280));d=ImageDraw.Draw(p);d.rounded_rectangle((18,780,702,1190),25,fill=(12,38,104,248))
for t,y,s,c in [('GRUPO JR · PUEBLA',803,35,'#ffd63c'),('Mándanos fotos de tu azotea',870,36,'white'),('por WhatsApp y te cotizamos hoy.',930,32,'white'),('WhatsApp',1010,32,'#ffd63c'),('221 573 3127',1060,65,'white')]:center(d,t,y,s,c)
p.save(D/'cta.png')
p=Image.new('RGB',(720,1280),(12,38,104));d=ImageDraw.Draw(p)
for t,y,s,c in [('GRUPO JR',100,91,'white'),('Impermeabilización en Puebla',230,38,'#ffd63c'),('Desde $150 por m²',350,64,'#ffd63c'),('Sellador + 2 capas',445,38,'white'),('10% de descuento',560,49,'#ffd63c'),('en más de 100 m²',625,37,'white'),('Mándanos fotos de tu azotea',760,36,'white'),('y te cotizamos hoy.',820,42,'white'),('WhatsApp',950,40,'#ffd63c'),('221 573 3127',1020,76,'white')]:center(d,t,y,s,c)
p.save(D/'tarjeta.png')
out=R/'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9e.mp4'
cmd=['ffmpeg','-v','error','-y','-i',str(R/'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9d.mp4'),'-i',str(A/'tmp_v9d/base.mp4'),'-i',str(D/'cta.png'),'-i',str(D/'tarjeta.png'),'-filter_complex',"[1:v]scale=720:1280[b];[0:v][b]overlay=enable='between(t,20.1,24.334)'[v1];[v1][2:v]overlay=enable='between(t,20.1,24.334)'[v2];[v2][3:v]overlay=enable='gte(t,24.334)'[v]",'-map','[v]','-map','0:a','-c:v','libx264','-threads','2','-profile:v','main','-level','3.1','-pix_fmt','yuv420p','-crf','22','-c:a','copy','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
print(out)
(D/'cambios.txt').write_text('Cierre fijo y completo desde 20.1 s; tarjeta nueva desde 24.334 s. Audio original v9d sin cambios: toma 1 verificada con Whisper medium, coincidencia 1.0. Descuento 10% confirmado por Carlos; condición >100 m² conservada del video anterior.\n')
