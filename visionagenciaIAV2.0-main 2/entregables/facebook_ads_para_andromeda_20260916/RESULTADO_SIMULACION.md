# Simulación: video de Mariano y los 6 flyers contra tu campaña ganadora

Corrida el 16 sep 2026 con el motor de Andromeda Lab (`engine.run`, versión 0.1.0), en proceso, sin levantar el
servidor de Astra. Informe completo: `informe_simulacion_mariano_flyers.json`.

## Qué se comparó

- **7 ideas**: el video de Catania de Mariano y los 6 flyers de San Marino, descritos con gancho, escena, oferta y
  llamada a la acción (`ideas_mariano_y_flyers.json`).
- **Historial**: 16 filas, **4 anuncios**, 4 campañas de mensajes. Carlos autorizó agruparlas en un solo contexto
  porque cada una tenía un anuncio y el motor exige 3. Criterio: mismo anunciante, mismo mercado, mismo evento
  contado y misma atribución. El CSV agrupado es `facebook_ads_normalizado_agrupado.csv`; el original no se tocó.
- **Referencia**: tu campaña ganadora, `[8/6/2026] Promoción de api.whatsapp.com/send`, que el motor aceptó y
  resolvió en **$4.39 por conversación**, 48 conversaciones, $210.65, CPM $27.05.
- **Escenario**: presupuesto $1,500 MXN, 7 días, reparto igual entre las 7 ideas, semilla 42.

## El resultado que importa

**El motor NO predice que el video o los flyers vayan a superar tu campaña ganadora, y explícitamente se niega a
ordenarlos.** Su aviso textual:

> «No se ordenan las ideas como ganadoras: el modelo textual todavía no supera la referencia en validación.
> Diferencias numéricas pueden ser ruido Monte Carlo.»

La razón está en la validación temporal: `tested_ads: 0`, `tested_campaigns: 0`, `text_model_enabled: false`.
Con 4 anuncios no alcanza para ninguna prueba: el motor exige entrenar con 5 anuncios anteriores por cada campaña
de prueba, y necesita 8 anuncios y 3 campañas para activar el modelo de texto. Por eso trató a las 7 ideas con la
**misma base común** y lo dice en cada una: «Base común: no hay evidencia suficiente para diferenciar esta idea».

## Los números, con esa advertencia por delante

| Idea | Conversaciones p10 | mediana | p90 | CPA mediano |
|---|---:|---:|---:|---:|
| Video Catania de Mariano | 0 | 7 | 58 | $5.48 |
| Flyer 2 · 3 formas de vivir | 0 | 9 | 59 | $5.29 |
| Flyer 5 · El mar pone la vista | 0 | 7 | 57 | $5.71 |
| Flyer 6 · Lotes en zona costa | 0 | 7 | 55 | $5.87 |
| Flyer 3 · Tarde Mexicana | 0 | 6 | 60 | $5.79 |
| Flyer 1 · Vivir bien empieza por el entorno | 0 | 5 | 59 | $5.93 |
| Flyer 4 · Últimos lotes | 0 | 4 | 59 | $6.30 |

Totales del escenario: gasto mediano $532.74 de los $1,500 disponibles, 131 conversaciones medianas entre las 7.

**Cómo leer esto sin engañarse:**

1. **El orden de la tabla no significa nada.** La diferencia entre 4 y 9 conversaciones es ruido del muestreo, no
   una señal de que el flyer 2 sea mejor que el 4. El propio motor lo advierte.
2. **El CPA sale peor que tu referencia**: $5.29 a $6.30 contra tus $4.39. Tampoco es una predicción firme, pero sí
   dice que el escenario no asume que estas ideas vayan a mejorar lo que ya lograste.
3. **El p10 es 0 en las siete.** En más del 10 % de los escenarios simulados una idea no consigue ni una sola
   conversación. Ese riesgo es real y el modelo no lo esconde.
4. **El rango p10–p90 es enorme** (de 0 a ~58). Con 4 anuncios de historial no hay forma de estrechar eso.

## Qué haría falta para que esto sirva de verdad

El simulador no está roto: está diciendo honestamente que **no tiene datos suficientes**. Para que pueda
diferenciar una idea de otra necesita, según su propia validación:

- **8 anuncios de mensajes con su texto** y **3 campañas** distintas, para activar el modelo textual.
- Hoy tienes 4 anuncios de mensajes y solo 25 de tus 56 anuncios traen texto rescatable.

La vía práctica: correr los próximos videos de Mariano y los flyers como campañas de mensajes con su texto
completo, e ir alimentando el historial. Con eso, en unas semanas el motor sí podría comparar ideas antes de
producirlas, que es justo para lo que Astra lo construyó.

## Advertencias del propio motor

- Los rangos P10–P90 son resultados del escenario, no intervalos de confianza calibrados para Facebook.
- La subasta, recuperación, afinidad, fatiga y calidad de ejecución son supuestos editables.
- El parecido entre textos no demuestra que una idea cause mejores resultados.
- La referencia elegida es retrospectiva y su selección puede ser optimista.
