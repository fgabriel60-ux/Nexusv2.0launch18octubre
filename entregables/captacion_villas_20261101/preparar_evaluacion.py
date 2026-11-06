from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
from producir import ROOT,OUT,FF,duration,norm

v=OUT/'Vision_duenos_villas_v1.mp4';T=duration(v)
tr=json.loads((OUT/'video_final_whisper.json').read_text());script=(OUT/'guion.txt').read_text()
print('Guion:',script);print('Whisper final:',tr['texto']);print('Coincidencia normalizada:',norm(script)==norm(tr['texto']))
if norm(script)!=norm(tr['texto']):
    import difflib
    print('Diferencias:',list(difflib.ndiff(norm(script),norm(tr['texto']))))
frames=[]
for i in range(30):
 t=T*(i+.5)/30;raw=subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(v),'-frames:v','1','-vf','scale=240:426','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
 im=Image.frombytes('RGB',(240,426),raw);ImageDraw.Draw(im).text((6,4),f'{t:.1f}s',font=ImageFont.load_default(18),fill='yellow',stroke_width=2,stroke_fill='black');frames.append(im)
photos=[]
for h in range(2):
 sheet=Image.new('RGB',(1200,1278))
 for j,im in enumerate(frames[h*15:h*15+15]):sheet.paste(im,(j%5*240,j//5*426))
 p=OUT/f'Vision_duenos_villas_v1_hoja{h+1}.jpg';sheet.save(p,quality=90);photos.append(str(p))
sys.path.insert(0,str(ROOT/'entregables/glimmer_evaluador'));from evaluar import PROMPT
cliente='''Visión Agencia, Carlos en Sonora. Video de CAPTACIÓN PARA DUEÑOS/ADMINISTRADORES DE VILLAS que rentan sus propiedades. NO anuncia hospedaje a turistas. Servicio a todo México, en línea. Oferta real: estrategia + videos $500 MXN/mes, pauta Meta aparte desde $250 MXN/mes. WhatsApp Carlos 6312470486. CTA: VILLA + ciudad + 3 fotos. El recorrido es una MUESTRA ILUSTRATIVA hecha con las fotos reales de Villa Bahía 3C, NO caso de éxito, cliente de pago ni promesa de reservas. Mostramos la foto original y su misma escena animada; los clips están generados con MiniMax H3.
Carlos pidió que diga «Usamos la IA de Facebook para revisar tu anuncio y buscamos que llegue a ocho de diez antes de lanzarlo. Aplícalo antes que tu competencia». En su servicio usa el modelo de Meta Glimmer para evaluar videos. Esta frase expresa la META de revisión; no es una nota del video ni una promesa de aprobación oficial de Meta Ads o de resultados. Califica el anuncio de captación de servicio por claridad, confianza y mensajes de dueños. No penalices por falta de tarifa por noche: no está ofreciendo estancias.'''
prompt=PROMPT.format(cliente=cliente,d=T,tr=tr['texto'],cap='Capacidades: montaje ffmpeg, cortes rápidos de tomas reales ya animadas, voz Fish Carlos, textos exactos en capas. No inventar resultados.')
(OUT/'evaluacion_lote.json').write_text(json.dumps([{'nombre':'VISION_DUENOS_VILLAS_v1','prompt':prompt,'fotos':photos}],ensure_ascii=False,indent=2))
(OUT/'anuncio.json').write_text(json.dumps([{'nombre':'VISION_DUENOS_VILLAS_v1','video':str(v),'cliente':cliente}],ensure_ascii=False,indent=2))
