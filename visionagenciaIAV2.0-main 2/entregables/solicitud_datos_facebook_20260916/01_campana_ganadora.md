# 01 — Reconstrucción de la campaña ganadora

Cuenta `684865860329838`, que en Meta se llama «684865860329838, MXN». Moneda: **MXN**. Zona horaria: **America/Tijuana** (UTC−7 en verano).
Fuente: Windsor.ai (conector `facebook`, solo lectura). Datos extraídos el 16 sep 2026.
Ventana de atribución: la opción `default` del conector, **7 días desde el clic + 1 día desde la visualización**. Evento contado: `actions_onsite_conversion_messaging_conversation_started_7d`, «Conversaciones con mensajes iniciadas».

> **Alcance.** Por instrucción del anunciante solo se incluyen anuncios **propios de Visión Agencia**, es decir, publicados desde la página `112035195330595` y que no promocionan a un cliente. La referencia de la solicitud («[8/6/2026] … 48 conversaciones, 210.65») resultó ser de un negocio ajeno y **se quitó** de toda la entrega (ver 05).
> La campaña ganadora propia la confirmó el anunciante con una captura de Ads Manager: **84 conversaciones · $11.51 por conversación · $966.63 gastados · 3,610 de alcance · 6,904 impresiones**. Los mismos números salen de la API.

---

## 1. Identificadores y estado

| Nivel | ID | Nombre | Creado | Estado actual |
|---|---|---|---|---|
| Campaña | `120251563208660651` | Nuevo Tráfico Campaña | 2026-06-17 18:58 | PAUSED |
| Conjunto | `120251563208930651` | Nuevo Tráfico Conjunto de anuncios | 2026-06-17 18:58 | — |
| **Anuncio ganador** | **`120251563209080651`** | Nuevo Tráfico Anuncio | 2026-06-17 18:58 | PAUSED |
| Segundo anuncio del conjunto | `120252656552890651` | Nuevo Tráfico Anuncio - Copia (video) | 2026-07-07 14:18 | CAMPAIGN_PAUSED |

- Página: `112035195330595` (Visión Agencia).
- Entrega del anuncio ganador: del 17/6 al 5/7/2026. Del 6/7 al 9/7 tuvo 0 impresiones. No tiene fecha de fin programada.
- Creativo actual: `1643517286946680`, formato `SHARE`. El 18/6 a las 00:43 se actualizó el creativo con la misma imagen; el ID anterior era `2116206429243223`. No se sabe qué cambió además del ID.
- Captura del anunciante: el anuncio aparece «Desactivado · Tráfico» y la cuenta muestra **«Cuenta publicitaria desactivada. No pudimos procesar el pago»**. Hay que resolverlo antes de publicar cualquier campaña nueva.

## 2. Anuncio

| Campo | Valor |
|---|---|
| Texto principal | **no disponible**: la API no devuelve `body` ni `body_asset_text` para este anuncio. El mensaje está escrito dentro de la imagen |
| Título | Chatea en Messenger |
| Descripción | **no disponible**: Meta responde con el error `#100` al pedir `description_asset` |
| CTA | `MESSAGE_PAGE` |
| Destino | Apps de mensajería, Messenger y WhatsApp (`MESSAGING_MESSENGER_WHATSAPP`). URL registrada: `https://fb.me/messenger_doc/` |
| Imagen original | `creativos/120251563209080651_image.jpg` |
| Vista previa | https://fb.me/29YUxK9KSGYNYSm |
| Publicación | https://facebook.com/p/112035195330595_122317360082032009 · https://www.instagram.com/p/DZuCLsTDCCe/ |

**La imagen, descrita a partir del archivo descargado.** Pieza cuadrada en negro y naranja. Titular: «**TU MARCA MERECE VENDER.** Nosotros creamos la campaña. Tú recibes los clientes.» Debajo hay tres tarjetas:
1. «**Por solo $500 al mes**», con la etiqueta «sin letras pequeñas».
2. Un cronómetro con «**En solo 4 horas**: tienes tu campaña corriendo».
3. Un ícono de play con «**Video gratis de muestra**: creamos un video profesional de tu marca para que veas resultados antes de empezar».

