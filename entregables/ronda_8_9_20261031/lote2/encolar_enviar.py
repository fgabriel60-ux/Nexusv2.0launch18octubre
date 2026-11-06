from pathlib import Path
import json,subprocess,sys,datetime
R=Path.cwd();D=R/'entregables/ronda_8_9_20261031/lote2'
sys.path.insert(0,str(R/'herramientas'));from wa import accion
items=[
('GIOVANNI_v5b','clientes/Giovanni/Giovanni_video_v5b.mp4',6,8,'Añadí 15 AÑOS DE EXPERIENCIA y WhatsApp grande fijo de 19.5 a 25.6 s.','Lic. Giovanni Pulido, divorcios voluntarios en Los Cabos; desde $20,000 precio único, WA 624 136 3328; 15 años de experiencia.'),
('ADRIAN_hardcut_v1b','clientes/Tatuador9983316522/hardcut_v1b/Tatuador_hardcut_v1b.mp4',6,8,'Un solo arranque del pecho, dos fotos reales de tatuajes terminados y tarjeta única desde 17.6 s.','Adrián, tatuajes Cancún; sesiones desde $1,000; WA 998 331 6522; material real del cliente. Sin voz hablada: solo música, Whisper no detectó habla.'),
('JESUS_v4','entregables/jesus_puertas_20261028/Jesus_carpinteria_v4.mp4',7,8.5,'Parota en tres acercamientos con whoosh y botón verde al cierre. FALTA confirmar teléfono: dejé [CONFIRMAR]; no está listo para campaña.','Jesús, carpintería Mazatlán; puerta parota desde $7,000 marco y vistas; económica $3,500 con chapa bisagras instalación; cocina melamina $8,000 metro lineal gabinete alto y bajo. Teléfono no confirmado; tarjeta [CONFIRMAR] intencional, impide campaña.'),
('VICTOR_v7b','clientes/Victor/video/Servilin_obra_fina_v7b.mp4',7,8,'Subtítulos continuos, frase empresas. Retiramos polvo completa y whoosh con desenfoque en el corte 12.9–13.7 s.','Servilin, limpieza de obra fina para empresas, no vacante; WhatsApp 56 3634 1441; pide tipo de inmueble y m². Conserva audio existente; Servilin y Cervilín son homófonos en español mexicano, Whisper escribe Cervilín.')]
manifest=[]
for i,(name,path,current,projected,change,client) in enumerate(items):
 assert (R/path).exists() and (D/f'{Path(path).stem}_whisper.json').exists()
 ident='lote2_20261031_'+name.lower();dest=R/'entregables/glimmer_evaluador'/ident
 spec=R/'entregables/glimmer_evaluador'/f'anuncios_{ident}.json';spec.write_text(json.dumps([dict(nombre=name,video=str(R/path),cliente=client)],ensure_ascii=False,indent=2))
 job=R/'entregables/fila/pendientes'/f'20261031_084{i}_{ident}.sh'
 job.write_text(f'#!/bin/bash\ncd {R}\npython3 entregables/glimmer_evaluador/evaluar.py {spec} {dest} && GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote {dest}/lote.json --tokens 4500 > {dest}/glimmer.log 2>&1\n')
 caption=f'{name}: {change}\nGlimmer de la versión BASE: {current}/10 actual → {projected}/10 proyectada. Esta versión nueva todavía SIN nota propia; evaluación encolada, un video por lote.\nReferencia real: Guillermo 8.2 logró $4.56/mensaje; $250 ≈55 mensajes si se repitiera ese costo, sin garantía.'
 r=subprocess.run([sys.executable,'herramientas/enviar_seguro.py',path,caption],capture_output=True,text=True);print(r.stdout,r.stderr,flush=True)
 manifest.append(dict(nombre=name,video=path,cola=str(job.relative_to(R)),envio=r.stdout.strip(),anterior_actual=current,anterior_proyectada=projected,nota_nueva='Pendiente'))
 (D/'entregas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
rows=json.loads((D/'prospectos_sin_referencia.json').read_text());chunks=[];msg='Lote 2 · prospectos sin reel enviado por el cliente en los 100 chats revisados. No equivale a no tener referencia: algunos ya tienen una enviada por ti o un video adjunto. Ciudad/giro pendientes se marcan sin inventar.\n'
for r in rows:
 line=f"\n• {r['nombre']} · {r['contacto']}\n{r['giro']} | {r['ciudad']}\nBuscar: {' / '.join(r['busquedas'])}. {r['referencia']}.\n"
 if len(msg)+len(line)>3300:chunks.append(msg);msg=''
 msg+=line
if msg:chunks.append(msg)
receipts=[]
for i,m in enumerate(chunks):
 res=accion('send-message',{'chatId':'44522318905388@lid','message':f'Lista sin reel {i+1}/{len(chunks)}\n'+m});receipts.append(res);print('lista',i+1,res.get('data',{}).get('status') if res else 'fallo',flush=True)
(D/'envio_lista.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2))
