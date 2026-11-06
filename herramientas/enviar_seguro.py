"""Manda un archivo (video/imagen) con texto al chat de Carlos, con reintentos. Uso: python3 enviar_seguro.py ruta "texto" """
import sys,os,base64,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from wa import accion
ruta,cap=sys.argv[1],sys.argv[2]
b=base64.b64encode(open(ruta,'rb').read()).decode()
for i in range(5):
    r=accion('send-media',{'chatId':'44522318905388@lid','mediaBase64':b,'mediaName':os.path.basename(ruta),'mediaCaption':cap})
    if r and r.get('data',{}).get('status')=='success': print('ok',ruta); break
    time.sleep(10*(i+1))
else: print('fallo',ruta)
