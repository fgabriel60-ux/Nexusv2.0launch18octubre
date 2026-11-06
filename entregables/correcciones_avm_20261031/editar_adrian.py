from pathlib import Path
import subprocess
D=Path(__file__).resolve().parent;R=D.parents[1];W=R/'clientes/Tatuador9983316522/whatsapp'
O=R/'clientes/Tatuador9983316522/hardcut_v2';O.mkdir(exist_ok=True)
def ff(a):subprocess.run(['ffmpeg','-v','error','-y','-threads','2',*map(str,a)],check=True)
def tm(t):return f'0:{int(t)//60:02}:{t%60:05.2f}'
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Montserrat,45,&H00FFFFFF,&H00FFFFFF,&H00101010,&H70000000,-1,0,0,0,100,100,1,0,1,3,1,2,50,50,240,1
Style: Small,Montserrat,27,&H00FFFFFF,&H00FFFFFF,&H00101010,&H70000000,-1,0,0,0,100,100,1,0,1,2,1,8,50,50,90,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
items=[(0,2.88,'Main','TU IDEA. TU PIEL.'),(0,18.72,'Small','ADRIÁN · TATUAJES · CANCÚN'),(2.88,6.72,'Main','DISEÑO PERSONALIZADO'),(9.60,12.48,'Main','Sesiones desde $1,000'),(15.36,18.72,'Main','WHATSAPP 998 331 6522\\NEnvía diseño + tamaño + zona del cuerpo')]
for a,b,sty,txt in items:ass+=f'Dialogue: 0,{tm(a)},{tm(b)},{sty},,0,0,0,,{txt}\n'
(D/'Adrian_v2.ass').write_text(ass)
# El hombre de lentes con el torso tatuado es material de resultado; no se presenta como Adrián.
shots=[('180319',10.2,2.88),('180310',5.2,.96),('180312',1.0,1.92),('180321',3.2,1.92),('180626',2.2,.96),('180320',2.6,1.92),('180322',6.0,1.92),('180319',8.8,2.88),('180312',4.1,3.36)]
segs=[]
for i,(n,start,dur) in enumerate(shots):
 p=O/f'seg_{i}.mp4';ff(['-ss',start,'-i',W/f'1029_{n}_el_video.mp4','-t',dur,'-vf','scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=25,eq=contrast=1.06:saturation=0.95,format=yuv420p','-an','-c:v','libx264','-preset','veryfast','-crf','20',p]);segs.append(p)
(O/'lista.txt').write_text(''.join(f"file '{p}'\n" for p in segs));ff(['-f','concat','-safe','0','-i',O/'lista.txt','-c','copy',O/'base.mp4'])
out=O/'Adrian_hardcut_v2.mp4';ff(['-i',O/'base.mp4','-stream_loop','-1','-i',R/'clientes/Guillermo/techo_20261029/salida_v6_caen/beat_techo.wav','-vf',f'ass={D}/Adrian_v2.ass','-af','volume=0.65,afade=t=out:st=17.7:d=1','-t','18.72','-c:v','libx264','-profile:v','main','-pix_fmt','yuv420p','-preset','veryfast','-crf','21','-c:a','aac','-b:a','128k','-movflags','+faststart',out]);print(out)
