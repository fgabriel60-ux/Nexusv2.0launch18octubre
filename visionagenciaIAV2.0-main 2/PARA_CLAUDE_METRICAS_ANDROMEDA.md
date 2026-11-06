# Para Claude: datos necesarios para Andromeda Lab

## Objetivo de Carlos

Evaluar ideas de anuncios **antes de producir imágenes o videos** y compararlas con
su mejor campaña de Facebook. Ya existe un simulador local. Necesitamos relacionar
el contenido de cada anuncio con sus métricas reales, no solo cargar resultados
agregados por campaña.

Tu extracción inicial ya está identificada y convertida a un resumen estructurado.
No repitas la búsqueda desde cero: amplía esa extracción con Windsor.ai, que según
tu informe tiene conectada la cuenta **684865860329838**. Supermetrics no funcionó
en esa extracción. Usa acceso de lectura; no publiques ni modifiques campañas.

## Lo que ya tenemos

Fuente: `entregables/campana_ganadora_facebook_20260916/METRICAS_CAMPANA_GANADORA.md`.

- Nueve campañas con información parcial.
- Referencia indicada por tu informe:
  **[8/6/2026] Promoción de https://api.whatsapp.com/send**.
- Periodo: 2026-06-08 a 2026-06-11.
- Gasto: 210.65; conversaciones iniciadas: 48.
- Costo calculado por conversación: **210.65 / 48 = 4.3885416667**.
- Impresiones: 7,786; CPM reportado: 27.06; CTR reportado: 5.83%.
- Conversaciones diarias: 1, 29, 10 y 8, respectivamente.
- Métrica de resultado usada:
  `actions_onsite_conversion_messaging_conversation_started_7d`.

Estos datos ya sirven como **referencia histórica**. Todavía no habilitan entrenamiento
por anuncio. En particular, el informe no especifica moneda, definición del CTR,
ventana de atribución, IDs de anuncios ni contenido creativo.

## Entrega prioritaria: datos reales a nivel anuncio

### 1. Confirmar configuración y definiciones

Consulta los campos disponibles del conector; no inventes nombres de campos API.
Documenta el mapeo de sus nombres reales a los encabezados del simulador.

- Moneda ISO de la cuenta: no asumir MXN ni USD a partir de `$`.
- Zona horaria de reportes.
- Objetivo real de campaña y evento de optimización del conjunto de anuncios.
- Definición exacta de conversación iniciada. Conserva la misma métrica de la referencia.
- Ventana/configuración de atribución realmente usada en la consulta.
  El sufijo `7d` del nombre de la acción no basta para inferirla.
- Definición de clics y CTR: distinguir todos los clics, clics de enlace y clics únicos.
- Fecha de extracción, rango temporal y granularidad.

### 2. Exportar todas las campañas del periodo, incluyendo perdedoras

Rango solicitado: **2026-04-01 a 2026-09-15**, inclusivo, según la zona horaria de
la cuenta. Así se incluyen la referencia de junio y la campaña de abril. No limitar
la exportación a los últimos 90 días, porque dejaría fuera parte de la referencia.

Preferimos **una fila por anuncio por día, agregada sobre ubicaciones**. No combinar
en el mismo archivo filas diarias con totales de campaña o totales del periodo.
Si el conector no permite datos diarios por anuncio, entrega una fila por anuncio
por periodo no superpuesto e indica la limitación.

Incluye anuncios pausados, archivados y con cero conversiones cuando sean accesibles.
No selecciones solo ganadores ni solo anuncios con resultados. Si hay límites de
filas, pagina o divide las consultas por fechas sin duplicar días. Documenta qué
quedó fuera. Conserva los resultados recientes sin declararlos maduros; separa la
vista apta para modelado según el retraso de atribución verificado.

### 3. Obtener qué decía y mostraba cada anuncio

Para cada `ad_id`, necesitamos el texto principal, título, descripción, CTA, formato,
oferta y una descripción fiel de la pieza visual. Incluye `creative_id`, enlace de
vista previa y URL del recurso si el acceso los permite.

El campo normalizado `idea` debe resumir **gancho + escena o demostración + oferta +
llamada a la acción**, usando el creativo real. El nombre de campaña por sí solo
no sirve como descripción. Distingue texto literal de descripción visual redactada.
Si no puedes acceder al contenido, déjalo ausente y reporta el bloqueo; no lo deduzcas
de que la campaña haya funcionado bien.

Para creativos dinámicos o varias versiones bajo un mismo ID, documenta la variación
y no atribuyas todo el rendimiento a una pieza concreta sin desglose suficiente.

## Contrato de importación actual

El CSV normalizado usa UTF-8, coma como delimitador, punto decimal, números sin
símbolos monetarios ni separadores de miles. JSON admite una lista de registros.
Los IDs deben ser strings para evitar pérdida de precisión.

| Campo del simulador | Qué debe contener |
|---|---|
| `ad_id` | ID real del anuncio, no un identificador inventado para una campaña |
| `campaign_id` | ID real de campaña |
| `date_start` | Inicio inclusivo `AAAA-MM-DD` |
| `date_end` | Fin inclusivo `AAAA-MM-DD`; igual al inicio en datos diarios |
| `idea` | Descripción fiel del creativo, con texto/escena/oferta/CTA |
| `account_id` | `684865860329838` |
| `currency` | Moneda confirmada de la cuenta |
| `objective` | `messages`, `leads`, `sales` o `traffic`, con mapeo documentado |
| `result_type` | Evento exacto que se contó; para referencia, conservar la métrica de conversaciones |
| `attribution` | Etiqueta estable de la configuración confirmada |
| `placement` | `mixed` solo si las ubicaciones vienen realmente agregadas |
| `audience` | Etiqueta estable del público y mercado, obtenida de la configuración real |
| `spend` | Gasto |
| `impressions` | Conteo de impresiones |
| `link_clicks` | Clics de enlace, no todos los clics ni clics únicos |
| `results` | Conteo del evento declarado, con cero explícito cuando corresponda |
| `revenue` | Opcional: ingresos atribuidos; dejar ausente si no hay evidencia |

