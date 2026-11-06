# 05: Calidad, faltantes y comparabilidad

## 1. Fuente y parámetros

| Dato | Valor |
|---|---|
| Fuente | Windsor.ai, conector `facebook` (Meta Ads Insights + objetos + historial de actividad). **Solo lectura**: no se creó, editó, duplicó, activó ni pausó nada |
| Fecha de extracción | 2026-09-16 |
| Cuenta | `684865860329838` («684865860329838, MXN») |
| Moneda | **MXN**, confirmada en `account_currency` |
| Zona horaria | **America/Tijuana**, confirmada en `account_timezone`. Las fechas y horas del historial de cambios también están en esa zona |
| Periodo solicitado | 2026-01-01 a 2026-09-16 |
| Periodo con entrega propia | **2026-03-25 a 2026-08-10**. No hubo entrega antes ni después |
| Historial anterior | Consulta del 2024-01-01 al 2025-12-31. Solo hubo entrega del 15 al 19 de julio de 2024 (ver §8) |
| Atribución de todas las métricas | `7d_click_1d_view`: opción `attribution_window=default` del conector, documentada como `["7d_click","1d_view"]` |
| Madurez de atribución | El último día con entrega (2026-08-10) quedó **37 días** antes de la extracción. La ventana de 7 días ya cerró para todas las filas y no hay periodos que puedan cambiar |
| Granularidad de `03` | Una fila por anuncio por día, agregada sobre todas las ubicaciones (`placement=mixed`) |

## 2. Filtro de propiedad

Por instrucción del anunciante se **quitaron de todos los archivos** los anuncios que no son de Visión Agencia:

- Anuncios de **otras páginas de Facebook**, que corresponden a clientes u otros negocios.
- Anuncios de la página de Visión Agencia que **promocionan a un cliente**: campañas «LEQ …» y «Amy vip campaña».

Se quitaron **15 anuncios con entrega, de 9 campañas (63 filas diarias)**, además de sus objetos sin entrega, cambios de segmentación y presupuesto, e imágenes. Los registros propios no se modificaron.

**Consecuencia para la solicitud.** Las dos referencias que pedía, `[8/6/2026]` (48 conversaciones, 210.65) y `[16/6/2026]` (14 conversaciones, 98.22), **no son campañas de Visión Agencia** y quedaron fuera. Las cifras sí se verificaron contra la API y coincidían al peso, pero no se usan. **La referencia correcta es el anuncio `120251563209080651`** (ver 01). El anunciante la confirmó con una captura de Ads Manager: 84 conversaciones, 11.51 por conversación, 966.63 de gasto.

**Supuesto a validar.** Las campañas «Sanaas - 1 Video Gratis …» se consideran **propias**: se publicaron desde la página de Visión Agencia y dirigen al WhatsApp del anunciante (`526312470486`). Si Sanaas fuera un cliente, hay que quitar 5 anuncios.

## 3. Mapeo de objetivo y evento

El objetivo se asigna combinando **objetivo de campaña + optimización del conjunto + destino**. Nada se asignó solo porque el anuncio haya registrado conversaciones.

| Objetivo de campaña | Optimización | Destino | `objective` | `result_type` | Campo contado |
|---|---|---|---|---|---|
| `MESSAGES` u `OUTCOME_ENGAGEMENT` | `CONVERSATIONS` | WhatsApp, Messenger o ambos | `messages` | `conversacion_iniciada` | `actions_onsite_conversion_messaging_conversation_started_7d` |
| `LINK_CLICKS` u `OUTCOME_TRAFFIC` | `CONVERSATIONS` | WhatsApp, Messenger o ambos | **`traffic`** | `conversacion_iniciada` | igual |
| `LEAD_GENERATION` | `LEAD_GENERATION` | formulario | `leads` | `lead` | `actions_lead` |
| `LINK_CLICKS` u `OUTCOME_TRAFFIC` | `LINK_CLICKS` | web / wa.me | `traffic` | `link_click` | `link_clicks` |
| `LINK_CLICKS` u `OUTCOME_TRAFFIC` | `LANDING_PAGE_VIEWS` | web | `traffic` | `landing_page_view` | `actions_landing_page_view` |
| `MESSAGES` | `POST_ENGAGEMENT` | WhatsApp | *(excluido)* | — | El evento optimizado no es la conversación |

- La campaña ganadora («Nuevo Tráfico Campaña») es de **tráfico optimizada a conversaciones**. Queda como `traffic` + `conversacion_iniciada`, **en un contexto distinto** a `messages`. Si Codex decide juntarlas, debe hacerlo explícitamente y documentarlo.
- `link_clicks` siempre es el campo de **clics de enlace**. No son todos los clics (`clicks`) ni clics únicos.
- El conector reporta el CTR (`ctr`) sobre **todos los clics**, por eso no se incluye. El CTR de enlace se calcula como `link_clicks / impressions`.
- `OUTCOME_ENGAGEMENT` con `CONVERSATIONS` se trata como `messages` porque es la ruta actual de Ads Manager para «Interacción → Apps de mensajería». Su evento optimizado es la conversación.