En la franja inferior hay cuatro íconos: estrategia a medida, anuncios que convierten, más ventas y clientes, atención por WhatsApp.

**Oferta concreta.** La agencia arma la campaña de publicidad por **$500 al mes** y la deja corriendo **en 4 horas**. Antes de contratar, el cliente recibe **un video de muestra gratis**. Va dirigida a dueños de marcas o negocios que quieren vender más. La pieza no menciona ciudad ni giro.

## 3. Objetivo, optimización y puja

| Campo | Durante la entrega (17/6–9/7) | Configuración actual |
|---|---|---|
| Objetivo de campaña | `LINK_CLICKS` (Tráfico) | igual |
| Objetivo de rendimiento | `CONVERSATIONS` (en el historial aparece como «Respuestas») | igual |
| App de mensajería | Messenger y WhatsApp | igual |
| Evento de cobro | `IMPRESSIONS` | igual |
| Estrategia de puja | Menor costo **sin límite** (`LOWEST_COST_BID_STRATEGY`) desde que se creó | **Límite de puja de $50.00**, puesto el 1/8/2026 a las 21:27. Fue después de la entrega del ganador |
| Compra | `AUCTION` | igual |

**Ojo con el objetivo.** La campaña es de **Tráfico**, pero está optimizada para conversaciones. En `03_historial_simulador.csv` queda como `objective=traffic` y `result_type=conversacion_iniciada`. No se convirtió a `messages`.

## 4. Presupuesto

El presupuesto es **diario y a nivel campaña** (CBO). Meta registra los importes en centavos.

| Fecha y hora (Tijuana) | Presupuesto diario |
|---|---|
| 17/6 18:58 (creación) | $50.00 |
| 21/6 00:09 | $50 → **$70** |
| 29/6 23:24 | $70 → **$50** |
| 4/7 11:15 | $50 → **$75** |
| 7/7 13:49 | $75 → **$161** |
| 10/7 20:03 | $161 → **$50** |
| 1/8 21:27 | $50 → $50 (se guardó sin cambio, a la misma hora que se puso el límite de puja) |

Hoy está en $50.00 al día. A partir del 7/7 (14:18) el presupuesto se reparte también con el video del mismo conjunto.

## 5. Segmentación

| Periodo | Ubicación | Edad | Público | Días en `03` |
|---|---|---|---|---|
| **17/6 18:58 → 8/7 17:46** | **México, todo el país** | 18–65+ | Sin públicos personalizados, intereses ni exclusiones registrados | Sí. **Cubre toda la entrega del anuncio ganador** |
| 8/7 17:46 → 9/7 09:14 | México: Sonora | 25–55 | Segmentación detallada Advantage+ activada · Público Advantage+ desactivado | No, el día mezcla dos configuraciones |
| 9/7 09:14 → actual | México | 25–55 | Segmentación detallada Advantage+ activada · Público Advantage+ desactivado | Solo el video: 10/7 en adelante |

- **Ubicaciones:** automáticas. Incluyen Facebook (feed, columna derecha, instream, marketplace, stories, búsqueda, «Explorar negocios», reels, overlay, perfil, notificaciones), Instagram (feed, stories, perfil, explorar, reels, búsqueda), Audience Network, Messenger Stories y Estado de WhatsApp.
- Tipos de ubicación: `home` y `recent`. Género: todos.
- No se consultaron miembros de ningún público.

**Dónde se entregó** (`extras/ubicaciones_anuncio_ganador.csv`, periodo completo):

| Ubicación | Gasto | Impresiones | Clics de enlace | Conversaciones |
|---|---:|---:|---:|---:|
| Facebook feed | 746.68 | 5,652 | 122 | 62 |
| Instagram reels | 43.04 | 173 | 12 | 9 |
| Facebook reels | 93.98 | 590 | 9 | 6 |
| Instagram feed | 46.80 | 218 | 5 | 3 |
| Instagram stories | 22.82 | 114 | 3 | 2 |
| Facebook stories | 7.57 | 52 | 4 | 1 |
| Facebook instream | 1.33 | 25 | 1 | 1 |
| Otras 5 ubicaciones | 4.40 | 80 | 1 | 0 |
| **Total** | **966.63** | **6,904** | **157** | **84** |

