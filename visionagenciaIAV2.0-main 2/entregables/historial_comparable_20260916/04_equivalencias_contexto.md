# 04 — Auditoría de etiquetas de público

**Método.** Cada `audience` de `03_historial_simulador.csv` se separó en componentes: Lugar, Edad o Edad mínima, Idioma, Intereses, Personas que coinciden con, Público personalizado, Público similar y los interruptores de Advantage+. Dentro de cada componente se ordenaron las listas, separando por «, », « o » y «/». Después se compararon todos los pares de etiquetas que tienen el mismo `objective` y `result_type`.

## Resultado

| Tipo de diferencia | Pares | Decisión |
|---|---:|---|
| Solo formato u orden, con componentes idénticos | **0** | — |
| Un solo componente distinto | 3 | **Se mantienen separadas**: en los tres casos cambia la configuración real |
| Dos o más componentes distintos | el resto | Se mantienen separadas |

### Pares con un solo componente distinto

| Objetivo / evento | Etiqueta A (anuncios) | Etiqueta B (anuncios) | Qué cambia | ¿Equivalentes? |
|---|---|---|---|---|
| messages / conversacion_iniciada | Edad mínima=18; México; Advantage+ activado (3) | lo mismo + **Público similar (2%) – People who like Vision Agencia** (1) | Se agrega un público similar | **No** |
| traffic / conversacion_iniciada | Edad=18 - 65+; México (2) | Edad=18 - 65+; **Nogales +25 mi (MX) y Nogales AZ +25 mi** (1) | Cambia la ubicación | **No** |
| traffic / link_click | Edad=18 - 65+; México; Advantage+ desactivado (1) | Edad=**25 - 60**; México; Advantage+ desactivado (10) | Cambia el rango de edad | **No** |

### Caso dudoso: la línea «Público Advantage+»

Algunas etiquetas no traen la línea «Público Advantage+» y otras dicen «Público Advantage+: Desactivado».

- **Conjunto `120251572153320651`** (no cambió después del 17/6 22:01): el registro no trae la línea y el JSON actual tampoco tiene `targeting_automation`.
- **Conjunto del ganador `120251563208930651`**: desde el 8/7 el registro muestra «Desactivado» y el JSON actual tiene `targeting_automation.advantage_audience = 0`.
- **No hay evidencia** de que Meta trate igual «sin el campo» y «campo = 0». Por eso **no se propone ningún mapeo**.
- Este caso **no afecta al contexto del ganador**. La única etiqueta que se distingue solo por esa línea es «Edad=18 - 65+; Lugar=México; Público Advantage+=Desactivado» (Sanaas URL wa.me), y está en `traffic/link_click`, no en `traffic/conversacion_iniciada`.

## Mapeo canónico propuesto

**Ninguno.** Unir cualquiera de estos pares mezclaría públicos que estaban configurados de forma distinta.
