"""Montaje por cuadros con memoria constante. Usa los clips H3 recuperados de Claude."""
import json, subprocess, wave
from pathlib import Path
import cv2, numpy as np
from PIL import Image
from armar import FF, W, H, FPS, rotulo
import sfx
AQUI=Path(__file__).resolve().parent
PLAN=[('K1',0,5.15,1.4,'Lanzamiento y despliegue'),('K2',0,2.3,1.3,'Corredera y alas abiertas'),('K3b',0,5.15,1.5,'Aleteo'),('K4',0,3.5,2.,'Desacople'),('K5',0,5.15,1.2,'Reenrollado')]
def main():
    nframes=[round((b-a)/v*FPS) for _,a,b,v,_ in PLAN]
    duration=sum(nframes)/FPS
    starts=np.cumsum([0]+nframes[:-1])/FPS
    events=[(.3,'whoosh',{'d':.55}), (starts[1],'clic',{}), (starts[2],'aleteo',{'d':nframes[2]/FPS,'hz':2.6}), (starts[3],'clic',{}), (starts[4]+1,'whoosh',{'d':1}), (duration-.6,'clic',{})]
    aud=sfx.pista(events,duration)
    wav=AQUI/'clips'/'audio_montaje.wav'
    with wave.open(str(wav),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sfx.SR);w.writeframes((aud*32767).astype('<i2').tobytes())
    out=AQUI/'pajaro_realista_v1.mp4'
    enc=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(wav),'-c:v','libx264','-profile:v','main','-crf','21','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
    for (clip,a,b,v,label),n in zip(PLAN,nframes):
        cap=cv2.VideoCapture(str(AQUI/'clips'/f'{clip}.mp4'))
        rgb,alpha=rotulo(label)
        for k in range(n):
            cap.set(cv2.CAP_PROP_POS_MSEC,(a+k/FPS*v)*1000)
            ok,fr=cap.read()
            if not ok: raise RuntimeError(f'No se puede leer {clip} cuadro {k}')
            fr=cv2.cvtColor(cv2.resize(fr,(W,H)),cv2.COLOR_BGR2RGB)
            fade=min(1,k/5,max(0,(1.6*FPS-k)/5))
            if fade: fr=(fr*(1-alpha*fade)+rgb*alpha*fade).astype('uint8')
            enc.stdin.write(fr.tobytes())
        cap.release()
    enc.stdin.close()
    if enc.wait():raise RuntimeError('Error de render')
    (AQUI/'montaje_v1.json').write_text(json.dumps({'plan':PLAN,'inicios':starts.tolist(),'duracion':duration},ensure_ascii=False,indent=2))
    print(out,round(duration,2),round(out.stat().st_size/1e6,2),'MB')
if __name__=='__main__':main()
