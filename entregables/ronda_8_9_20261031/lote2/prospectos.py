from pathlib import Path
import re,json
P=Path('entregables/ronda_8_9_20261031');s=(P/'chats_recientes.txt').read_text()
# Datos confirmados en contexto/archivos; ciudad desconocida no se deduce por lada.
known={
'250053667119335':('Adrián','Tatuajes','Cancún','tatuador trabajando hard cut','tatuaje terminado detalle estudio'),
'77185511633028':('Jesús Puertas','Carpintería','Mazatlán','carpintería puerta parota proceso','cocina melamina fabricación instalación'),
'117725154296056':('Julio César','Por confirmar (no asumir rosticería sin identificar)','Por confirmar','[giro por confirmar] proceso real','[giro por confirmar] antes después'),

'214925314125860':('Prospecto bienestar','Terapias/bienestar; especialidad por confirmar','Por confirmar','terapeuta presentación consultorio','terapia bienestar preguntas frecuentes'),
'39724370628839':('Despacho contable','Contabilidad','Por confirmar','contador para negocios reel','despacho contable asesoría emprendedores'),
'230536849182782':('Cursos de inglés','Inglés general y de negocios','Por confirmar','business english clase muestra','curso inglés conversación adultos'),
'250719353442519':('Carpintería Cadena','Cocinetas y clósets','Monterrey','cocina integral antes después','carpintería closet proceso fabricación'),
'62144250904789':('Casas en fraccionamiento','Venta de casas','Por confirmar','casa fraccionamiento recorrido agente','casa nueva tour amenidades'),
'7292988711081':('Plomería y electricidad','Plomería y electricidad','Mazatlán','plomero reparación fuga antes después','electricista instalación residencial'),
'262577305219104':('Cancelería','Aluminio y cristal','CDMX','cancel aluminio instalación proceso','cancel baño cristal antes después'),
'216041770741763':('Eventos / departamento de su hermana','Eventos; renta de departamento','Manzanillo solo el departamento','montaje evento antes después','departamento Manzanillo tour renta'),
'155959590658268':('Royal Honey VIP','Comercialización Royal Honey VIP','Mérida','producto empaque presentación tienda','tienda producto unboxing sin promesas'),
'259682430128161':('Internet','Servicio de internet','Ciudad Juárez','internet hogar instalación técnico','internet negocio cobertura servicio'),
'74333166797031':('Finanzas e Inmobiliaria','Venta de propiedades','Por confirmar','asesor inmobiliario recorrido propiedad','casa venta tour detalles'),
'24709718618270':('Serenatas y eventos','Música para serenatas y XV años','Por confirmar','serenata presentación grupo musical','música en vivo quinceañera'),
'189026124464199':('Plataforma streaming','Plataforma de streaming','Por confirmar','plataforma streaming demostración app','streaming catálogo presentación servicio'),
'127857351200908':('Impacto Publicidad','Imprenta gran formato, lona y vinil','Por confirmar','impresión gran formato proceso','rotulación vinil antes después'),
'109350605598921':('Plomería y electricidad','Plomería y electricidad','Por confirmar','plomero reparación fuga proceso','electricista instalación segura'),
'31615388487861':('Maquillaje y flores','Sombras, aretes y ramos','Por confirmar','ramo rosas armado proceso','maquillaje accesorios producto reel'),
'222870970093821':('Música en YouTube','Música; proyecto inicial','Por confirmar','cantante acapella presentación','videoclip músico independiente'),
'52974797778979':('Cinthia · Jayil','Acompañamiento en adicciones','Por confirmar','acompañamiento adicciones presentación profesional','centro apoyo adicciones preguntas frecuentes'),
'99621917425766':('Blanca · Hablar Hablando','Terapia de lenguaje','Por confirmar','terapeuta lenguaje consultorio presentación','terapia lenguaje actividad ejemplo'),
'233916904525900':('Rachel · Clou SPA','Micropigmentación','Mexicali','micropigmentación cejas proceso real','especialista cejas presentación estudio'),
'177558293323885':('Manuel · Hunab Ku','Fotografía XV años','Por confirmar','fotógrafo quinceañera detrás cámaras','sesión XV años resultado'),
'57844753760482':('Verónica Argüelles','Departamentos Torre El Charro','Tampico','departamento lujo recorrido agente','dron interior departamento amueblado'),
'54022266478629':('Ignacio · Energy Controlled','Generadores','Por confirmar','generador eléctrico demostración','planta emergencia instalación'),
'244250780389552':('Víctor · Servilin','Limpieza para empresas','Por confirmar','limpieza obra fina antes después','limpieza industrial equipo trabajando'),
'147832891793521':('Giovanni Pulido','Abogado divorcios','Los Cabos','abogado divorcio presentación despacho','divorcio voluntario preguntas frecuentes'),
'121135308009543':('Alberto · Veneers Dental','Odontología','Nogales','dentista presentación clínica','implante dental explicación sin promesas'),
'214649748369481':('BD Pro','Pistas y servicios para eventos','Monterrey','pista baile montaje evento','audio iluminación evento montaje'),
'256998142660619':('Guillermo · Vicens','Herrería','Puebla','herrería techo instalación proceso','portón herrería antes después'),
'161641681395864':('Lisbeth','Terrenos','Tomatlán','terreno venta recorrido dron','lotes cerca playa recorrido'),
'252291428913257':('Lisbeth · número nuevo','Terrenos','Tomatlán','terreno venta recorrido dron','lotes cerca playa recorrido'),
'257883358937112':('José · Grupo JR','Impermeabilización','Puebla','impermeabilización azotea proceso','impermeabilizante antes después lluvia'),
'186389366857933':('José · otro chat','Impermeabilización','Puebla','impermeabilización azotea proceso','impermeabilizante antes después lluvia'),
'263766994321528':('Fernando · Anegocios','Punto de venta','CDMX','punto venta demostración negocio','impresora tickets lector instalación'),
'72125973008625':('Iván · Fumicam','Fumigación','Cuernavaca/CDMX','fumigación servicio proceso','control plagas negocio técnico'),
'25112875143230':('Rubén','Alineación Alphabiótica','Zinacantepec/Metepec','consultorio bienestar presentación','sesión bienestar explicación sin promesas')}
# No se clasifican conversaciones personales, proveedores entrantes o rechazo explícito como prospectos activos.
exclude={'57372793950429':'Personal','251419567337705':'Socio','117472321663152':'Personal','7967818657796':'Personal','207623165083740':'Rechazó propuesta','215920991563840':'Pidió dejarlo para después','26917315031157':'Proveedor de formación','155358110683290':'Publicidad de viajes entrante','249992900006009':'Respuesta automática restaurante','252136776572995':'Respuesta automática renta autos','236704539627655':'Gestión de Lisbeth; no prospecto distinto'}
rows=[];already=[];excluded=[]
for b in re.split(r'(?=^===== CHAT)',s,flags=re.M):
 if not b.strip():continue
 h=b.splitlines()[0];m=re.search(r'CHAT (.*?) \[(\d+)@lid\]',h)
 if not m:continue
 name,cid=m.groups()
 if cid in exclude:excluded.append((name,cid,exclude[cid]));continue
 client_reel=any('] CLIENTE chat ' in l and re.search(r'instagram\.com/(?:reel|reels)/',l) for l in b.splitlines())
 if client_reel:already.append((name,cid));continue
 k=known.get(cid,(name,'Por confirmar','Por confirmar','[giro por confirmar] proceso real','[giro por confirmar] antes después'))
 phone=re.search(r'\+\d[\d ()-]+',name);contact=phone[0].strip() if phone else cid+'@lid (teléfono pendiente)'
 other='Carlos compartió reel en este extracto' if re.search(r'instagram\.com/(?:reel|reels)/',b) else 'Sin reel en el extracto'
 rows.append(dict(nombre=k[0],contacto=contact,chat=cid+'@lid',giro=k[1],ciudad=k[2],busquedas=k[3:],referencia=other))