Además, conserva en la exportación enriquecida `campaign_name`, `adset_id`,
`adset_name`, `ad_name`, `creative_id`, objetivo original, evento de optimización,
país/mercado, formato, estado, texto original, URL de vista previa y madurez de
atribución. El importador actual puede ignorar columnas adicionales; no las elimines
del archivo fuente.

No traduzcas automáticamente una campaña de interacción a `messages`: comprueba
el evento de optimización. Mantén las campañas de tráfico separadas de las de
mensajes. Si el objetivo no puede mapearse con certeza, conserva el valor original
y excluye esa fila del CSV listo para modelar, explicando la razón.

No uses IDs únicos de conjunto como etiquetas de audiencia por comodidad: eso
fragmentaría los contextos e impediría comparar públicos equivalentes. Si necesitas
agrupar públicos, documenta el criterio; no unas mercados distintos sin evidencia.

## Reglas para no contaminar el modelo

1. **Ausente no es cero.** No rellenar métricas desconocidas con ceros.
2. No reconstruir clics a partir de CTR redondeado, ni impresiones a partir de CPM
   redondeado. Obtener conteos de la fuente.
3. No convertir resúmenes de campaña en supuestos anuncios ni fabricar descripciones.
4. No mezclar monedas, eventos de resultado, atribuciones o públicos distintos.
5. No duplicar totales al combinar consultas o desgloses. El importador actual
   rechaza periodos solapados para un mismo anuncio, incluso con distinto placement.
6. Con cero conversaciones, costo por conversación es indefinido, no cero.
7. Las conversiones atribuidas pueden superar los clics de enlace: no descartarlas
   automáticamente ni forzar un embudo de clics a conversiones.
8. No interpretar conversaciones como ventas. El informe no prueba las dos ventas
   mencionadas por Carlos; ingresos y ROAS requieren datos adicionales.
9. No copiar tokens o credenciales a los entregables ni imprimirlos en logs.
10. Mantener esta entrega limitada a métricas y creativos; no se necesitan nombres,
    teléfonos ni mensajes de los prospectos.

## Archivos que debe entregar Claude

Crear carpeta:

`entregables/facebook_ads_para_andromeda_20260916/`

Entregables:

1. **`facebook_ads_raw.json`**: resultados originales de las consultas, sin tokens.
2. **`facebook_ads_enriched.json`**: métricas unidas al catálogo de creativos por ID,
   conservando ausencias y metadatos.
3. **`facebook_ads_normalizado.csv`**: solo registros completos y aptos para el
   contrato anterior, sin inventar campos faltantes. Separar en archivos de hasta
   5.000 filas / 8 MB si hace falta y documentar su unión sin duplicados.
4. **`creativos.json`**: catálogo con texto, descripción, CTA, formato y referencias.
5. **`VALIDACION.md`**: consultas, campos originales, mapeo, filtros, paginación,
   filas excluidas, limitaciones, fechas de extracción y cobertura efectiva.

Si el conector solo permite nivel campaña o no devuelve creativos, entrega lo que
sí obtengas, indica exactamente qué endpoint/campo falta y **no generes un CSV
aparentemente completo** con datos inventados. No prometas entrenamiento terminado.

## Comprobación imprescindible de la referencia

Al agregar sus anuncios entre el 8 y 11 de junio, intenta reconciliar:

| Métrica | Informe anterior |
|---|---:|
| Gasto | 210.65 |
| Impresiones | 7,786 |
| Conversaciones | 48 |
| Conversaciones por día | 1, 29, 10, 8 |

Registra coincidencias y diferencias. Si cambian los valores por atribución,
actualización o filtros, conserva ambas extracciones con su configuración. No
alteres la nueva exportación para que coincida artificialmente.

## Dónde está el simulador

Directorio absoluto:

`/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/andromeda-lab/`

Archivos relevantes:

- `engine.py`: validación, analogías textuales, prueba temporal y escenarios.
- `server.py`: API y servidor local.
- `METODOLOGIA.md`: supuestos y límites.
- `local-data/facebook_reference.json`: resumen de las nueve campañas ya preparado;
  directorio excluido de Git. No sobrescribirlo con datos sintéticos.
- `static/reference.js`: presentación de la referencia agregada, separada del
  historial de entrenamiento.

Comprobar el archivo normalizado sin modificar el motor:

```python
from pathlib import Path
from engine import parse_history

csv_text = Path("/ruta/facebook_ads_normalizado.csv").read_text(encoding="utf-8-sig")
rows, duplicates = parse_history(csv_text)
print({"filas_validas": len(rows), "duplicados_exactos": duplicates})
```

Ejecutar desde el directorio del simulador. Validar el CSV es distinto de demostrar
precisión predictiva. El motor exige al menos tres anuncios comparables para ejecutar
escenarios y aplica una comprobación temporal adicional antes de diferenciar ideas
por su texto. Más datos útiles y diversidad creativa importan más que llegar al mínimo.

**Al terminar:** comunica las rutas exactas, número de anuncios y campañas, periodo,
moneda, atribución, porcentaje con creativo disponible, reconciliación de la referencia
y cualquier dato que siga faltando. Mantén el trabajo en la extracción y preparación
de datos; no cambies el motor ni reinicies servicios que esté usando Astra.