## 4. Audiencia (`audience`)

- Se construye **por día** a partir del **historial de cambios de segmentación** de cada conjunto (`extras/cambios_segmentacion_2026.csv`), no de la configuración actual. Así, cada fila refleja la segmentación vigente ese día.
- Incluye ubicación geográfica, edad, idioma, intereses, públicos personalizados o similares y los interruptores de Advantage+. **Excluye las ubicaciones de anuncio**, que van en `placement`.
- **Los días en que la segmentación cambió** mezclan dos configuraciones y **no entran en `03`**: 10 filas de 8 anuncios. Siguen completos en `02`.
- No se agruparon públicos distintos. Por eso muchos contextos tienen un solo anuncio (§6).

## 5. Ceros y ausencias

- Meta **omite** una acción cuando ocurrió 0 veces. Si el anuncio **tuvo impresiones** ese día y la acción no aparece, se escribió `0`: **70 valores**. La consulta con `use_unified_attribution_setting=true` devolvió esos mismos ceros de forma explícita.
- Los días **sin impresiones** no entran en `03`. En `02`, los campos ausentes se conservan como `null`.

## 6. Exclusiones y conteos

**Origen propio:** 161 filas diarias, **46 anuncios, 22 campañas**.
**`03_historial_simulador.csv`:** **119 filas, 43 anuncios, 19 campañas**, del 2026-03-25 al 2026-08-10.

