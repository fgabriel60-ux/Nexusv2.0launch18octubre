from pathlib import Path
import re,json,datetime,subprocess
P=Path('entregables/ronda_8_9_20261031');R=Path.cwd()
selections={
'Guillermo':'clientes/Guillermo/far12_v1/Vicens_far12_v4b_voz.mp4',
'BD Pro':'clientes/PistasBaile/video/BDPro_proceso_vs_resultado_v2.mp4',
'José':'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9f.mp4',
'Doctora / Alberto':'clientes/Alberto/video/Veneers_Dra_Angeles_implantes_estilo_ref_v6c.mp4',
'Víctor':'clientes/Victor/video/Servilin_obra_fina_v7.mp4',
'Giovanni':'clientes/Giovanni/Giovanni_video_v5.mp4',
'Fernando':'clientes/Fernando/video/Anegocios_Fernando_v7_capacitacion_pasos.mp4',
'Manuel':'clientes/XV/final/XV_reel_v20_manuel.mp4',
'Lisbeth':'clientes/Lisbeth/video/Lisbeth_v9_terreno_real.mp4',
'Jesús Puertas':'entregables/jesus_puertas_20261028/Jesus_carpinteria_v3.mp4',
'Tatuador / Adrián':'clientes/Tatuador9983316522/hardcut_v2/Adrian_hardcut_v2.mp4',
'Rachel':'clientes/Micropigmentacion6861607879/video/Micropigmentacion6861607879_qwen_v1.mp4',
'Blanca':'clientes/Blanca/video/Hablar_Hablando_Blanca_v3.mp4',
'Mariano':'clientes/Mariano/video/Vizcaino_v5_gancho_spiderman_v2.mp4',
'Verónica':'clientes/VeronicaArguelles/video/VeronicaArguelles_qwen_v1.mp4',
'Iván':'clientes/Ivan/video_v5_20261030/Fumicam_Ivan_v5b.mp4',
'Andrés':'clientes/Contratista6561300006/video_v1/Contratista_muestra_v2.mp4',
'Rubén':'clientes/Ruben_Quiropraxia/video_v3/Ruben_video_v3b.mp4',
'Uriel':'clientes/Uriel/video_plataforma_sin_precio.mp4',
'Ignacio Corona / Generadores':'clientes/Generadores5554615710/video/Generadores5554615710_qwen_v1.mp4',
'Fumigaciones Chávez':'clientes/Fumigador449/video/Fumigaciones_Chavez_v1.mp4'}
# Evaluaciones: solo la respuesta final, asociada por orden al manifest del lote.
evals={};allrecords=[]
for mf in Path('entregables/glimmer_evaluador').glob('anuncios*.json'):
 try:items=json.loads(mf.read_text())
 except:continue
 lid=mf.stem.removeprefix('anuncios_');log=mf.parent/lid/'glimmer.log'
 if not log.exists():continue
 parts=log.read_text(errors='replace').split('assistant to=user')[1:]
 for it,part in zip(items,parts):
  m=re.search(r'CALIFICACI[ÓO]N TOTAL:\s*([\d.]+)\s*/\s*10',part)
  if not m:continue
  ending=re.search(r'VEREDICTO:[^\n]*',part)
  answer=part[:ending.end()] if ending else part.split('assistant')[0]
  proj=re.search(r'proyectada\D{0,15}([\d.]+)\s*/\s*10',answer,re.I)
  v=it['video'];v=v[v.find('/clientes/')+1:] if '/clientes/' in v else v[v.find('/entregables/')+1:] if '/entregables/' in v else v
  rec={'video':v,'nombre':it['nombre'],'actual':m[1],'proyectada':proj[1] if proj else None,'log':str(log),'mtime':log.stat().st_mtime,'respuesta':answer}
  allrecords.append(rec)
  if v not in evals or rec['mtime']>evals[v]['mtime']:evals[v]=rec
(P/'evaluaciones_verificadas.json').write_text(json.dumps(allrecords,ensure_ascii=False,indent=2))
lines=['# Inventario de videos · Fase A1','', 'Corte UTC: '+datetime.datetime.now(datetime.timezone.utc).isoformat(),'', 'La nota pertenece únicamente a la ruta evaluada. Se conservaron las respuestas finales posteriores a `assistant to=user`; no se usaron notas internas ni proyecciones como actuales. Fecha = modificación UTC. En archivos migrados, varias fechas coinciden; se prioriza versión dentro de la misma serie. No se consideran escenas, referencias, temporales ni anuncios de Nexus como videos del cliente.','', '| Cliente | Ruta absoluta | Versión | Última calificación propia | Fecha UTC |','|---|---|---|---|---|']
rows=[]
for name,rel in selections.items():
 p=Path(rel)
 if not p.exists():
  lines.append(f'| {name} | No localizada: {rel} | — | Sin verificar | — |');continue
 v=re.findall(r'v\d+[a-z]?',p.stem,re.I);ver=v[-1] if v else 'sin versión'
 e=evals.get(rel);note=f"{e['actual']}/10 actual; {e['proyectada'] or 'no indicada'}/10 proyectada; `{e['log']}`" if e else 'Sin calificación propia verificable'
 date=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(timespec='seconds')
 probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],capture_output=True,text=True)
 rows.append({'cliente':name,'video':str(R/rel),'version':ver,'mtime':date,'duracion':probe.stdout.strip(),'evaluacion':e})
 lines.append(f'| {name} | {R/rel} | {ver} | {note} | {date} |')
missing=['Israel','Jesús Rar~Amore','Ignacio Iglesia (Colorado)','Rafael BYD','Pleiadian','Sanick','Carpintería Cadena','Jeremías','Omar','Terapeuta de lenguaje (55 2858 1526)','Antonio Cancelería','Julio Rosticería','Luz y Sonido GDL','Cinthia (tarjeta animada, no anuncio de captación)']
for n in missing:lines.append(f'| {n} | Sin anuncio final .mp4 identificado en clientes/ ni entregables/ | — | Sin nota verificable | — |')
lines += ['', '## Guillermo: base pendiente de identificar','Carlos pidió el video generado en Modal previamente enviado; far12 v4b es el último montaje con voz, pero NO se declara que sea la base aprobada. Hay versiones de techo “caen” y “suben”; ubicar mensaje y archivo antes de editar. Guillermo_Pixar_v5_metodo es anuncio de la agencia, no se incluye como anuncio de Vicens.','', '## Series adicionales','Doctora: también hay carillas, ortodoncia, placas y tomografía v1; se inventaría implantes v6c como la serie del encargo. No confundir esos anuncios con una versión nueva del mismo video.','Israel: los Israel_1 a Israel_4 en ideas_aprobar son referencias, no una muestra final atribuible al cliente.','Cinthia: tarjeta animada en visionagenciaIAV2.0-main 2/entregables/cinthia_payan_logo_20261027/tarjeta/; fuera de los dos árboles pedidos y fuera de evaluación de anuncio.']
(P/'inventario.md').write_text('\n'.join(lines)+'\n');(P/'inventario.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('Videos',len(rows));print('No encontrados',[x for x,p in selections.items() if not Path(p).exists()])
