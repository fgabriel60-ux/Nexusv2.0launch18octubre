"""Flyers pendientes: movimiento H3 con texto EXTRAÍDO del original, sin reescribir cifras."""
import json, subprocess, sys
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageFilter,ImageDraw
import imageio_ffmpeg
AQUI=Path(__file__).resolve().parent
FF=imageio_ffmpeg.get_ffmpeg_exe();W,H,FPS,FIN=1080,1920,30,7
CONFIG={
 'Sotol_familia':('1018_005111_BA9020.jpg',[(.1,'punch',.8,0),(1.,'ding',.8,0),(1.7,'mouse',.6,0)]),
 'Bugambilia_mejor_opcion':('1020_210408_4AF9D8.jpg',[(.1,'punch',.8,0),(.65,'ding',.8,0),(1.2,'mouse',.6,0),(1.65,'camara',.7,0)])}
def layers(name,source):
    out=[]
    def add(box,t,white=False,rounded=False,soft_top=0):
        im=source.crop(box).convert('RGBA')
        if white:
            a=np.asarray(im)[:,:,:3].astype(float);mask=np.clip((a.min(2)-185)/45,0,1)
            mask*=np.clip((55-(a.max(2)-a.min(2)))/25,0,1)
            im.putalpha(Image.fromarray((255*mask).astype('uint8')))
        if rounded:
            mask=Image.new('L',im.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,im.width+12,im.height-1),15,fill=255);im.putalpha(mask)
        if soft_top:
            alpha=np.array(im.getchannel('A')).astype(float)
            alpha[:soft_top]*=np.linspace(0,1,soft_top)[:,None]
            im.putalpha(Image.fromarray(alpha.astype('uint8')))
        x,y=box[:2];im=im.resize((round(im.width*1.2),round(im.height*1.2)),Image.Resampling.LANCZOS)
        out.append((im,round(x*1.2),round(y*1.2),t))
    if name=='Sotol_familia':
        add((55,172,858,303),.1,white=True)
        add((616,1039,900,1318),1.,rounded=True)
        add((0,1318,900,1600),1.7,soft_top=30)
    else:
        add((0,95,900,310),.1)
        add((0,310,900,462),.65)
        add((0,462,900,601),1.2)
        add((0,640,900,834),1.65)
        add((0,1350,900,1600),.4)
    return out

def render(name):
    source=Image.open(AQUI.parent/'flyers_recibidos'/CONFIG[name][0]).convert('RGB')
    ls=layers(name,source)
    folder=AQUI/'nuevos'/name
    for i,(im,x,y,t) in enumerate(ls):im.save(folder/f'capa_{i}.png')
    clip=folder/'clip.mp4'
    rd=imageio_ffmpeg.read_frames(str(clip),output_params=['-vf',f'scale={W}:{H}:flags=lanczos,fps={FPS}'])
    meta=next(rd)
    version=sys.argv[1] if len(sys.argv)>1 else '2'
    out=AQUI/f'Mariano_flyer_{name}_v{version}.mp4'
    proc=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-profile:v','main','-pix_fmt','yuv420p','-crf','21','-preset','medium','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
    last=None
    try:
        for i in range(FIN*FPS):
            try:last=next(rd)
            except StopIteration:pass
            if last is None:raise RuntimeError('Clip vacío')
            t=i/FPS;img=Image.frombytes('RGB',(W,H),last).convert('RGBA')
            if name!='Sotol_familia':ImageDraw.Draw(img).rectangle((0,0,W,1000),fill='white')
            for im,x,y,start in ls:
                if t<start:continue
                k=min(1,(t-start)/.3);k=1-(1-k)**3
                layer=im.copy();layer.putalpha(layer.getchannel('A').point(lambda a:round(a*k)))
                # Deslizamiento sin zoom: los bordes y las cifras no se recortan.
                img.alpha_composite(layer,(x,y+round(22*(1-k))))
            if i in [6,30,105,204]:img.convert('RGB').save(folder/f'revision_{i:03d}.jpg')
            proc.stdin.write(img.convert('RGB').tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Error de codificación')
    finally:rd.close()
    print(out,flush=True)
if __name__=='__main__':
    (AQUI/'nuevos'/'eventos.json').write_text(json.dumps({n:c[1] for n,c in CONFIG.items()},indent=2))
    for name in CONFIG:render(name)