| Motivo de exclusión en `03` | Filas | Anuncios |
|---|---:|---:|
| Sin entrega ese día (0 impresiones) | 28 | 11 |
| La segmentación cambió ese mismo día | 10 | 8 |
| `MESSAGES` optimizado a `POST_ENGAGEMENT` (campaña «[5/6/2026] Promoción de https://api.whatsapp.com/send») | 4 | 1 |

**Por objetivo y evento (`03`):**

| objective / result_type | Anuncios | Campañas | Gasto MXN | Resultados | Anuncios con gasto y **0** resultados |
|---|---:|---:|---:|---:|---:|
| messages / conversacion_iniciada | 11 | 11 | 2,065.74 | 37 | 5 |
| traffic / conversacion_iniciada | 3 | 2 | 1,387.90 | 93 | 0 |
| leads / lead | 11 | 2 | 217.40 | 15 | 3 |
| traffic / link_click | 12 | 3 | 200.02 | 381 | 4 |
| traffic / landing_page_view | 6 | 1 | 289.01 | 327 | 1 |

Los anuncios que fallaron **están incluidos**: 13 anuncios con gasto y ningún resultado.

**Contextos comparables completos** (cuenta, moneda, objetivo, evento, atribución, ubicación y audiencia). La lista completa está en `extras/resumen_construccion.json`.

| Contexto | Anuncios | Campañas |
|---|---:|---:|
| leads · México 18+ Advantage+ | 11 | 2 |
| traffic/link_click · México 25–60 | 10 | 1 |
| traffic/landing_page_view · México 25–55 | 6 | 1 |
| **messages · México 18+ Advantage+** | **3** | **3** |
| **traffic/conversacion_iniciada · México 18–65+** (ganadora y video) | **2** | **1** |
| messages · México 25–52, idioma Polaco, intereses de negocios | 2 | 2 |
| Otros 11 contextos de mensajes o tráfico | 1 c/u | 1 c/u |

### Reglas mínimas del motor

- **≥5 anuncios de otras campañas del mismo contexto, terminadas antes del inicio:** ninguna campaña de mensajes ni de tráfico con conversaciones lo cumple. El máximo es 2 anuncios previos, en «Campaña de Interacción» del 14/6. Para la ganadora es 0, porque no hay campañas previas con su mismo contexto.
- **Diferencias por texto (≥8 anuncios evaluados en ≥3 campañas del mismo contexto):** **no se cumple en ningún contexto de conversaciones**. El único con 3 campañas tiene 3 anuncios.
- Si se ignora la audiencia, `messages/conversacion_iniciada` tendría 11 anuncios en 11 campañas y `traffic/conversacion_iniciada` 3 en 2. Eso **mezcla públicos distintos**: México, Nogales 80 km con intereses, audiencia tibia, público similar. No se hizo.
- **No se fabricaron divisiones de campaña ni se agruparon públicos** para llegar a los mínimos.

## 7. Faltantes («no disponible»)

| Faltante | Alcance | Motivo |
|---|---|---|
| **Texto principal** | 24 de 46 anuncios, **incluido el ganador** | La API no devuelve `body` ni `body_asset_text`. En esos casos `idea` usa el texto **visible en la imagen**, transcrito de la pieza descargada |
| Descripción del anuncio | todos | Error `#100` de Meta al combinar `description_asset` |
| **Video original, transcripción y escenas** | 10 anuncios en video | La API no entrega el archivo. Solo hay miniatura; la `idea` lo indica con «[Video: descripción solo de la miniatura; sin transcripción]» |
| Ventana guardada en el conjunto (`attribution_spec`) | todos | El conector no la expone. Las métricas usan 7d_click_1d_view |
| Saludo, preguntas o plantilla de mensaje inicial | todos | El conector no lo trae. No se leyeron chats |
| Historial de cambios de ubicaciones y puja día a día | parcial | Solo lo que registra el log de actividad (todas las categorías del 1 al 25 de junio; BID, BUDGET y TARGETING del periodo completo) |
| Monto del límite de puja antes del 1/8 | — | No había límite; se puso el 1/8/2026 ($50.00) |
| Miembros de públicos | — | No se solicitaron |

## 8. Discrepancias y avisos

1. **CTR anterior.** El «5.83 %» que circulaba era el CTR de *todos los clics* de otra campaña. En `01` se usa el CTR de enlace.
2. **Idioma «Polaco» en 4 conjuntos propios.** El historial de Meta registra `Idioma: Polaco` (`locales: [15]`) en «[11/5/2026] Promoción de https://fb.com/messenger_doc/», su copia, «Marketing AI - WhatsApp Conversaciones - Mayo 2026» y «Retargeting — Cierre $500 — Vision Agencia». Entre las cuatro: **2 conversaciones con 443.46 de gasto**. Se conserva tal cual en `audience`. **Conviene confirmarlo en Ads Manager**: si es un error de configuración, esos resultados no representan al público mexicano. No se afirma que esa sea la causa del bajo desempeño.
3. **Creativo del ganador actualizado.** El 18/6 a las 00:43 cambió el `creative_id` sin cambiar la imagen. Sus filas no se partieron porque el mensaje visual es el mismo.
4. **Cuenta publicitaria desactivada por pago.** Aparece en la captura del anunciante. No afecta los datos históricos, pero impide publicar hasta pagar.
5. **Historial 2024** (`extras/historial_2024_diario.csv`). Dos campañas `MESSAGES` / `CONVERSATIONS` de Visión Agencia, del 15 al 19 de julio de 2024: **355.12 de gasto y 0 conversaciones reportadas**. Texto: «Te ayudamos a llevar tu negocio de la mejor forma a tus clientes!». Segmentaciones: México 18–65 y Nogales Centro. No entran en `03` porque sus imágenes no se descargaron ni describieron y su configuración es la actual, no la de entrega.

## 9. Contactos, compras e ingresos

- **Compras marcadas en el chat** (`onsite_conversion.purchase`, lo que se etiqueta como compra en Messenger o WhatsApp Business): **2 en toda la historia propia**, las dos con **valor 0**:
  - 2026-05-04, anuncio `120248293143300651` (Campaña de Interacción).
  - 2026-06-19, anuncio **`120251563209080651` (ganador)**.
  - Archivo: `extras/compras_marcadas_en_chat.csv`.
- **Leads de formulario:** 15 en `03` (campañas «Promoción continua de generación de clientes potenciales»).
- **Contactos calificados, ventas cerradas e ingresos:** **no disponibles** en la plataforma. `action_values_total = 0`. No se dedujeron ventas a partir de conversaciones.

## 10. Archivos

| Archivo | Contenido |
|---|---|
| `01_campana_ganadora.md` | Reconstrucción del anuncio ganador y su tabla diaria |
| `02_historial_original.json` | Todas las consultas originales (propias), con nombres de métricas y metadatos sin reinterpretar |
| `02_historial_original_diario.csv` | Métricas diarias por anuncio tal como vienen de la fuente |
| `03_historial_simulador.csv` | 119 filas normalizadas con el encabezado exacto del contrato |
| `04_creativos.csv` | 47 filas: una por variante de texto identificable de cada uno de los 46 anuncios, sin métricas |
| `05_calidad_y_faltantes.md` | Este documento |
| `creativos/` | Imágenes y miniaturas descargadas, nombradas `<ad_id>_<campo>.<ext>` |
| `extras/` | Ubicaciones y totales del ganador, cambios de presupuesto y segmentación, compras marcadas, historial 2024 |

Todos los archivos pesan menos de 8 MB y tienen menos de 5,000 filas, así que no hubo que dividir nada.
