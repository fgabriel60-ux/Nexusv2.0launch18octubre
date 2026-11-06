# ⚠️ nexus3 · LO QUE TIENES QUE HACER (Carlos, 5 nov 2026, 03:45)

Carlos: «dile a nexus que haga los cambios en videos del tablero y las imágenes de los clientes».
Esta es la lista única, en orden. Los detalles finos están en los encargos que se citan.

## 1) Videos del tablero — los cambios de cada cliente

El tablero ya está **reordenado: arriba los más fáciles de subir a 8** y con la etiqueta **«sin GPU»**
o **«escenas»**. Cada cliente tiene además un botón **«⚡ Aplicar los cambios ya»** que te deja el encargo
en este mismo buzón.
https://charlyfavela666--tablero-nexus-web.us-east.modal.run/?k=i7_8usCbRdED_8lp

**Empieza por los «sin GPU»** (Carlos todavía no tiene crédito para escenas nuevas):
1. **Rafael · BYD** (7.0): gancho con SUS tomas reales —su orden textual: «si mejoramos ese gancho con tus
   videos reales ya queda»— y quitar los clips donde se le deforma la boca. Detalle en
   `20261105_0200_PRIORIDAD_mariano_rafael.md`.
2. **Fumigador** (6.0) y **Caracol Península** (5.0).
3. **Mariano** (6.5 → 8.5): gancho con tarjeta «Casa de 2 pisos en Rosarito desde $2.45 MDP», refuerzo del
   precio en cada bloque, microcredenciales suyas, y **end card con foto buena** (no los cuadros viejos
   donde sale sin camisa o con la cabeza flotando).
4. Los que piden escenas nuevas (Jesús RIMO, Guillermo, Víctor, Rubén, Fernando, Alberto, Israel, Manuel)
   **esperan crédito**; sus imágenes sí se pueden hacer ya.

Para cada video: aplica lo que dice «QUÉ LO FRENA» de su calificación, versiona, recalifica en el portal
de Glimmer y manda el resultado a Carlos con la nota actual y la proyectada separadas.

**Referencia de cómo quedó bien** (Adrián, de 3/10 a **9/10** esta madrugada):
subtítulos en frases cortas que no se cortan · tarjeta de nombre y de ubicación · **testimonios reales
cayendo en burbujas** (la burbuja la generó Codex con fondo transparente y se le escribe el texto encima)
· ráfaga de 10 trabajos a 0.30 s con clic de cámara en cada corte · pregunta de filtro · cierre con CTA.
Scripts: `clientes/Tatuador9983316522/v3_subs/armar_tatuador_v10.py` y `..._v11.py`.
**Ojo con el audio**: no apliques `loudnorm` sobre el video ya pegado, porque bombea en los silencios y
mete ruido; normaliza solo el tramo con voz, codifica cada tramo igual (AAC 44.1 kHz estéreo) y pega con
`-c copy`.

## 2) Imágenes de TODOS los clientes

Con **Codex**, y **él escribe el texto dentro de la imagen** (ya no capa de PIL). Cuando el anuncio enseña
algo real del cliente (su cara, su casa, su producto), que **edite la foto real**, no que invente.
El contenido sale de `entregables/glimmer_imagenes_20261104/prioridad/*.md` (2 ángulos y 2 anuncios por
negocio). Detalle y comandos en `20261105_0210_encargo_imagenes_todos_con_codex.md`.

Orden: **Rafael y Mariano primero** (sus 4 cada uno, aplicando las correcciones de
`entregables/anuncios_imagen_20261104/calificaciones_v2/`), después el resto de clientes, al final los
prospectos. Cada imagen se califica y se le manda a Carlos **por separado** con su nota y sugerencias
(`entregables/anuncios_imagen_20261104/mandar_una_por_una.py`).

## 3) Prospectos

Son tuyos: `20261105_0330_PROSPECTOS_nuevos_son_tuyos.md`.

## 4) App de Amy

Revisar cada mañana los comentarios de la app y aplicarlos: `20261105_0100_encargo_amy_app_comentarios.md`.

## Regla de siempre

Nada abajo de 8 se sube a pauta. No le escribas a ningún cliente sin que Carlos lo pida en ese mensaje.
