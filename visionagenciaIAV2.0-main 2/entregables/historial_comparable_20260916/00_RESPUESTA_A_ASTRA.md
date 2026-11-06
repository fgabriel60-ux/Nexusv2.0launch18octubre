# Respuesta a `propuesta_agencia_20260916/ENCARGO_PARA_CLAUDE.md`

Claude, 16 sep 2026. Solo hubo consulta y exportación: no se publicó, editó ni activó nada. No se modificó la entrega anterior (`solicitud_datos_facebook_20260916/`). No se incluyen tokens, teléfonos, nombres de prospectos ni datos de clientes.

## Resumen

| Pregunta | Respuesta |
|---|---|
| ¿Existe un tercer anuncio propio comparable? | **No. El historial de este contexto está agotado.** |
| ¿Hay etiquetas de público equivalentes que se puedan unir? | **No.** Todas las diferencias entre etiquetas son de configuración real |
| Texto principal del ganador | **Vacío.** Se publicó sin texto (hay evidencia). Además se recuperaron el saludo y los botones del mensaje inicial |
| Video comparable | Descargado. **No tiene voz**; se describieron las escenas por segundo |
| ¿Sanaas es de la agencia? | **Hay indicios fuertes, pero no prueba.** Sus filas quedan aparte como pendientes |

---

## 1. Búsqueda del tercer anuncio comparable

Contexto buscado (`entrada_motor.json`): `684865860329838 · MXN · traffic · conversacion_iniciada · 7d_click_1d_view · mixed · "Edad=18 - 65+; Lugar=México"`.

**Qué se revisó:**
- La cuenta: Windsor solo tiene conectada `684865860329838`, y no hay otras cuentas publicitarias.
- **Periodos:** de 2024-01-01 a 2026-09-16. En 2024 solo hubo dos campañas `MESSAGES` y en 2025 no hubo entrega.
- **Estados:** activos, pausados, archivados y objetos sin entrega (`include_objects_without_insights`).
- **Anuncios propios `traffic/conversacion_iniciada` en todo el historial:** solo hay **3**.

| Anuncio | Campaña | ¿Tiene días en el contexto exacto? | Evidencia |
|---|---|---|---|
| `120251563209080651` (ganador) | `120251563208660651` | Sí: 17 días, 17/6–5/7 | Segmentación México 18–65+ desde la creación hasta el 8/7 17:46 |
| `120252656552890651` (video) | `120251563208660651`, la **misma campaña** | Sí: solo el 7/7 | 8/7 17:46 → Sonora 25–55; 9/7 09:14 → México 25–55 |
| `120251572155030651` («Te ayudamos a llevar tu negocio…», imprenta) | `120251572152380651` | **No** | Nació el 17/6 21:24 con México 18–65+. El 17/6 22:01 pasó a Nogales +25 mi (MX y AZ). Por horas, **toda su entrega del 17/6 fue a las 22:00 y 23:00**: 10 impresiones y 0.37 MXN. La hora 22 incluye el cambio, así que no hay un día completo con la configuración original |

**Días que se revisaron por hora porque tuvieron cambio de segmentación** (`_fuente/q12_horas_dias_con_cambio.json`):

- **Video, 8/7:** 124.45 MXN, 1,304 impresiones y 5 conversaciones antes de las 17:00; la hora 17, que contiene el cambio, trae 4.16 MXN; después, 5.59 MXN. **El día está mezclado.** Aunque se aceptara, seguiría siendo el mismo anuncio: no suma un ID nuevo.
- **Video, 9/7:** empieza con Sonora 25–55 y a las 09:14 cambia a México 25–55. No es el contexto buscado.

**Resultado: no hay un tercer `ad_id` real** con gasto e impresiones en `traffic · conversacion_iniciada · Edad=18 - 65+; Lugar=México`. Tampoco se crearon IDs a partir de días, variantes o anuncios de clientes.

- Hay otro anuncio con el mismo objetivo y fechas, pero **es de un cliente** y queda excluido por instrucción de Carlos.
- **Anuncios con cero conversaciones en el contexto:** ninguno de los dos tiene 0 en el total. El video tiene días en 0 dentro del CSV: 14/7 y 15/7, pero pertenecen al contexto de 25–55.

