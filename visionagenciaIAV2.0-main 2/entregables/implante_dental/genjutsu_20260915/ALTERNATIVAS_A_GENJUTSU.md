# Alternativas a Genjutsu (Higgsfield) en WaveSpeed — probadas el 16 sep 2026

Carlos: «¿habrá una alternativa a Genjutsu de Higgsfield en WaveSpeed que sea barata? está tardando mucho».
Se probaron dos con el **tramo A real del implante**, no con ejemplos.

## Qué hace Genjutsu y qué hay que igualar

Motion Transfer: video de movimiento (3 a 30 s) + hasta 40 imágenes de referencia + prompt → video con otro look
que respeta el movimiento original. Lo que hay que igualar: **respetar el tiempo**, **usar imágenes de referencia**
y **aguantar 18 segundos**.

## Prueba 1 — `decart/lucy-restyle` · $0.01 · 100 segundos

Entrada: tramo A completo (18 s, 432×768). Sin imágenes de referencia, el modelo no las acepta.

**No sirve para este trabajo.** Tres fallas:

1. **Rompió el tiempo.** Entraron 540 cuadros a 30 fps (18 s) y salieron 863 a 24 fps (35.96 s). No fue un cambio
   de etiqueta de fps: re-cronometró el video. El movimiento queda a media velocidad y descuadra con la voz.
2. **Nunca hizo el corte anatómico.** Se quedó en la cara de la mujer los 36 segundos: sin sección del maxilar, sin
   sticker que se despega, sin hueso ni implante.
3. **Pintó los dientes de verde turquesa** y los labios de rosa neón. Tomó el «deep teal» del prompt, que era para
   el fondo, y se lo puso a los dientes. Sin imágenes de referencia no tiene cómo saberlo.

A favor: barato, rápido, subió a 704×1280 y no tiene tope de duración. Sirve para repintar una toma sencilla.

Archivos: `prueba_lucy_restyle.py`, `PRUEBA_LUCY_RESTYLE_TRAMO_A.mp4`, `REVISION_LUCY.jpg`.

## ⚠️ Corrección de costos (16 sep, tras revisar el saldo)

**Los precios de lista engañan.** El saldo de WaveSpeed pasó de **$7.87 a $5.01** con solo estas dos pruebas:
**$2.86 reales** contra los $0.26 que suman los precios de lista. Once veces más.

WaveSpeed no reporta el cobro por trabajo, así que no se puede separar exactamente cuánto fue cada una, pero el
grueso es de MiniMax: el `base_price` corresponde a la unidad mínima, y **la duración y la resolución multiplican**.
Se pidieron 15 s a 768p. Antes de lanzar cualquier otra prueba de video, contar con que el costo real puede ser
un orden de magnitud mayor que el de lista, y medirlo con el saldo antes y después.

## Prueba 2 — `wavespeed-ai/minimax-h3/video-edit` · lista $0.25, **real ≈ $2.85** · 1,249 segundos (21 min)

Entrada: tramo A recortado a 15 s (su tope), más **5 imágenes de referencia** (los cuadros 01 a 05), `768p`,
`generate_audio: false` para no inventar audio.

**Sí reemplaza a Genjutsu en calidad.** Lo que logró y lucy no:

1. **Respetó el tiempo:** 15.08 s de salida contra 15.0 s de entrada, a 768×1344. Sin estirones.
2. **Hizo el corte anatómico y el sticker**: el rostro se despega y revela el maxilar con hueso poroso, encía,
   raíces y el implante de titanio.
3. **Respetó el look de la hoja de Alberto**: dientes blancos brillantes, encía rosa, fondo casi negro con bokeh
   turquesa y naranja. Las imágenes de referencia sí funcionaron.
4. La aguja de la anestesia entra en la encía en el punto correcto.

**Dos problemas reales:**

- **Tardó 21 minutos** por 15 segundos de video, contra los 100 segundos de lucy. Si el motivo de buscar
  alternativa era la lentitud, este no la resuelve.
- **Le salió sangre escurriendo** en el tramo final, pese a que el prompt decía «anatomically clean, not gore».
  Hay que reforzar el negativo o rehacer ese pedazo.

Archivos: `prueba_minimax_edit.py`, `PRUEBA_MINIMAX_EDIT_TRAMO_A.mp4`, `REVISION_MINIMAX.jpg`.

## Comparación

| | lucy-restyle | minimax video-edit | Genjutsu |
|---|---|---|---|
| Precio | $0.01 | $0.25 | créditos Higgsfield |
| Tiempo (15-18 s) | 100 seg | 21 min | lento, según Carlos |
| Imágenes de referencia | ninguna | **hasta 9** | hasta 40 |
| Tope de duración | sin tope | 15 s | 30 s |
| ¿Respeta el tiempo? | **no**, lo duplicó | **sí** | sí |
| ¿Hizo el corte y el sticker? | **no** | **sí** | sí |

