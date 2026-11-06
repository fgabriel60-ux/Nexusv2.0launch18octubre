"""Combina el gancho correcto de toma 3 con el cuerpo correcto de toma 2."""
import json
from producir import OUT,run
takes=json.loads((OUT/'tomas_whisper.json').read_text());a,b=takes[2],takes[1]
wa=a['palabras'];wb=b['palabras'];end=wa[2]['end'];start=wb[3]['start']
out=OUT/'voz_compuesta_verificada.wav'
run(['-i',a['ruta'],'-i',b['ruta'],'-filter_complex',f'[0:a]atrim=0:{end},asetpts=PTS-STARTPTS[a];[1:a]atrim=start={start},asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[out]','-map','[out]',out])
words=wa[:3]+[dict(w,start=w['start']-start+end,end=w['end']-start+end) for w in wb[3:]]
choice={'ruta':str(out),'texto':' '.join(w['word'] for w in words),'palabras':words,'fuentes':['Gancho: toma 3','Cuerpo y cierre: toma 2'],'pendiente':'Revisar transcripción de salida final'}
(OUT/'voz_elegida.json').write_text(json.dumps(choice,ensure_ascii=False,indent=2));print(choice['texto'])
