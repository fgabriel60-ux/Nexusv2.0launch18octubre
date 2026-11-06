import json,re,shlex
from pathlib import Path
P=Path('entregables/ronda_8_9_20261031');G=Path('entregables/glimmer_evaluador');R=Path.cwd()
inv=json.loads((P/'inventario.json').read_text());tab=json.loads(re.search(r'<script type="application/json" id="datos">(.*?)</script>',Path('entregables/ruta_clientes_20261030/ruta.html').read_text(),re.S)[1])['clientes']
context=Path('/vol/claude-config/codex/contexto_carlos.md').read_text()
keys={'Guillermo':'guillermo','BD Pro':'pistas','José':'jose','Doctora / Alberto':'alberto','Víctor':'victor','Giovanni':'giovanni','Fernando':'fernando','Manuel':'manuel','Lisbeth':'lisbeth','Jesús Puertas':'jesus','Tatuador / Adrián':'tatuador','Rachel':'rachel','Blanca':'blanca','Mariano':'mariano','Verónica':'veronica','Iván':'ivan','Andrés':'andres','Rubén':'ruben','Uriel':'uriel','Ignacio Corona / Generadores':'generadores','Fumigaciones Chávez':'fumigador'}
allitems=[]
for x in inv:
 k=keys[x['cliente']];c=next((c for c in tab if c['id']==k),{})
 lines=[l.strip('| ') for l in context.splitlines() if l.startswith('|') and any(s in l.lower() for s in [k, x['cliente'].split(' /')[0].lower()])]
 facts=f"{x['cliente']}. Giro confirmado en tablero: {c.get('g','ver contexto')}. "+' '.join(lines)
 if k=='jose':facts+=' Descuento 10% confirmado por Carlos el 31 oct. No penalizar por falta de confirmación del descuento.'
 if k=='fernando':facts+=' Ya envió audio el 31 oct 04:02 UTC y guion actualizado: paquete $3500, instalación y capacitación CDMX/área metropolitana; soporte en llamada un año sin costo; paga al funcionar. IVA: confirmar, el guion del cliente no lo menciona.'
 if k=='guillermo':facts+=' Esta es far12 v4b con voz; Carlos pidió base Modal anterior (techo) y aún se distingue entre las versiones caen/suben. Esta evaluación no valida que sea la base elegida.'
 if k=='jesus':facts+=' Carlos propuso quitar precios y hacerlo más realista (30 oct 22:40-22:44 UTC); son instrucciones de Carlos, no una frase escrita del cliente. Revisar audios del cliente.'
 if k=='tatuador':facts+=' Cliente rechaza avatar IA; editar su material real con cara del tatuador identificado. Mínimo $1000; depende de diseño/tamaño.'
 allitems.append({'nombre':re.sub(r'[^A-Za-z0-9]+','_',k.upper()+'_'+x['version']),'video':x['video'],'cliente':facts})
(G/'anuncios_ronda1_20261031.json').write_text(json.dumps(allitems,ensure_ascii=False,indent=2))
covered=set()
for f in [G/'anuncios_ronda1a_20261031.json',G/'anuncios_ronda1b_20261031.json']:
 for it in json.loads(f.read_text()):covered.add(str(Path(it['video']).resolve()))
rest=[it for it in allitems if str(Path(it['video']).resolve()) not in covered]
notes=['# Fase A2 · manifiesto y cola','',f'Inventario: {len(allitems)} videos. Dos lotes preexistentes cubren {len(covered)}; no se vuelven a lanzar. Se completan {len(rest)} videos en dos lotes adicionales de máximo 8. Los manifiestos a/b y sus resultados se preservan.','', 'Datos: tablero ruta.html + contexto_carlos.md; correcciones con mensajes originales guardados en chats/.','', 'Manifiesto maestro: entregables/glimmer_evaluador/anuncios_ronda1_20261031.json.','']
commands=[]
for letter,start in [('c',0),('d',8)]:
 arr=rest[start:start+8]
 if not arr:continue
 lid=f'ronda1{letter}_20261031';mf=G/f'anuncios_{lid}.json';dest=G/lid;mf.write_text(json.dumps(arr,ensure_ascii=False,indent=2));dest.mkdir(exist_ok=True)
 cmd=f'python3 entregables/glimmer_evaluador/evaluar.py {mf} {dest} && GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote {dest}/lote.json --tokens 4500 > {dest}/glimmer.log 2>&1'
 # Idempotencia: no recalificar si ya hay respuestas finales suficientes.
 commands.append(f"if [ \"$(grep -o 'assistant to=user' {dest}/glimmer.log 2>/dev/null | wc -l)\" -lt {len(arr)} ]; then\n  {cmd}\nfi")
 notes.append(f'- {lid}: '+', '.join(it['nombre'] for it in arr))
queue=Path('entregables/fila/pendientes/20261031_0700_ronda1.sh')
if not queue.exists() and not (queue.parent.parent/'hechos'/queue.name).exists():
 queue.write_text('#!/bin/bash\nset -e\ncd '+shlex.quote(str(R))+'\n'+ '\n'.join(commands)+'\n')
notes+=['','Cola complementaria: '+str(queue), 'Solo utiliza gasto_modal.py con perfil carlosfavelajeje y respeta su tope. No genera escenas. No modifica credenciales ni límites.','La fila ya estaba activa por encargo de Claude; no se cambia su pausa/horario. La fase A2 pide encolar, no esperar todos los resultados.']
(P/'lotes_glimmer.md').write_text('\n'.join(notes)+'\n')
print('maestro',len(allitems),'ya cubiertos',len(covered),'encolados',len(rest))