lines=['# Prospectos sin reel enviado por el cliente · lote 2','','Fuente: chats_recientes.txt, 100 conversaciones. “No mandó reel” significa que no consta un enlace de reel enviado por el cliente en este extracto; no prueba ausencia en todo su historial. Un video adjunto o perfil de Instagram no se cuenta como enlace de reel. Incluye clientes existentes para no omitir pendientes. Las búsquedas son propuestas, no referencias verificadas. No se deduce ciudad de la lada.','','| Nombre / contacto | Giro | Ciudad | 2 búsquedas sugeridas en Instagram | Referencia en este extracto |','|---|---|---|---|---|']
for r in rows:lines.append(f"| {r['nombre']} · {r['contacto']} | {r['giro']} | {r['ciudad']} | {' / '.join(r['busquedas'])} | {r['referencia']} |")
lines+=['','## Excluidos con motivo','']+[f'- {n} ({cid}@lid): {why}.' for n,cid,why in excluded]
lines+=['','## Sí enviaron un enlace de reel en el extracto','']+[f'- {n} ({cid}@lid).' for n,cid in already]
lines+=['','## Cruce con historial disponible','','Consultar prospectos_referencias.md antes de buscar: varios clientes tienen reels enviados por Carlos en chats anteriores aunque aquí no aparecen. Adrián recibió y envió referencia como archivo de video; no se debe pedirle que repita material ya recibido. Los contactos con giro pendiente necesitan identificación antes de elegir un reel.']
(P/'prospectos_sin_referencia.md').write_text('\n'.join(lines)+'\n');(P/'lote2/prospectos_sin_referencia.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(len(rows),'sin reel cliente;',len(already),'sí;',len(excluded),'excluidos')
