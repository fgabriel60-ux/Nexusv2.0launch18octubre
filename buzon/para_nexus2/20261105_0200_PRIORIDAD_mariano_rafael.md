# ⚠️ PRIORIDAD (Carlos, 5 nov 2026, 02:00): MARIANO y RAFAEL primero

Antes que cualquier otro encargo del buzón, trabaja estos dos. Lo demás (tablero, prospectos,
imágenes de los otros clientes) sigue después.

## Rafael · BYD — lo más urgente

**Imágenes** (no existen todavía; el trabajo de Codex se pasó de tiempo y lo mataron sin generar nada).
Son 4 anuncios COMPLETOS, con el texto escrito por Codex dentro de la imagen, guardados en
`entregables/anuncios_imagen_20261104/codex_texto/`:
- `RAFAEL_1A_texto.png` — él junto a un SUV blanco en el piso de exhibición, mano en el cofre.
  Etiqueta AGENCIA BYD · Titular PRUEBA DE MANEJO · Apoyo «Prueba sin compromiso, tú eliges el día» ·
  Viñetas: Te acompaño yo en la prueba / Te digo versiones y disponibilidad / Te contesto yo, no un bot ·
  Nombre «Rafael · Asesor BYD» · Botón «Agendar prueba por WhatsApp».
- `RAFAEL_1B_texto.png` — abriendo la puerta del conductor. Titular SÚBETE Y PRUÉBALO ·
  Apoyo «Agenda tu prueba esta semana» · Viñetas: Tú eliges día y horario / Te acompaño en todo el
  recorrido / Sin compromiso de compra · Botón «Agendar prueba por WhatsApp».
- `RAFAEL_2A_texto.png` — primer plano sonriendo, SUV desenfocado atrás. Titular TE CONTESTO YO, NO UN BOT ·
  Apoyo «Agenda tu prueba de manejo hoy» · Viñetas: Respuesta de una persona real / Te digo versiones y
  precios vigentes / Prueba sin compromiso · Botón «Agendar prueba con Rafael».
- `RAFAEL_2B_texto.png` — con su celular mostrando una conversación de WhatsApp donde se lee
  «Rafael · Asesor BYD». Titular PREGÚNTAME POR WHATSAPP · Apoyo «Dime qué modelo te interesa y qué día
  quieres probarlo» · Viñetas: Te paso versiones y disponibilidad / Te acompaño en la prueba / Te
  contesto yo mismo · Botón «Escribirle a Rafael».

Reglas para las 4: edita a partir de su foto real `clientes/Rafael_BYD/refs/rafael_cara.jpg`, **con su
polo azul marino** (él lo pidió: «con la camisita me vería mejor»), una sola persona, manos bien,
el bloque de texto abajo a la izquierda **sin taparle la cara**. Revisa el texto palabra por palabra.

**Video**: la orden de Carlos, escrita en el chat de Rafael el 4 nov 22:19, es
«si mejoramos ese gancho con tus videos reales ya queda». Arranca con su mejor toma REAL
(`clientes/Rafael_BYD/whatsapp/del_cliente/`, las del 3 nov; ya existe
`clientes/Rafael_BYD/v5_20261104/Rafael_BYD_v5B_sus_tomas.mp4`). Y arregla lo que él dijo:
«a veces la boca cambia» → quita o sustituye los clips donde se le deforma la boca.

## Mariano · Vizcaíno Residencial

**Imágenes**: rehacer sus 4 con Codex escribiendo el texto dentro, **editando sus fotos reales**
(la fachada real de Benjamina está en `clientes/Mariano/anuncios/refs/benjamina_fachada.jpg`;
no sirve una casa inventada en un anuncio inmobiliario). Textos y arreglos exactos en
`20261105_0030_encargo_mariano_arreglar_imagenes.md`: precios por modelo, 3 amenidades, sello
«Mariano Herrera · Asesor · Vizcaíno Residencial» y CTA «Quiero el recorrido» / «Recorrido y precios».

**Video v8 «cuerda mejorada»** (6.5 → 8.5): gancho nuevo con tarjeta «Casa de 2 pisos en Rosarito desde
$2.45 MDP», refuerzo del precio en cada bloque y microcredenciales suyas en la capa inferior.

## Al terminar cada uno

Califica en el portal de Glimmer, manda a Carlos **cada imagen por separado** con su nota y sugerencias
(`mandar_una_por_una.py`), y dile qué falta. Nada abajo de 8 se sube.

---

## AÑADIDO (Carlos, 02:40): el end card de Mariano y las sugerencias en las imágenes

**End card de Mariano: hay que cambiar la foto.** Las que se usaron de `clientes/Mariano/video/v4/`
(C6_cierre, C3_presenta) son cuadros generados viejos y están mal: en uno sale sin camisa y en otro la
cabeza queda flotando. No se vuelven a usar.
Opciones buenas, en este orden:
1. `entregables/anuncios_imagen_20261104/codex/MAR_B2_codex.png` — Codex a partir de su foto real: él con
   el llavero en la entrada de la casa, luz de tarde. Sirve tal cual de end card.
2. `clientes/Mariano/fotos/mariano_luz_final.png` — su foto real con las llaves frente a la casa blanca.
3. Generar una nueva con Codex **editando su foto real**: plano medio, saco azul claro, sonriendo frente a
   la fachada real de Benjamina (`clientes/Mariano/anuncios/refs/benjamina_fachada.jpg`), luz dorada.
El end card lleva: «Mariano Herrera · Asesor · Vizcaíno Residencial», el precio desde $2.45 MDP y el botón
de WhatsApp. Nada de caras generadas que no se parezcan a él.

**Las sugerencias también van a las IMÁGENES, no solo al video.** Cada imagen de cliente que ya tiene
calificación en `entregables/anuncios_imagen_20261104/calificaciones_v2/` trae su bloque
«QUÉ LO FRENA» con el arreglo exacto y cuánto sube. Aplícalos TODOS al regenerar con Codex:
- Mariano: precios por modelo y 3 amenidades visibles, sello del asesor, CTA «Quiero el recorrido» /
  «Recorrido y precios», texto fuera de la cara.
- Rafael: CTA «Agendar prueba por WhatsApp», microtexto de agencia y modelo [FALTA: ciudad, sucursal y
  modelo — pídeselos a Carlos], filtro de intención en el mensaje prellenado, texto fuera del rostro.
- Manuel: oferta concreta en pantalla, logo y WhatsApp visibles, que el texto no tape a la quinceañera,
  dejar claro que es fotografía Y video de toda la fiesta. (Manuel ya aprobó por WhatsApp.)
Después de cada tanda: recalificar y mandar a Carlos cada imagen por separado con su nota.
