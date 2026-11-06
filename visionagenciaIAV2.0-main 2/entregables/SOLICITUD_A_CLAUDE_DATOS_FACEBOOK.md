# Claude: recuperar mi campaña ganadora y el historial para el simulador

Tengo un simulador local llamado Andromeda Lab. Quiero que Codex pueda proponer una campaña tomando como referencia mi mejor costo por conversación de WhatsApp. Tú tienes acceso a mi Facebook: recupera los datos y materiales indicados aquí y devuélvelos como archivos descargables.

Esta solicitud autoriza consultar y exportar información. No publiques, edites, dupliques ni actives campañas y no consumas presupuesto publicitario. No incluyas contraseñas, tokens ni datos personales de las conversaciones.

## 1. Identificar y reconstruir la campaña ganadora

Cuenta publicitaria de referencia: `684865860329838`. Confirma nombre de cuenta, moneda y zona horaria.

Según una extracción de Windsor.ai del 16 de septiembre de 2026:

- Campaña: `[8/6/2026] Promoción de https://api.whatsapp.com/send`.
- Periodo observado: 8–11 de junio de 2026.
- Objetivo reportado: `MESSAGES`.
- Conversaciones iniciadas: **48**.
- Gasto: **210.65**; costo por conversación: **4.39**.
- Impresiones: **7,786**; CPM aproximado: **27.06**.
- Campo de resultados del conector: `actions_onsite_conversion_messaging_conversation_started_7d`.

Son datos de referencia que debes verificar, no valores que debas forzar. Confirma la moneda; el historial local se normalizó como MXN. Si hay diferencias, explica periodo, zona horaria, atribución o definición de evento que puedan causarlas. El sufijo del campo del conector no basta para deducir la ventana de atribución.

Recupera de esta campaña, sus conjuntos y sus anuncios:

1. IDs y nombres originales, fechas de inicio/fin y estado.
2. Texto principal completo, título, descripción, CTA y destino del anuncio.
3. Imagen o video original descargable, si está accesible; en su defecto, enlace de publicación/vista previa y capturas. Para video, transcripción y descripción de las escenas principales, con tiempos cuando sea posible. No inventes lo que no puedas ver.
4. Oferta concreta: qué se prometía, precio/promoción y a quién se dirigía.
5. Objetivo original, objetivo de rendimiento/evento de optimización, aplicación de mensajería de destino y estrategia de puja.
6. Presupuesto diario o total, si estaba a nivel campaña o conjunto, y cambios históricos si están disponibles. Distingue configuración actual de configuración durante la entrega.
7. Segmentación: zonas y radios, edades, idiomas, intereses, exclusiones, públicos personalizados/similares y opciones de expansión/Advantage que consten. Basta identificar los públicos; no exportes sus miembros.
8. Ubicaciones automáticas/manuales y plataformas incluidas.
9. Ventana de atribución utilizada y configuración inicial de conversación: saludo, preguntas o plantilla, si existe.
10. Resultados diarios por anuncio: gasto, impresiones, alcance, frecuencia, clics de enlace, conversaciones iniciadas y costo por conversación. Indica la definición exacta del CTR si lo reportas.

Si una configuración histórica o un material no está disponible, márcalo explícitamente como **no disponible**.

## 2. Recuperar historial comparable, incluidos los anuncios que fallaron

Exporta el historial disponible del 1 de enero al 16 de septiembre de 2026, o hasta la fecha de extracción si es anterior. Prioriza todas las campañas orientadas a conversaciones/mensajes, con sus anuncios y creativos. Si hay historial anterior útil, entrégalo en un archivo separado. Incluye anuncios pausados o archivados si son accesibles.

No selecciones solamente ganadores: necesitamos también anuncios con gasto y cero conversaciones. Conserva por separado campañas de tráfico, leads o ventas; no las conviertas en campañas de mensajes porque registraron alguna conversación.

Para cada anuncio recupera el texto completo y una descripción fiel de gancho, escena, oferta y CTA. Vincula todo mediante `ad_id`. Incluye también metadatos originales de campaña/conjunto, segmentación, atribución y fechas para determinar comparabilidad.

La última simulación solo tenía 4 anuncios de mensajes utilizables. El motor necesita, para cada campaña evaluada, al menos 5 anuncios de otras campañas terminadas antes de su inicio. Solo habilita diferencias basadas en texto después de evaluar al menos 8 anuncios en al menos 3 campañas y reducir el error más de un 5% frente al promedio histórico. **No basta con reunir 8 anuncios totales y no debes fabricar divisiones de campañas para llegar al mínimo.** Extrae todo lo disponible y reporta lo que falta; no hace falta lanzar campañas nuevas para cumplir esta solicitud.

## 3. Formato de entrega

Entrega estos archivos, idealmente juntos en un ZIP:

