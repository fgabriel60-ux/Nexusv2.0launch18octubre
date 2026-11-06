# Encargo: hacer las imágenes de TODOS igual que las de Rafael (4 nov 2026, 23:20)

Carlos lo pidió así: «dile al Claude de Modal que haga la orden que te puse en Rafael».
O sea: lo que ya quedó hecho para **Rafael (BYD), Mariano y Manuel**, repetirlo para el resto de los
clientes y prospectos. No es describir imágenes: es **generarlas y dejarlas listas para subir a Meta**.

## Qué es «la orden de Rafael», exacto

Por cada negocio: **2 ángulos de venta** y **2 imágenes por ángulo = 4 anuncios**, formato **4:5 (1080x1350)**,
con foto real del cliente, titular corto, línea de apoyo y botón de WhatsApp, y el texto SIEMPRE en capa
aparte (nunca generado dentro de la imagen).

## Lo que ya está hecho (no lo repitas)

- Ángulos y guiones escritos de 15 negocios: `entregables/glimmer_imagenes_20261104/prioridad/*.md`
  (tatuador, Mariano, Rafael, Giovanni, Fernando, Rubén, ginecólogo, oficinas amuebladas León, Lisbeth,
  Víctor, Rashel Carrasco, Jesús Puertas, Ignacio Iglesia, Jesús cápsulas, Manuel).
- Ronda previa con 5 ideas de imagen por cliente: `entregables/glimmer_imagenes_20261104/clientes/*.md`.
- **Imágenes YA generadas (12)**: `entregables/anuncios_imagen_20261104/anuncios/` → MARIANO_*, RAFAEL_*, MANUEL_*.

## Lo que falta (tu trabajo)

1. Las 4 imágenes de cada uno de los demás: **Giovanni, Fernando, Rubén, Lisbeth, Víctor, Ignacio Iglesia,
   Jesús cápsulas, Adrián tatuador, Jesús Puertas, Rashel Carrasco, ginecólogo y oficinas amuebladas León.**
2. Los **10 prospectos** que faltan de estrategia: ya está armado el lote
   `entregables/glimmer_imagenes_20261104/lote2_prospectos.json` (2 ángulos + 2 static ads + guion).

## La receta que funcionó (cópiala tal cual)

1. **Refs = fotos REALES del cliente.** Búscalas en `clientes/<Cliente>/whatsapp/del_cliente/`,
   `clientes/<Cliente>/fotos/` y en fotogramas de SUS videos (ffmpeg). Antes de usar un fotograma, revisa
   que no traiga rótulos pegados: a Mariano le salió un «2.8M MXN» viejo dentro de la imagen generada.
2. **Spec de Qwen** como `entregables/anuncios_imagen_20261104/spec_mariano_rafael.json`:
   `{"carpeta","salida","semilla","ancho":1024,"alto":1280,"pasos":30,"refs":{...},"cuadros":{"NOMBRE":[[refs],"prompt","negativo extra"]}}`
   - El prompt empieza SIEMPRE con «Una sola persona: el mismo hombre/la misma mujer de la primera foto,
     misma cara...» y describe ropa real. En el negativo: `dos personas, persona duplicada, gemelo, texto,
     logotipos inventados, manos deformes`. Sin eso salen dos copias de la persona (le pasó a Rafael).
3. **Generar:**
   `GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/_escenas_carlos/escenas_carlos_modal.py::cuadros_par --spec <spec>.json`
   (A100 en paralelo, ~3-4 min por tanda de 4-6 cuadros.)
4. **Componer el anuncio** con `entregables/anuncios_imagen_20261104/armar_anuncios.py`: ahí están las
   funciones `anuncio()` (degradado + titular + línea + botón de WhatsApp + etiqueta + pie), `collage3()`
   (una foto grande y dos abajo) y `logo()`. Agrega una función por cliente igual que `manuel()` y corre
   el script. Salida en `entregables/anuncios_imagen_20261104/anuncios/`.
5. **Revisa cada imagen antes de darla por buena**: una sola persona, cara parecida a la real, manos bien,
   sin texto inventado dentro de la foto, y que el titular se lea sobre el fondo.
6. **Datos**: solo precios y datos que el cliente haya dado por escrito o rotulado él mismo en sus videos.
   Si falta, no lo pongas y anótalo como `[FALTA: ...]`.

## Al terminar

- Arma una hoja por cliente (2x2) y mándasela a Carlos con `python3 herramientas/enviar_seguro.py RUTA "texto"`,
  diciendo qué ángulo es cada imagen, qué foto es real y qué falta que mande el cliente.
- No le escribas a ningún cliente sin que Carlos lo pida en ese mensaje.