Los 35 s del implante: con MiniMax salen en 3 pedazos ≈ **$0.75**; con lucy, $0.02 pero inservible.

## Prueba 3 — `wavespeed-ai/ltx-2-19b/control`, modo profundidad · lista $0.20, **real $0.54** · 153 segundos

Entrada: tramo A **completo, 18 s sin recortar** (su tope es 20 s), 1 imagen de referencia (cuadro 04, el único
que permite), `mode: depth`, `resolution: 480p`, `audio_mode: none`. Saldo medido antes y después: $5.01 → $4.47.

**Gana en velocidad y precio, falla en la transición.**

A favor:
1. **2 minutos y medio**, contra los 21 minutos de MiniMax. Es la única opción que resuelve la lentitud.
2. **$0.54 real**, 2.7 veces el precio de lista, contra las 11 veces de MiniMax.
3. **Respetó la duración:** 17.71 s de salida contra 18.0 de entrada, 425 cuadros a 24 fps. Sin estirones.
4. **La guía por profundidad conservó la geometría del render de Blender**: cara, encuadre y movimiento fieles.
   Esto confirma que el método de 3D primero sí se puede aprovechar con control por profundidad.

En contra:
- **No hizo el corte anatómico ni el sticker.** En vez de despegar el rostro y revelar la sección del maxilar,
  superpuso un armazón con dientes y raíces flotando sobre los labios, como calcomanía encima de la cara. El
  instrumento queda fuera de la boca.
- Causa: **solo acepta una imagen de referencia**. MiniMax usó cinco y por eso sí entendió la anatomía.
- Salida a 448×832, la más baja de las tres.

Archivos: `prueba_ltx_control.py`, `correr_ltx_y_avisar.py`, `PRUEBA_LTX_DEPTH_TRAMO_A.mp4`, `REVISION_LTX.jpg`,
`recibo_ltx.json`.

## Conclusión de las tres pruebas

| | lucy-restyle | LTX depth | MiniMax video-edit |
|---|---|---|---|
| Costo real | $0.01 | **$0.54** | ~$2.85 |
| Tiempo | 100 seg | **2.5 min** | 21 min |
| Respeta el tiempo | no | **sí** | **sí** |
| Imágenes de referencia | 0 | 1 | **5 (hasta 9)** |
| Hace el corte y el sticker | no | no | **sí** |

**Para el video del implante, donde la transición es el truco, MiniMax es el único que sirve.** LTX queda para
retoques de tomas simples donde solo se cambie el look, con la ventaja de ser 8 veces más rápido y 5 veces más
barato. lucy queda descartado.

## Wan Animate en Modal: bloqueado (16 sep)

Carlos pidió correr Wan 2.2 Animate en la GPU de Modal. **No se puede hoy**, por dos razones distintas:

- Cuenta `charlyfavela1`: «Workspace has exceeded its spend limit». Agotó su límite con el render en CPU. Ahí ya
  no corre ni CPU ni GPU.
- Cuenta `carlosfavela328-eng`: «Please add a payment method to use T4 GPU functions». Nunca tuvo tarjeta.

Aunque hubiera GPU: Wan 2.2 Animate son 14 mil millones de parámetros y no cabe en una T4 de 16 GB para video
útil; pediría A100 o H100. Y es un modelo de **animación de personajes** (una foto de persona repitiendo el
movimiento de un video), no sirve para cortes anatómicos.

**No hace falta Modal:** WaveSpeed ya hospeda `wavespeed-ai/wan-2.2/animate` (lista $0.20, hasta 120 s, 720p,
recibe video + imagen). Pendiente de autorización de Carlos por el riesgo de costo real.

## Sin probar todavía

- `wavespeed-ai/ltx-2-19b/control` · $0.20 · hasta 20 s, con guía por **profundidad o canny**. Es el que mejor
  encaja con el método de 3D primero, porque tomaría la geometría del render de Blender. Solo acepta 1 imagen de
  referencia.
- `wavespeed-ai/wan-2.2/fun-control` · $0.20 · hasta 120 s, 1 imagen de referencia.
- `wavespeed-ai/wan-2.1-14b-vace` · $0.30 · hasta 5 imágenes, pero tope de 10 s.

## Recomendación

Para **calidad**, MiniMax ya demostró que hace el trabajo de Genjutsu con 9 imágenes de referencia en lugar de 40.
Para **velocidad**, ninguno de los dos resuelve: falta probar `ltx-2-19b/control`, que además aprovecharía la
geometría del Blender.
