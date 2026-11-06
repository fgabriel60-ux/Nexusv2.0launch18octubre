# Validación de la extracción de Meta Ads para Andromeda Lab

Encargo: `PARA_CLAUDE_METRICAS_ANDROMEDA.md` (Astra). Extracción hecha por Claude el **16 sep 2026**.
Solo lectura: no se creó, modificó ni pausó nada en la cuenta, y no se tocó el motor del simulador.

## 1. Configuración y definiciones confirmadas

| Dato | Valor confirmado | Cómo se obtuvo |
|---|---|---|
| Cuenta | `684865860329838` | `get_connectors`: es la única con cuentas conectadas |
| Moneda | **MXN** | campo `account_currency`; el nombre de la cuenta es «684865860329838, MXN» |
| Zona horaria | **America/Tijuana** (UTC−7) | `account_timezone`, `account_timezone_offset_hours_utc` |
| Atribución | **7d_click + 1d_view** | opción `attribution_window` del conector; su valor `default` es `["7d_click","1d_view"]`. Se usó el default, no se forzó otra ventana |
| Evento de resultado (mensajes) | `actions_onsite_conversion_messaging_conversation_started_7d` = «Messaging conversation started» | mismo campo de la referencia anterior, conservado |
| Fecha de extracción | 2026-09-16 | — |
| Rango pedido | 2026-04-01 a 2026-09-15 | — |
| Rango con datos | **2026-04-14 a 2026-08-11** | la cuenta no tiene entrega fuera de eso |
| Granularidad | una fila por anuncio por día, agregada sobre ubicaciones | no se pidió desglose por ubicación, por eso `placement = mixed` |

**Sobre el sufijo `7d`:** Astra tenía razón en no inferir la ventana del nombre. El nombre del campo dice `7d` pero la
ventana real de la consulta la fija la opción `attribution_window` del conector, que quedó en `default` = 7 días de
clic + 1 día de visualización. La etiqueta estable usada en el CSV es `default_7d_click_1d_view`.

**Clics:** se distinguen tres campos y NO son lo mismo.

- `clicks` = todos los clics (incluye reacciones, expandir texto, etc.).
- `link_clicks` = clics de enlace. **Es el que exige el contrato** y el que va en el CSV.
- `outbound_clicks_outbound_click` = clics que salen de Facebook. Viene nulo en 122 de 216 filas.

En la referencia del 8 al 11 de junio: **454 clics totales contra 160 clics de enlace**. Usar los totales habría
inflado el embudo casi 3×.

**CTR:** el campo `ctr` del conector es CTR de todos los clics. No se incluyó en el CSV para no mezclar
definiciones; si se quiere CTR de enlace se calcula con `link_clicks / impressions` en el simulador.

## 2. Consultas hechas

1. **Métricas diarias por anuncio** — 216 filas, 56 anuncios, 29 campañas, 2026-04-14 a 2026-08-11.
   Campos: `date, ad_id, ad_name, adset_id, adset_name, campaign_id, campaign, objective, adsset_optimization_goal,
   spend, impressions, reach, frequency, clicks, link_clicks, outbound_clicks_outbound_click, actions_link_click,
   actions_lead, actions_onsite_conversion_messaging_conversation_started_7d`.
2. **Catálogo de creativos** — 56 filas, una por anuncio, sin duplicar por día.
   Campos: `ad_id, ad_name, campaign_id, campaign, adset_id, adset_name, creative_id, object_type, body, title,
   call_to_action_type, image_url, thumbnail_url, ad_preview_shareable_link, facebook_permalink_url,
   instagram_permalink_url, status, effective_status, ad_created_time, campaign_objective, adsset_optimization_goal`.

Sin paginación: cada consulta cupo en una sola respuesta. No se dividieron rangos, así que no hay días duplicados.

**Dos consultas fallaron y se reintentaron:**
- Mezclar `description_asset_text` y `video_asset_video_id` con campos de acciones da error de Meta
  `(#100) Current combination of data breakdown columns (action_type, description_asset, video_asset) is invalid`.
  Por eso **no hay texto de descripción ni ID de video** en el catálogo.