Estos importes son un **desglose aparte** y no deben sumarse a las filas por día. El 74 % de las conversaciones salió del feed de Facebook, pero eso muestra dónde repartió Meta el gasto, no demuestra que esa ubicación sea mejor.

## 6. Atribución y mensaje inicial

- **Ventana de las métricas:** 7 días desde el clic + 1 día desde la visualización. Al repetir la consulta con `use_unified_attribution_setting=true` (la configuración de cada conjunto), las conversaciones diarias de este anuncio salieron idénticas: 0, 5, 2, 5, 6, 10, 6, 6, 7, 9, 1, 2, 8, 5, 6, 2, 4. El total de 84 también coincide con la captura de Ads Manager.
- **Ventana guardada en el conjunto (`attribution_spec`):** **no disponible** en el conector.
- **Saludo, preguntas frecuentes o plantilla de Messenger/WhatsApp:** **no disponible**. El conector no trae esa configuración y no se abrieron chats.
- **Primera respuesta** (`messaging_first_reply`): 83 de 84 conversaciones.

## 7. Resultados diarios — anuncio `120251563209080651`

| Fecha | Gasto | Impresiones | Alcance | Frecuencia | Clics de enlace | Conversaciones | Costo por conversación |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-06-17 | 2.22 | 24 | 24 | 1.00 | 0 | 0 | — |
| 2026-06-18 | 68.10 | 464 | 408 | 1.14 | 6 | 5 | 13.62 |
| 2026-06-19 | 35.81 | 136 | 124 | 1.10 | 4 | 2 | 17.91 |
| 2026-06-20 | 51.27 | 335 | 299 | 1.12 | 9 | 5 | 10.25 |
| 2026-06-21 | 99.41 | 483 | 420 | 1.15 | 15 | 6 | 16.57 |
| 2026-06-22 | 91.71 | 589 | 481 | 1.22 | 17 | 10 | 9.17 |
| 2026-06-23 | 85.20 | 691 | 579 | 1.19 | 13 | 6 | 14.20 |
| 2026-06-24 | 67.14 | 637 | 537 | 1.19 | 16 | 6 | 11.19 |
| 2026-06-25 | 63.76 | 331 | 291 | 1.14 | 11 | 7 | 9.11 |
| 2026-06-26 | 49.02 | 467 | 379 | 1.23 | 12 | 9 | 5.45 |
| 2026-06-27 | 34.31 | 408 | 366 | 1.11 | 2 | 1 | 34.31 |
| 2026-06-28 y 29 | 0.00 | 0 | 0 | — | — | — | — |
| 2026-06-30 | 23.74 | 184 | 165 | 1.12 | 1 | 2 | 11.87 |
| 2026-07-01 | 60.89 | 460 | 365 | 1.26 | 17 | 8 | 7.61 |
| 2026-07-02 | 64.99 | 362 | 298 | 1.21 | 8 | 5 | 13.00 |
| 2026-07-03 | 54.99 | 525 | 430 | 1.22 | 10 | 6 | 9.17 |
| 2026-07-04 | 56.63 | 425 | 365 | 1.16 | 10 | 2 | 28.32 |
| 2026-07-05 | 57.44 | 383 | 330 | 1.16 | 6 | 4 | 14.36 |
| 2026-07-06 al 09 | 0.00 | 0 | 0 | — | — | — | — |
| **Total** | **966.63** | **6,904** | **3,610** | **1.91** | **157** | **84** | **11.51** |

Cómo se calcularon los totales:
- **Costo por conversación:** gasto total entre conversaciones totales, 966.63 / 84 = **11.51**. No se promediaron los costos diarios.
- **Alcance y frecuencia:** vienen de una consulta del periodo completo. El alcance diario no se puede sumar.
- **CTR de enlace:** clics de enlace entre impresiones, 157 / 6,904 = **2.27 %**. El CTR de *todos* los clics es 209 / 6,904 = 3.03 %.
- **CPM:** 966.63 / 6,904 × 1000 = **140.01**.
- **Promedio diario:** 84 conversaciones en 17 días con entrega = **4.9 conversaciones al día**.

