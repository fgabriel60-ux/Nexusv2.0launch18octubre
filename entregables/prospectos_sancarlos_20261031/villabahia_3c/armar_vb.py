import subprocess,glob
from PIL import Image,ImageDraw,ImageFont
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; N='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
fs=sorted(glob.glob('salida/VBT*.mp4')); D=2.7
cap=["Frente al Mar de Cortés","Alberca entre palmeras","Tu balcón con vista a la bahía","Sala con techo de madera","Cocina equipada","Recámara con vista al mar","Atardeceres en San Carlos"]
inp=sum([['-ss','0.2','-t',str(D),'-i',f] for f in fs],[])
fc=''
for i in range(len(fs)):
    fc+=(f"[{i}:v]scale=720:1280,setsar=1,fps=30,format=yuv420p,fade=t=in:st=0:d=0.25,drawtext=fontfile={F}:text='{cap[i]}':fontsize=40:fontcolor=white:borderw=4:bordercolor=black@0.7:x=(w-text_w)/2:y=h*0.78[v{i}];")
fc+=''.join(f'[v{i}]' for i in range(len(fs)))+f'concat=n={len(fs)}:v=1:a=0[b];'
fc+=(f"[b]drawtext=fontfile={F}:text='VILLA BAHÍA 3C':fontsize=56:fontcolor=white:borderw=5:bordercolor=black@0.6:x=(w-text_w)/2:y=h*0.10:enable='lt(t,2.7)',drawtext=fontfile={N}:text='San Carlos, Sonora':fontsize=38:fontcolor=white:borderw=4:bordercolor=black@0.6:x=(w-text_w)/2:y=h*0.10+70:enable='lt(t,2.7)'[v1]")
T=D*len(fs)
im=Image.open('salida/VB7_terraza.png').convert('RGB').resize((720,1280)); im=Image.alpha_composite(im.convert('RGBA'),Image.new('RGBA',im.size,(0,0,0,150))).convert('RGB'); d=ImageDraw.Draw(im)
for y,t,f,c in [(470,'VILLA BAHÍA 3C',ImageFont.truetype(F,60),'white'),(550,'San Carlos, Sonora',ImageFont.truetype(N,38),'white'),(700,'Reserva tu fin de semana',ImageFont.truetype(F,44),(255,214,120)),(780,'frente al mar',ImageFont.truetype(F,44),(255,214,120)),(930,'Escríbenos por WhatsApp',ImageFont.truetype(N,36),'white')]:
    d.text((360,y),t,font=f,fill=c,anchor='mm')
im.save('/tmp/vb_card.png')
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-loop','1','-t','2.5','-i','/tmp/vb_card.png','-stream_loop','-1','-i','/workspaces/Nexusv2.0launch18octubre/clientes/XV/musica_suave_s7.wav','-filter_complex',
 fc+f";[{len(fs)}:v]scale=720:1280,setsar=1,fps=30,format=yuv420p,fade=t=in:d=0.3[c];[v1][c]concat=n=2:v=1:a=0[v];[{len(fs)+1}:a]volume=0.5,afade=t=in:d=0.5,afade=t=out:st={T+1.5}:d=1,atrim=0:{T+2.5}[a]",
 '-map','[v]','-map','[a]','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-shortest','../VillaBahia3C_recorrido_v1.mp4'],check=True)