**Suficiencia:**
- **Escenarios básicos (≥3 anuncios):** no se alcanza; hay 2 anuncios de 1 campaña.
- **Comparación por texto (≥5 anuncios previos, ≥8 evaluados, ≥3 campañas):** no se alcanza. **No existen campañas terminadas antes del 17/6 en este contexto.**
- Para destrabarlo hace falta **publicar campañas nuevas**, y eso lo tiene que decidir Carlos: presupuesto y publicación.

## 2. Auditoría de etiquetas de público

Método (`04_equivalencias_contexto.md`): se desarmó cada etiqueta de `audience` en sus componentes (lugar, edad, idioma, intereses, públicos, Advantage+). Las listas se ordenaron y se compararon todos los pares con el mismo `objective` y `result_type`.

- **Diferencias solo de formato u orden:** **0.** No hay dos etiquetas distintas que describan la misma configuración.
- **Pares que difieren en un solo componente**, todos con diferencia real:
  - `messages`: «México 18+ Advantage+» contra lo mismo más un **público similar 2 %** → público distinto.
  - `traffic/conversacion_iniciada`: «México 18–65+» contra **Nogales +25 mi MX y AZ** → ubicación distinta.
  - `traffic/link_click`: edad **18–65+** contra **25–60** → edad distinta.
- **Caso dudoso, sin resolver:** la ausencia de la línea «Público Advantage+» contra «Público Advantage+: Desactivado». En el conjunto `120251572153320651`, que nunca volvió a cambiar, la línea falta en el registro y `targeting_automation` también falta en el JSON actual. En los conjuntos donde aparece «Desactivado», el JSON tiene `advantage_audience: 0`. **No se pudo demostrar** que «ausente» y «0» sean la misma configuración para Meta. Además, ese par no afecta al contexto del ganador: los únicos con esa diferencia tienen `result_type` distinto.

**Mapeo canónico propuesto: ninguno.** Se mantiene la separación actual.

## 3. Texto principal, título y mensaje inicial del ganador

| Elemento | Resultado | Evidencia |
|---|---|---|
| **Texto principal (post)** | **Vacío: se publicó sin texto** | `effective_instagram_media__caption = ""` en el post `DZuCLsTDCCe` de @visionagencia595. En la página pública de Instagram, `og:description` = «2 likes, 0 comments - visionagencia595 on June 18, 2026», sin el texto que Instagram muestra cuando existe. En la publicación de Facebook, `og:description` = «Chatea en Messenger», que es solo el título. La API tampoco devuelve `body` ni `body_asset_text`. La vista previa `fb.me` pide iniciar sesión |
| **Texto en la imagen** | «TU MARCA MERECE VENDER. Nosotros creamos la campaña. Tú recibes los clientes.» · «Por solo $500 al mes — sin letras pequeñas» · «En solo 4 horas tienes tu campaña corriendo» · «Video gratis de muestra: creamos un video profesional de tu marca para que veas resultados antes de empezar» | Imagen original y versión de Instagram en `creativos/` |
| **Título** | «Chatea en Messenger» | Campo `title`, `ctwaContext.title` en los 35 chats y `og:description` de Facebook |
| **Mensaje inicial (WhatsApp)** | Saludo: **«¡Hola! ¿Cómo podemos ayudarte?»** Respuestas sugeridas que tocaron los prospectos: **«Quiero más información sobre el negocio.»** (19) y **«Quiero más información sobre el anuncio.»** (12). En 4 chats el primer mensaje fue otro texto, que no se revisó | `ctwaContext.greetingMessageBody` en los 35 chats con `sourceId = 120251563209080651`, más el conteo de primeros mensajes idénticos. Solo se registran textos repetidos 3 veces o más, que corresponden a botones automáticos |
| Origen de los chats | Facebook 28, Instagram 7 | `ctwaContext.sourceApp` |

**Mensaje inicial en Messenger:** no disponible. No se consultó la bandeja de Messenger.

**Actualización en `03`.** La `idea` del ganador ahora marca el texto principal como vacío y agrega el mensaje inicial. No cambió ninguna métrica.

## 4. Video comparable `120252656552890651`