## 8. El otro anuncio del conjunto: video «4 videos solo 500 al mes»

Anuncio `120252656552890651`, en formato VIDEO. Está en el mismo conjunto y comparte presupuesto, puja y segmentación con el ganador.

- **Miniatura:** una mujer joven de traje negro caminando por la calle. Texto sobre la imagen: «Lo mejor es que sea tu mejor versión sin grabarte, 4 videos solo 500 al mes».
- **Texto principal:** no disponible.
- **Transcripción y escenas:** **no disponibles**. La API no entrega el archivo de video, solo la miniatura. No se describe nada que no se haya visto.
- **CTA:** `MESSAGE_PAGE`.
- Vista previa: https://fb.me/1V2T5XWKSIhbovX · https://www.instagram.com/p/DagaiuiMiU_/

| Periodo | Gasto | Impresiones | Alcance | Clics de enlace | Conversaciones | Costo por conversación |
|---|---:|---:|---:|---:|---:|---:|
| 7/7 al 1/8/2026 | 615.92 | 6,646 | 4,468 | 37 | 20 | **30.80** |

Arrancó con segmentación nacional de 18–65+ y el 8 y 9 de julio le cambiaron la segmentación. Solo el 7/7 y los días del 10/7 en adelante entran en `03`.

## 9. Anuncios propios comparables, para contexto

Todos son de Visión Agencia y están ordenados por conversaciones. Cada costo se calcula como gasto total entre conversaciones.

| Anuncio | Campaña (objetivo / optimización) | Pieza | Gasto | Conversaciones | Costo |
|---|---|---|---:|---:|---:|
| **`120251563209080651`** | Nuevo Tráfico Campaña (LINK_CLICKS / CONVERSATIONS) | «Tu marca merece vender — $500 · 4 horas · video gratis» | 966.63 | **84** | **11.51** |
| `120248293143300651` | Campaña de Interacción (OUTCOME_ENGAGEMENT / CONVERSATIONS) | «VISION Agencia IA… $500 al mes» | 1,189.38 | 22 | 54.06 |
| `120252656552890651` | Nuevo Tráfico Campaña | video «4 videos solo 500 al mes» | 615.92 | 20 | 30.80 |
| `120247020986250651` | [14/4/2026] (MESSAGES / CONVERSATIONS) | flyer «Hoy solo $500 al mes · 3 imágenes y un video gratis» | 281.43 | 10 | 28.14 |
| `120251557968510651` | Sanaas… Audiencia Tibia MENSAJES - Copia 2 (OUTCOME_ENGAGEMENT / CONVERSATIONS) | **misma pieza «Tu marca merece vender»** | 128.51 | 6 | 21.42 |
| `120251287630570651` | Sanaas - 1 Video Gratis - Trafico URL wa.me (OUTCOME_TRAFFIC / LINK_CLICKS) | «Los virales no se inventan. Se replican — 1 video gratis» | 93.49 | 2 | 46.74 |

**Las campañas «Sanaas - 1 Video Gratis» de tráfico.** Son las de CPM más bajo de la cuenta: 3.93, 3.09 y 12.88. **No ganaron en conversaciones**: 4 conversaciones con $142.67 entre las tres. Estaban optimizadas para clics de enlace y en `03` se quedan como `traffic/link_click`.

## 10. Lo que está comprobado y lo que no

**Comprobado:**
- El anuncio ganador trajo 84 conversaciones a $11.51 en 17 días de entrega, con segmentación nacional de 18–65+, ubicaciones automáticas, sin límite de puja y con presupuesto de entre $50 y $75 al día.
- La **misma imagen** en otra campaña, «Sanaas… Copia 2», con otro objetivo y un público de audiencia tibia, dio 6 conversaciones a $21.42.
- El video del mismo conjunto, con la oferta «4 videos por $500», dio 20 conversaciones a $30.80.

**No se puede afirmar con estos datos:**
- Que la oferta «$500 · 4 horas · video gratis» *causó* el resultado. Hay una sola campaña con este desempeño y las comparaciones cambian a la vez el objetivo, el público, las fechas y el presupuesto.
- Que las 84 conversaciones se convirtieron en clientes o ventas. La cuenta no registra compras ni ingresos (ver 05).
