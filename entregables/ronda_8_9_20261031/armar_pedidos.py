from pathlib import Path
import json,re
P=Path('entregables/ronda_8_9_20261031');board=json.loads(re.search(r'<script type="application/json" id="datos">(.*?)</script>',Path('entregables/ruta_clientes_20261030/ruta.html').read_text(),re.S)[1])['clientes']
custom={
'guillermo':('Guillermo, ¿me manda 4 clips verticales de 5 segundos soldando, cortando, pintando e instalando en su taller? Ya tenemos sus audios; los revisamos para conservar lo que pidió.','Carlos debe identificar el video Modal que quiere usar: no dar por aprobada far12 v4b. No confundir anuncio de Nexus con Vicens.'),
'pistas':('¿Qué servicio hacemos primero en el segundo video: audio o pantallas? ¿Me comparte 3 clips reales, zonas, precio desde y qué incluye? Lo dejamos separado de las pistas de vinil.','BD Pro dijo que no recibió mensajes. Carlos revisa estado y destino de campaña en Meta; no afirmar que está activa.'),
'bdpro':('¿Qué servicio hacemos primero en el segundo video: audio o pantallas? ¿Me comparte 3 clips reales, zonas, precio desde y qué incluye?','Verificar campaña y WhatsApp con Carlos.'),
'jose':('José, ¿me comparte un clip corto de una azotea terminada y una foto clara de las cubetas que usa? Nos ayudará a mostrar su trabajo real.','10% ya confirmado por Carlos: no volver a pedirlo. Video actual requiere mejora visual según Glimmer.'),
'alberto':('Alberto, ¿la doctora puede revisar y aprobar el guion de implantes y la oferta desde $12,500, con corona aparte? Si tienen un clip claro de ella en la clínica, nos ayuda mucho.','Voz y gancho los corrige producción. No prometer resultados de salud.'),
'israel':('Israel, ya tenemos el guion de SIRLed y las referencias. ¿Me manda su audio leyéndolo y confirma las zonas, el precio desde y qué incluye el servicio?','No se localizó audio nuevo del guion en los 150 mensajes revisados.'),
'victor':('Víctor, ¿me manda 3 clips verticales de su equipo limpiando una obra real y el resultado terminado? Para el anuncio industrial, confirme zonas, servicios y qué datos necesita para cotizar.','v7 sí tiene evaluación nueva: consultar inventario y final de ronda1a. Carlos verifica campaña y pauta.'),
'giovanni':('Giovanni, ¿nos confirma que sigue vigente divorcio voluntario desde $20,000 y qué incluye? Si tiene un clip suyo en su despacho, nos ayuda a reforzar la confianza.','Corregir voz, experiencia y WhatsApp en producción. No inventar plazos.'),
'fernando':('Fernando, ya recibimos su audio y el guion actualizado. Solo confirme si los $3,500 incluyen IVA y cuál WhatsApp quiere visible al cierre.','No pedir de nuevo el audio: llegó 31 oct 04:02 UTC. Mostrar los accesorios reales y seguir su guion, no el anterior.'),
'manuel':('Manuel, ¿me confirma su ciudad, qué incluye el paquete de XV, precio desde y fechas disponibles? También el WhatsApp para que le manden fecha y ciudad.','v20 ya existe. No usar la nota de v19 como nota de v20.'),
'lisbeth':('Lisbeth, ¿me comparte su WhatsApp nuevo, plano o croquis, medidas, precios y cuántos lotes siguen disponibles? También confirme qué documentos entrega y si agua y luz ya están instaladas o se entregarán después.','No inventar plano ni precios. Sus mensajes dicen “sí tendrán agua y luz”; no convertirlo sin prueba en infraestructura instalada. Confirmar video de presa Cajón de Peña y presupuesto con Carlos.'),
'jesus':('Jesús, ¿me comparte una foto suya y 3 clips trabajando en su taller? Queremos que el video se vea más real. También confirme el WhatsApp que quiere al cierre.','Carlos propuso quitar precios y mostrar proceso como la referencia. Revisar los tres audios nuevos antes de cerrar guion; no atribuir a Jesús una frase de Carlos.'),
'rar':('Don Jesús, ¿qué producto priorizamos en el video de cápsulas y cuál es su precio vigente? ¿Me comparte fotos del envase, ingredientes y el WhatsApp de atención?','Referencia DcdiHfmTjbf. Sin promesas de salud; Carlos verifica WhatsApp Business y campaña.'),
'ruben':('Rubén, ¿me manda un video corto suyo atendiendo en el consultorio, sin pacientes identificables? Confirme si sigue la sesión en $300, horarios y WhatsApp para citas.','Servicio: alineación Alphabiótica, no inventar tratamientos ni curación.'),
'ivan':('Iván, ¿me confirma precios desde por servicio, zonas que atiende y las plagas más frecuentes? Así el anuncio pide zona y plaga antes de cotizar.','Corregir voz de marca en producción. Confirmar pauta con Carlos.'),
'andres':('Andrés, ¿el nombre comercial queda como U Construcción? ¿Me manda 3 clips de obras reales y confirma ciudad, servicios y WhatsApp para cotizar?','Usar otra voz, como pidió; no volver a solicitar las seis fotos ya recibidas.'),
'tatuador':('Adrián, ya tenemos sus videos y la referencia hard cut. ¿Me identifica cuál toma es usted y cuál muestra su cara de frente? Usaremos su material real.','No pedir de nuevo precio: mínimo $1,000, depende diseño/tamaño. No crear su cara con IA. Revisar documentos Adrian 3.mov e IMG_9331.MOV antes de afirmar que falta toma.'),
'rachel':('Rachel, ¿nos confirma cuál referencia de cejas o labios prefiere y si sigue vigente la promoción de $1,899? Carlos le pasa los cuadros para que los apruebe antes de animarlos.','Ya hay fotos y dirección: Calzada Cuauhtémoc 876, Prohogar, Mexicali. No inventar certificación ni apartado.'),
'blanca':('Blanca, ¿pudo grabar el video hablando usted en su consultorio? Con ese material respetamos su cara y voz. Confirme horarios, ciudad y WhatsApp para agendar.','Ya informó valoración $1,800 y terapia $850 semanal. No sustituir con promesa de resultado; rechazó el avatar por cara/lipsync.'),
'mariano':('Mariano, ¿me manda los clips del dron y confirma qué casa priorizamos, precio vigente y qué lugares del desarrollo debemos mostrar? Conservamos el gancho que le compartió Carlos.','Referencia Spider-Man DfEChbGT2px y “puras casas”. Verificar lugares reales antes de animar.'),
'veronica':('Verónica, ¿me manda un video suyo de 10 segundos diciendo el gancho y un recorrido real del departamento? Confirme disponibilidad, precio vigente y WhatsApp de cierre.','Desde $7,600,000 PESOS; no dólares. Revisar referencia y sus audios; no usar el chat de Mr. Patio por error.'),
'ignacio':('Ignacio, ¿sigue disponible la Colorado 2019 en $225 mil a tratar? Confirme ciudad, kilometraje actual y WhatsApp para interesados; ya tenemos sus fotos y el reel.','Referencia Dctql18iSBC. Separar este Ignacio de Ignacio Corona/Generadores. Carlos define pauta y acuerdo de pago.'),
'generadores':('¿Qué generador quiere promocionar primero? Confirme precio desde, capacidad, zonas de entrega y WhatsApp; si tiene un video funcionando, nos ayuda.','Revisar audios antes de insistir en ventas o dar cifras de resultado.'),
'cocinetas':('¿Me confirma la ciudad, su nombre comercial y precio desde? Ya revisamos las fotos disponibles; si tiene un reel de cocinas o clósets que le guste, mándemelo.','No gastar GPU de un caso nuevo sin planteamiento y aprobación.'),
'plomeria':('¿En qué ciudad trabaja y qué servicio quiere promover primero? ¿Me comparte 3 fotos reales, precio desde y un reel de su giro que le guste?','Verificar si ya respondió en su chat antes de enviar.'),
'fumigador':('¿Me confirma las zonas de Aguascalientes que atiende y precio desde por servicio? Ya tenemos una muestra; si hay un trabajo reciente que quiera mostrar, compártalo.','No prometer ventas ni insistir si rechaza seguimiento.'),
'cancel':('Antonio, ya tenemos sus fotos. ¿Me confirma ciudad, nombre comercial, precio desde y WhatsApp de cierre? Si le gusta algún reel de cancelería, mándemelo.','Preparar plan antes de producir caso nuevo.'),
'julio':('Julio, ¿sigue vigente la promoción de 2 pollos por $280 y qué incluye? Confirme dirección, horarios y WhatsApp para pedidos.','Ya hay fotos; no afirmar que existe video final si no está localizado.'),
'luzsonido':('¿Qué paquete de luz y sonido priorizamos? Confirme precio desde, zona y WhatsApp; ya tenemos sus videos. Lo del departamento de Manzanillo va en otro anuncio.','No mezclar servicios.'),
'omar':('Omar, Carlos está revisando con usted cómo resolver el pendiente de su campaña.','Solo Carlos decide devolución o entrega; no prometer fecha ni ejecutar devolución.'),
'uriel':('Uriel, ¿me confirma la oferta y el público del Filtro de Liderazgo y el WhatsApp de atención? Si tiene un video suyo explicándolo en 15 segundos, nos ayuda.','Rehacer guion sobre Filtro de Liderazgo; el video actual no representa la oferta y sigue bajo 8.'),
}
lines=['# Pedidos a clientes · A4','','BORRADORES para aprobación de Carlos. No se envió ninguno. Antes de reenviar, revisar que no hayan respondido después del corte. Se piden únicamente datos pendientes; la edición, el plan 10/10/10 y Glimmer son trabajo de producción.','']
used=set()
for c in board:
 k=c['id'];used.add(k);v=custom.get(k)
 if v:msg,internal=v
 else:
  msg=c.get('msj','').strip()
  # No reutilizar promesas de entregas o datos bancarios del tablero.
  if not msg or any(t in msg.lower() for t in ['ya quedó','le hice','le armé','mañana','mi cuenta','ya tengo','hoy mismo','le muestro','lo mismo','subo']):
   msg='¿Me confirma su giro, ciudad y servicio principal? Compártame 3 fotos reales, precio desde, WhatsApp de atención y un reel de Instagram de su giro que le guste.'
  internal='Pendiente según tablero: '+c.get('falta','Revisar ficha antes de contactar.')
 lines+=['## '+c['n'],'',msg+'\n— La IA de Carlos','', '**Para Carlos/producción:** '+internal,'']