- Supermetrics no se usó: Facebook Ads aparece `NOT_AUTHENTICATED` y el trial de esa cuenta venció.

## 3. Mapeo al contrato del simulador

| Campo del simulador | De dónde sale |
|---|---|
| `ad_id`, `campaign_id` | `ad_id`, `campaign_id` reales, como texto |
| `date_start`, `date_end` | `date` (grano diario: inicio = fin) |
| `idea` | texto literal del creativo + título + CTA + formato |
| `account_id`, `currency` | `684865860329838`, `MXN` |
| `objective` | mapeo estricto, ver abajo |
| `result_type` | `conversacion_iniciada`, `lead` o `link_click` según el objetivo mapeado |
| `attribution` | `default_7d_click_1d_view` |
| `placement` | `mixed` (las ubicaciones vienen realmente agregadas) |
| `audience` | **nombre del conjunto de anuncios**, no su ID |
| `spend`, `impressions`, `link_clicks`, `results` | conteos de la fuente, sin derivar |
| `revenue` | ausente: no hay datos de ingresos en la plataforma |

**El objetivo NO se tradujo a ciegas.** Solo se mapea cuando el objetivo de campaña y el evento de optimización
del conjunto concuerdan:

| Objetivo de campaña | Optimización exigida | Objetivo del simulador | Evento contado |
|---|---|---|---|
| `MESSAGES` | `CONVERSATIONS` | `messages` | conversaciones iniciadas |
| `LEAD_GENERATION` | `LEAD_GENERATION` | `leads` | `actions_lead` |
| `LINK_CLICKS` | `LINK_CLICKS` o `LANDING_PAGE_VIEWS` | `traffic` | `link_clicks` |

Todo lo demás queda fuera del CSV, conservado en el enriquecido con su valor original. En esta cuenta hay casos
reales de desajuste: campañas `MESSAGES` optimizadas a `POST_ENGAGEMENT` y campañas `LINK_CLICKS` optimizadas a
`CONVERSATIONS`. Traducirlas habría mezclado eventos distintos.

**Criterio de audiencia:** se usó el **nombre** del conjunto de anuncios como etiqueta, no su ID, como pedía el
encargo. Consecuencia honesta: en esta cuenta cada campaña de mensajes tuvo su propio conjunto con nombre distinto,
así que **cada una queda como un contexto separado de un solo anuncio**. No se agruparon mercados distintos.

## 4. Filas excluidas del CSV y por qué

De 216 filas diarias extraídas, **56 entraron** al CSV de modelado y 160 se excluyeron:

| Motivo | Filas | Anuncios |
|---|---:|---:|
| Sin texto del creativo: no se puede describir la `idea` sin inventarla | 67 | 24 |
| Objetivo `LINK_CLICKS` optimizado a `CONVERSATIONS`: evento incierto | 43 | 4 |
| Objetivo `OUTCOME_ENGAGEMENT`: no se mapea a ninguno de los cuatro válidos | 40 | 9 |
| Objetivo `MESSAGES` optimizado a `POST_ENGAGEMENT`: evento incierto | 4 | 1 |
| Sin entrega ese día (0 impresiones) | 6 | 3 |

Solo **25 de 56 anuncios traen texto** en el campo `body`. Los 31 restantes son en su mayoría publicaciones
compartidas (`object_type = SHARE`), donde el texto vive en el post original y el conector no lo devuelve. No se
dedujo el contenido a partir de que la campaña funcionara bien.

**Ceros explícitos:** en 31 casos Meta omitió la acción en un día en que el anuncio **sí tuvo impresiones**. Ahí se
escribió `0`, que es como Meta representa «cero ocurrencias». Nunca se rellenó un dato desconocido: las filas sin
entrega se excluyeron y los campos ausentes en el enriquecido quedaron en `null`.

## 5. Reconciliación con el informe anterior

Campaña de referencia `[8/6/2026] Promoción de https://api.whatsapp.com/send`, del 8 al 11 de junio:

| Métrica | Informe anterior | Esta extracción | Coincide |
|---|---:|---:|:--:|
| Gasto | 210.65 | 210.65 | ✅ |
| Impresiones | 7,786 | 7,786 | ✅ |
| Conversaciones | 48 | 48 | ✅ |
| Conversaciones por día | 1, 29, 10, 8 | 1, 29, 10, 8 | ✅ |

Coincide al peso y al conteo, sin ajustar nada. **Dato nuevo:** esa campaña fue **un solo anuncio**, el
`120250891895420651`, con 160 clics de enlace (no 454, que son los clics totales) y moneda MXN confirmada.

## 6. Cobertura efectiva y límite para modelar

El CSV trae **56 filas, 18 anuncios, 8 campañas, del 2026-04-14 al 2026-07-17**. Pasó la validación del motor:
`parse_history` devuelve `{"filas_validas": 56, "duplicados_exactos": 0}`, sin periodos solapados.

Contextos (objetivo + evento + audiencia) y anuncios distintos en cada uno:

| Objetivo | Audiencia | Anuncios | Filas | Gasto MXN | Resultados |
|---|---|---:|---:|---:|---:|
| leads | Promoción continua de generación de clientes potenciales | **8** | 15 | 121.25 | 9 |
| traffic | México 35-64 - Tráfico Enlace IMSS | **5** | 24 | 325.69 | 209 |
| messages | [14/4/2026] Promoción de facebook.com/6155… | 1 | 4 | 281.43 | 9 |
| messages | [11/5/2026] Promoción de fb.com/messenger_doc | 1 | 5 | 271.11 | 2 |
| messages | [8/6/2026] Promoción de api.whatsapp.com/send | 1 | 4 | 210.65 | 48 |
| messages | [16/6/2026] Promoción de api.whatsapp.com/send | 1 | 3 | 98.22 | 14 |
| traffic | Advantage+ - Todo Mexico | 1 | 1 | 11.71 | 39 |

**Límite importante:** el motor exige al menos 3 anuncios comparables por contexto. Con estos datos solo lo cumplen
`leads` (8 anuncios) y `traffic` IMSS (5). **El objetivo `messages`, que es el caso de negocio de Carlos, tiene un
solo anuncio por contexto y hoy no se puede simular.**

Hay una salida posible, pero es decisión de Astra y no se tomó aquí: agrupar la audiencia de forma más gruesa, por
ejemplo todas las campañas de mensajes a WhatsApp como un mismo contexto. Eso daría 4 anuncios de mensajes, pero
mezclaría públicos que el anunciante definió por separado. Requiere criterio documentado, no conviene hacerlo en
silencio.

## 7. Lo que sigue faltando

1. **Texto de 31 anuncios** (`object_type = SHARE`): el conector no devuelve el cuerpo del post original. Haría
   falta leerlo desde la publicación o desde la API de creativos.
2. **Descripción visual de las piezas.** Solo hay URLs de imagen y miniatura; nadie describió lo que se ve. El
   campo `idea` lleva el texto literal, no una descripción de la escena.
3. **Descripción del creativo y ID de video**: bloqueados por el error `(#100)` de combinación de campos.
4. **Ingresos y ventas**: no existen en la plataforma. Las «dos ventas» que menciona Carlos no se pueden comprobar
   con estos datos y no se calculó ROAS.
5. **Madurez de atribución**: no se marcó ninguna fila como inmadura porque el último día con datos es 2026-08-11,
   más de un mes antes de la extracción; la ventana de 7 días ya cerró para todas.

## 8. Archivos

| Archivo | Qué es |
|---|---|
| `facebook_ads_raw.json` | las dos consultas tal cual, con su configuración. Sin tokens |
| `facebook_ads_enriched.json` | 216 filas diarias + creativo unido por `ad_id`, conservando ausencias |
| `facebook_ads_normalizado.csv` | 56 filas listas para el contrato, sin campos inventados |
| `creativos.json` | catálogo de los 56 anuncios con texto, CTA, formato y enlaces |
| `resumen_construccion.json` | conteos y motivos de exclusión que generó el script |
| `construir_entregables.py` | el script que arma todo, reproducible |
