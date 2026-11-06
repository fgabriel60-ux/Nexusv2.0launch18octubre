# Propuesta para Visión Agencia IA y resultado del algoritmo

## Propuesta: «Tu marca merece vender»

**Texto del anuncio:**

> Tu marca merece vender.
>
> Por $500 al mes preparamos la campaña de tu marca, lista en 4 horas.
>
> Primero conoce nuestro trabajo con un video gratis de muestra.
>
> Escríbenos **MUESTRA** y cuéntanos qué vendes.

**Pieza propuesta:** imagen cuadrada negra y naranja, manteniendo la estructura del anuncio histórico. Titular grande y tres tarjetas: «$500 al mes», «Lista en 4 horas» y «Video gratis de muestra». Un ejemplo de anuncio en un teléfono, identificado como muestra. CTA: «Enviar mensaje». Es un concepto escrito para evaluar antes de producir la imagen.

**Hipótesis:** conservar precio, rapidez y muestra gratuita de la pieza ganadora; conservar el gancho y hacer concreta la primera acción del prospecto. El historial respalda que esa combinación existió en el ganador; no permite aislar qué elemento causó su desempeño ni demostrar que la nueva redacción sea mejor.

Precio, plazo, alcance del servicio y condiciones de la muestra se tomaron del anuncio histórico. Deben confirmarse antes de publicar; falta aclarar si el precio incluye inversión publicitaria y desde cuándo corren las cuatro horas. Esta prueba no publica ni gasta dinero.

## Prueba ejecutada con dos anuncios

Carlos autorizó el modo exploratorio con dos anuncios y la referencia exclusiva por anuncio. Se utilizó la entrega más reciente de Claude: `historial_comparable_20260916/03_historial_simulador.csv`, 111 filas, sin Sanaas. El contexto exacto mantiene 18 filas: 17 días del ganador y solo un día comparable del video. No se incorporaron sus días con otra segmentación.

Se corrigió la referencia: `benchmark_scope=ad`, `benchmark_id=120251563209080651`. El video participa en la base histórica, pero sus resultados **no** se suman a la referencia. La selección de evento usa conversaciones, no clics. El mínimo exploratorio de dos anuncios se habilita explícitamente con `exploratory_two_ads=true`; el mínimo normal de tres y las reglas de validación textual permanecen.

Parámetros: 966.63 MXN, 19 días calendario, una propuesta, reparto uniforme, semilla 42, 600 réplicas, tolerancia al costo histórico 0%. El motor reparte el presupuesto por días; no reproduce la secuencia histórica de cambios presupuestales.

| Métrica | Ganador histórico | Escenario central (mediana) | P10–P90 del escenario |
|---|---:|---:|---:|
| Conversaciones | 84 | 93 | 71–127 |
| Costo por conversación | 11.51 MXN | 10.39 MXN | 7.61–13.61 MXN |
| Gasto | 966.63 MXN | 966.58 MXN | 966.53–966.62 MXN |

En el 70% de las 600 réplicas, el costo fue igual o inferior a los 11.5075 MXN históricos. **Es una fracción interna del escenario, no una probabilidad validada de éxito en Facebook.** Los extremos de costo y conversaciones son percentiles marginales y no parejas de una misma réplica.

## Interpretación

Dentro de estos supuestos, la mediana supera el resultado histórico, pero el rango también contiene resultados peores. **No está demostrado que la propuesta replique la ganadora.** El motor evaluó cero campañas y cero anuncios en validación temporal, y mantiene el modelo textual desactivado. Por ello, cambiar el gancho no mejora su pronóstico: otra descripción en el mismo contexto, con la misma semilla y configuración, obtiene la misma base numérica.

La cifra depende de supuestos sin calibrar: audiencia disponible de 10,000 personas, 2 oportunidades por persona/día, recuperación 0.65, competencia 1, dispersión de mercado 0.45, multiplicador de puja 1.5, fatiga 0.08 y dispersión de ejecución 0.35. El modelo usa una subasta simplificada cuyo precio condicionado puede hacer optimista el costo simulado. No reconstruye la entrega real de Meta. Los rangos P10–P90 no son intervalos de confianza calibrados.

La oferta propuesta agrega texto principal y la instrucción MUESTRA; el ganador, según Claude, se publicó sin texto principal y usó botones genéricos. Por tanto, es una variante de la oferta histórica, no una copia exacta.

## Verificación y archivos

Pasaron las **16 pruebas** del motor, incluidas la referencia por anuncio sin sumar al otro anuncio, el permiso explícito para usar dos, el rechazo con uno y la métrica de conversaciones para tráfico. No se publicó ninguna campaña ni se consumió presupuesto.

- `probar_propuesta.py`: ejecución reproducible.
- `propuesta.json`: concepto escrito.
- `entrada_motor.json`: historial, contexto, referencia y parámetros enviados.
- `resultado_motor.json`: salida completa de las 600 réplicas resumidas por el motor.
- `auditoria.json`: conteos, referencia y huellas de los archivos utilizados.

Replicar el costo histórico exige 84 conversaciones o más por 966.63 MXN efectivamente gastados. Calidad de contactos, pagos y rentabilidad siguen requiriendo medición aparte.