extras={
'Rafael Hernández · BYD':('Rafael, ya tenemos sus fotos y referencias. ¿Me confirma la ciudad y agencia, modelo que quiere anunciar, oferta vigente con condiciones y WhatsApp de atención?','Chat 225412869304444@lid. No inventar enganche, mensualidad ni precio; falta aprobación de plan/costo para gastar GPU de escenas.'),
'Pleiadian Brewing Co.':('¿Qué cerveza y platillo quiere mostrar, con qué precio y horario? Ya tenemos Plaza Puerta del Sur, Nogales, y WhatsApp 631 194 2065. ¿Nos comparte 3 clips del lugar?','Black Hole es stout de café; cocina Desierto Restaurante. Solo mayores de edad.'),
'Sanick':('¿Me confirma dirección, horarios y WhatsApp de atención? También si sigue vigente la promoción de $250 y qué incluye.','Chicoloapan; no prometer curación de nervio ciático. Falta localizar muestra final.'),
'Cinthia · Jayil':('Cinthia, ¿qué servicio de Jayil quiere anunciar primero y cuál WhatsApp de atención usamos? Confirme ciudad y qué información desea recibir de los interesados.','Ya existe tarjeta verde; no confundirla con anuncio de captación. Sin promesas de salud.'),
}
for n,(msg,note) in extras.items():lines+=['## '+n,'',msg+'\n— La IA de Carlos','', '**Para Carlos/producción:** '+note,'']
lines+=['## Control antes de campaña','','Carlos confirma pago/pauta, aprobación del cliente y WhatsApp conectado a su página. Producción verifica video final, voz/cara/textos y nota ACTUAL ≥8. Ninguna proyección sustituye esos requisitos.']
(P/'pedidos_clientes.md').write_text('\n'.join(lines)+'\n');print('borradores',len(board)+len(extras));print('ids',[(c['id'],c['n']) for c in board[:10]])
