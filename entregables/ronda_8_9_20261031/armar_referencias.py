from pathlib import Path
import json,re,datetime
P=Path('entregables/ronda_8_9_20261031');msgs=json.loads((P/'mensajes_normalizados.json').read_text());ids=json.loads((P/'chat_ids.json').read_text());board=json.loads(re.search(r'<script type="application/json" id="datos">(.*?)</script>',Path('entregables/ruta_clientes_20261030/ruta.html').read_text(),re.S)[1])['clientes']
urlpat=r'https?://(?:www\.)?instagram\.com/[^\s<>"\)»]+'
known={'Guillermo':'Herrería, Puebla','Fernando':'Anegocios, punto de venta, CDMX','Jose':'Grupo JR, impermeabilización, Puebla','Alberto':'Veneers Dental, Nogales','Victor':'Servilin, limpieza empresarial','Giovanni':'Abogado, Los Cabos','Ivan':'Fumicam, fumigación','Ruben':'Alineación Alphabiótica','Lisbeth':'Terrenos, Tomatlán','Tatuador':'Tatuajes, Cancún','Andres':'U Construcción, Cd. Juárez','Jesus_Puertas':'Carpintería, Mazatlán','Ignacio':'Venta Chevrolet Colorado 2019 (no confundir con generadores)','BYD_Rafael':'Rafael Hernández, asesor de autos BYD; ciudad por confirmar','Israel':'SIRLed, pantallas LED','Mariano':'Casas, Vizcaíno Residencial/Catania, Rosarito','Blanca':'Hablar Hablando, terapia de lenguaje','Manuel':'Hunab Ku, fotografía XV','BDPro':'Pistas de baile y audio/pantallas, Monterrey','Cinthia':'Jayil, acompañamiento en adicciones','JesusRarAmore':'Rar~Amore, suplementos','Rachel':'Clou SPA, micropigmentación, Mexicali','Uriel':'Filtro de Liderazgo, consultoría','Veronica':'Torre El Charro, Tampico'}
rows=[];covered=set()
for n,cid in ids.items():
 xs=[x for x in msgs if x['chat']==n];links=[]
 for x in xs:
  if x['type']!='chat':continue
  for u in re.findall(urlpat,x['body']):
   links.append((u,'Carlos' if x['fromMe'] else 'cliente',x['id']))
 unique=list(dict.fromkeys((u,by) for u,by,_ in links));received=sum(1 for x in xs if not x['fromMe'] and x['type']=='image');audio=sum(1 for x in xs if not x['fromMe'] and x['type'] in ['audio','ptt']);vid=sum(1 for x in xs if not x['fromMe'] and x['type'] in ['video','document'])
 reel=[(u,by) for u,by in unique if '/reel/' in u or '/p/' in u]
 status='; '.join(f'{by}: {u}' for u,by in unique) or 'No localizado en los mensajes revisados'
 if n=='Tatuador':status+='; referencia hard cut recibida como VIDEO (30 oct 19:57), no enlace de Instagram'
 rows.append((bool(reel) or n=='Tatuador',f'| {n.replace("_"," ")} | {cid}@lid | {known.get(n,"Sin giro confirmado")} | {status} | {received} imágenes, {audio} audios, {vid} videos/documentos recibidos; chats/{n}.json |'))
 covered.add(cid)
# Auditoría histórica adicional: no supone que todo chat sea un prospecto comercial.
extra=[]
for f in Path('entregables/analisis_clientes_20261030/digest').glob('*.txt'):
 s=f.read_text();m=re.search(r'\((\d+)@lid\)',s)
 if not m or m[1] in covered:continue
 cid=m[1];name=s.splitlines()[0].removeprefix('# ').split(' (')[0];links=[]
 for l in s.splitlines():
  for u in re.findall(urlpat,l):links.append(('Carlos' if 'YO' in l else 'cliente' if 'EL' in l else 'autor sin confirmar',u))
 links=list(dict.fromkeys(links));bc=next((c for c in board if c['n'].lower().split(' ·')[0] in name.lower() and len(c['n'])>5),None)
 giro=bc['g'] if bc else 'No confirmado en esta ficha; ver digest'
 images=bool(re.search(r'EL\[image\]',s));audio=bool(re.search(r'EL\(audio\)|EL\[ptt\]|EL\[audio\]',s));video=bool(re.search(r'EL\[video\]|EL\[document\]',s))
 linkstr='; '.join(f'{by}: {u}' for by,u in links) or 'No localizado'
 extra.append((any('/reel/' in u for _,u in links),f'| {name} | {cid}@lid | {giro} | {linkstr} | fotos: {"sí" if images else "no consta"}; audio: {"sí" if audio else "no consta"}; video: {"sí" if video else "no consta"}; {f} |'))
lines=['# Referencias y material · A3','','Se distingue quién envió el enlace: cliente o Carlos. Tener referencia de Carlos no significa que la haya enviado el prospecto. “No localizado” solo describe la evidencia revisada. Conteos = mensajes recibidos, no archivos únicos.','','## Con referencia disponible','','| Prospecto/cliente | Teléfono o chatId | Giro | Reel exacto y quién lo mandó | Fotos/audio |','|---|---|---|---|---|']
lines.extend(r for ok,r in rows if ok)
lines+=['','## Sin reel localizado (Carlos les busca o confirma referencia)','','| Prospecto/cliente | Teléfono o chatId | Giro | Reel exacto y quién lo mandó | Fotos/audio |','|---|---|---|---|---|'];lines.extend(r for ok,r in rows if not ok)
for yes,title in [(True,'Índice histórico adicional con referencia'),(False,'Índice histórico sin referencia localizada')]:
 lines+=['',f'## {title}','','Este índice incluye contactos sin giro identificado; no se declara que todos sean prospectos activos. Fuente: digest del 30 oct. No se envió ningún mensaje.','','| Contacto | chatId | Giro | Enlaces | Material recibido |','|---|---|---|---|---|'];lines.extend(r for ok,r in extra if ok==yes)
lines+=['','## Referencias reenviadas en el chat de Carlos','', 'Se pidió primero limit 150; para ampliar a tres días se pidió limit 500. WaAPI devolvió 250 mensajes, desde el 28 oct 20:15 UTC; no cubre 72 h completas. Se cruzó además el archivo chat_carlos_200.txt. No se atribuye un reel a un cliente si el mensaje no lo identifica.','']
for w in json.loads((P/'carlos_3dias.json').read_text())['data']['data']:
 d=w['message']['_data']
 if d.get('type')!='chat':continue
 for u in re.findall(urlpat,d.get('body','')):lines.append(f'- {datetime.datetime.fromtimestamp(d["t"],datetime.timezone.utc).isoformat()}: {u}. Mensaje `{d["id"]["_serialized"]}`. Contexto: {d["body"][:350]}')
lines+=['','Correspondencia confirmada por memoria/archivos: DdRkpj4xfm2 → José (obrero Pixar); DasdFyGlBeq → referencia de proceso/cocina vinculada a Fernando en memoria obrero-modal-cola.md. DfAGEf8Tbvs no se asigna por suposición.','',f'Se revisaron {len(rows)} chats actuales y {len(extra)} fichas adicionales históricas.']
(P/'prospectos_referencias.md').write_text('\n'.join(lines)+'\n');print('filas',len(rows),len(extra))