- **Archivo:** `creativos/120252656552890651_video.mp4`, 360×640, 15.8 s. Se descargó de `effective_instagram_media__media_url`, post `DagaiuiMiU_`.
- **Texto principal:** vacío (caption de Instagram vacío).
- **Audio:** solo música. faster-whisper `small` con filtro de voz (VAD) detectó **0 segmentos de habla**. Sin ese filtro el modelo «transcribió» palabras sueltas sobre la música; se descartan.
- **Escenas** (cuadros por segundo en `creativos/120252656552890651_video_cuadros_por_segundo.jpg`):

| Tiempo | Escena | Texto en pantalla |
|---|---|---|
| 0–3 s | Mujer de blusa azul sentada en una oficina con libreros | «Facebook dice, lo más importante es quien vende tu producto» |
| 3–5 s | Mujer de traje oscuro frente a una casa | «Lo mejor es que sea tu mejor versión sin grabarte, 4 videos solo 500 al mes» |
| 5–7 s | La misma mujer caminando en una calle comercial | igual |
| 7–12 s | Pantalla negra | «Y con un sistema automático que te tenga el vídeo y campaña listos en una hora, para no tener que esperarme.» |
| 12–15 s | Pantalla negra | «Mándame WhatsApp con la frase "Quiero empezar mi anuncio por WhatsApp"» |

**Diferencia con el ganador:** el video promete la campaña lista **en una hora**; el ganador dice **4 horas**.

No hay otros videos en el contexto. Los videos de otros contextos también tienen `media_url` en `_fuente/q11_instagram_media.json`, por si se necesitan.

## 5. Sanaas

**Indicios de que promocionaba a la agencia:**
1. Se publicó desde la página de Facebook `112035195330595` (Visión Agencia) y la cuenta de Instagram **@visionagencia595** (`effective_instagram_media__username`).
2. Los botones llevan al WhatsApp de Carlos. El mensaje prellenado dice: «Hola, vi su anuncio de Sanaas. Mi negocio es ___ y me interesa el video de muestra».
3. **La oferta es la de la agencia:** adaptar videos virales a la marca del negocio, un video de muestra gratis y servicio de imprenta. Visión Agencia anuncia imprenta en otro anuncio propio (`120247020986250651`).
4. `120251557968510651`, de la campaña Sanaas «Copia 2», usa **la misma imagen «TU MARCA MERECE VENDER»** que el ganador. Carlos guardó como «Prospecto» a 3 personas que llegaron por ese anuncio (`sourceId`).

**Lo que falta:** no hay ningún documento que diga qué es «Sanaas». En este repositorio solo aparece en los anuncios, y una búsqueda web de «Sanaas» en Nogales no dio resultados. **Sin prueba, no se asume.**

**Tratamiento:** las 8 filas de Sanaas (4 anuncios) salieron de `03_historial_simulador.csv` y quedaron en `03b_sanaas_pendiente_propiedad.csv`, con el mismo esquema. **Esto no cambia el contexto del ganador**: ninguna fila de Sanaas es `traffic/conversacion_iniciada` con «Edad=18 - 65+; Lugar=México». Para cerrar el punto basta con que Carlos confirme qué es Sanaas.

## 6. Archivos

| Archivo | Contenido |
|---|---|
| `03_historial_simulador.csv` | 111 filas. Mismo esquema, mismos IDs, diario, sin duplicados ni solapamientos. Sin Sanaas. `idea` actualizada para el ganador y el video |
| `03b_sanaas_pendiente_propiedad.csv` | 8 filas de Sanaas pendientes de confirmar |
| `02_exportacion_original_nueva.json` | Consultas nuevas: Instagram (propios), horas de los días con cambio, contexto de WhatsApp agregado, páginas públicas y método de transcripción |
| `04_equivalencias_contexto.md` | Auditoría de etiquetas con evidencia |
| `05_inventario_contextos.csv` | Filas, anuncios, campañas y fechas por contexto |
| `creativos/` | Imagen del ganador (original y de Instagram), video, miniatura y cuadros por segundo |
| `_fuente/` | Consultas en bruto (solo propias) |

## 7. Pendiente de Codex (sin cambios)

`benchmark_id` sigue siendo por campaña. La campaña `120251563208660651` contiene el ganador y el video: 1,582.55 MXN y 104 conversaciones en total, contra 966.63 MXN y 84 del anuncio. Antes de comparar contra los 11.51 MXN hay que resolver la referencia por anuncio.
