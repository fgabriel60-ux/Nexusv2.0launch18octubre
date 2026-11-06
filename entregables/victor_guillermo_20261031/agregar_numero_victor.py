from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[1]
s=(D/'Victor.ass').read_text().replace('COTIZA POR WHATSAPP\\NTipo de inmueble + m²','WHATSAPP 56 3634 1441\\NTipo de inmueble + m²')
# Gancho completo desde primer cuadro, además del gancho hablado.
s+='\nDialogue: 3,0:00:00.00,0:00:02.00,Default,,0,0,0,,{\\an5\\pos(360,500)\\fs46}¿ERES CONSTRUCTORA\\NO DESARROLLADOR?'
a=D/'Victor_v6c.ass';a.write_text(s)
j=json.loads((D/'Victor_tomas.json').read_text());best=next(x for x in j if Path(x['path']).name=='Victor_toma0.wav');voice=best['path']
# Misma voz validada de v6b; solo cambia la capa visual.
out=R/'clientes/Victor/video/Servilin_obra_fina_v6c.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(D/'Victor_base.mp4'),'-i',str(R/'clientes/Victor/video/Servilin_obra_fina_v6b.mp4'),'-vf',f'ass={a}','-map','0:v','-map','1:a','-c:v','libx264','-profile:v','main','-pix_fmt','yuv420p','-preset','veryfast','-crf','21','-c:a','copy','-shortest','-movflags','+faststart',str(out)],check=True)
print(out)