- `01_campana_ganadora.md`: reconstrucción completa y tabla de resultados diarios.
- `02_historial_original.csv` o `.json`: exportación original con nombres de métricas y metadatos, sin sobrescribir ni reinterpretar la fuente.
- `03_historial_simulador.csv`: versión normalizada según el esquema siguiente, solo con registros cuyos campos necesarios estén verificados.
- `04_creativos.csv`: IDs de anuncio/campaña/conjunto, textos, descripción visual, enlaces y nombres de archivos descargados. Una fila por variante si existen variantes identificables; no repartas métricas entre variantes sin evidencia.
- `05_calidad_y_faltantes.md`: fuente, fecha de extracción, periodo, zona horaria, atribución, campos faltantes, discrepancias y conteos de campañas/anuncios disponibles por contexto comparable.
- Carpeta `creativos/`: imágenes, videos o capturas recuperadas.

### CSV para Andromeda Lab

UTF-8, separado por comas, decimales con punto, importes sin símbolos ni separadores de miles. IDs conservados como texto. Encabezado exacto:

```csv
ad_id,campaign_id,date_start,date_end,idea,account_id,currency,objective,result_type,attribution,placement,audience,spend,impressions,link_clicks,results
```

Definiciones:

| Campo | Qué colocar |
|---|---|
| `ad_id`, `campaign_id` | IDs originales y estables; no renombrar ni inventar campañas. |
| `date_start`, `date_end` | Fechas inclusivas `AAAA-MM-DD`. Preferentemente una fila por anuncio por día; ambas fechas iguales. |
| `idea` | Texto real más descripción fiel del creativo: gancho, escena, oferta y CTA. Escapar comillas y comas según CSV. |
| `account_id`, `currency` | Cuenta y moneda verificadas. |
| `objective` | `messages`, `leads`, `sales` o `traffic`, con mapeo documentado desde el objetivo y la optimización originales. |
| `result_type` | Para mensajes, `conversacion_iniciada`, únicamente si corresponde al evento verificado. |
| `attribution` | Ventana exacta utilizada para esas métricas. No asumir `7d_click_1d_view` por defecto. |
| `placement` | `mixed` si las métricas están agregadas entre ubicaciones; conservar el detalle de configuración por separado. |
| `audience` | Etiqueta estable basada en público/mercado real. No usar el nombre de campaña como sustituto ni agrupar públicos diferentes para pasar los filtros. |
| `spend` | Gasto en la moneda declarada. |
| `impressions` | Impresiones. |
| `link_clicks` | Clics de enlace; no todos los clics ni clics únicos. |
| `results` | Conteo del evento declarado. Cero solo cuando la fuente confirma cero; ausencia de información no equivale a cero. |

Mantén una sola granularidad en el CSV normalizado. No mezcles totales de campaña con sus anuncios o totales del periodo con sus filas diarias. No mezcles desgloses de ubicaciones con sus totales. No dupliques un anuncio al recuperar variantes de su creativo.

El simulador separa contextos por cuenta, moneda, objetivo, evento, atribución, ubicación y audiencia. Conserva diferencias reales aunque reduzcan la muestra. Si un campo necesario es desconocido, conserva el registro en la exportación original y explica por qué no pudo normalizarse. Señala los periodos recientes cuya atribución todavía podría cambiar.

El importador admite hasta 5,000 filas / 8 MB por archivo: si se excede, divide en archivos claramente identificados sin perder la exportación completa. Codex preparará la carga; el simulador reemplaza el conjunto importado y no acumula archivos automáticamente.

## 4. Verificaciones finales

- Recalcula costo por conversación como gasto total / conversaciones totales; no promedies costos diarios.
- Contrasta la campaña ganadora con la referencia de 48 conversaciones y 210.65 de gasto, documentando cualquier diferencia.
- Como segunda referencia, busca `[16/6/2026] Promoción de https://api.whatsapp.com/send`: se reportaron 14 conversaciones y 98.22 de gasto entre el 16 y el 18 de junio.
- Mantén separadas las campañas «Sanaas - 1 Video Gratis»: los datos locales indican que las de tráfico tuvieron CPM bajo, pero eso no las convierte en ganadoras por conversaciones.
- Separa evidencia recuperada de interpretaciones. No atribuyas el éxito a una imagen, segmentación u oferta solo por correlación.
- Si hay métricas agregadas verificables de contactos calificados, ventas o ingresos, entrégalas aparte y explica su fuente. No deduzcas ventas a partir de conversaciones ni leas chats personales para esta extracción.

Al terminar, resume qué recuperaste, qué no está accesible y cuántos anuncios con creativo y resultados completos quedan disponibles. Con estos archivos Codex reconstruirá la referencia, comprobará qué historial es comparable y preparará propuestas. La simulación por sí sola no garantiza repetir el resultado en Facebook.
