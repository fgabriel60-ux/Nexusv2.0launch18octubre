# Encargo de Carlos · estrategia de 2 ángulos + imágenes (4 nov 2026, 21:30)

Carlos lo pidió en el chat con Claude (Codespace). Se copia aquí para que NO se caiga la orden:
Claude del Codespace ya la está ejecutando, tú continúala si él se queda sin uso o si algo se cae a medias.
Antes de empezar revisa qué hay ya hecho en `entregables/glimmer_imagenes_20261104/` para no repetir.

## Qué pidió, en orden

1. **Por cada cliente y prospecto: DOS ÁNGULOS de venta distintos.** El ángulo = la idea con la que se
   ataca al comprador (a quién le habla, qué le duele, la promesa con un dato REAL del cliente).
2. **DOS ANUNCIOS DE IMAGEN POR CADA ÁNGULO** (o sea 4 imágenes por negocio), cada uno con:
   qué se ve y de dónde sale la foto, titular en pantalla (máx. 7 palabras), línea de apoyo, formato
   (4:5 o 9:16), texto primario, botón, calificación esperada y qué le falta para 10.
3. **GUION para que el cliente lo grabe él mismo** con su celular (20-30 s): frase por frase, con qué
   debe estar grabando en cada frase, cómo poner el celular y la luz, y qué NO decir.
4. **GENERAR DE VERDAD LAS IMÁGENES** (no solo describirlas) con Qwen-Image-Edit a partir de sus FOTOS
   REALES, prioridad: **Mariano, Rafael (autos BYD) y Manuel (fotografía XV)**.
5. **Adrián el tatuador es prioritario aparte**: analizar el video que él mismo grabó y mandó hoy
   (`clientes/Tatuador9983316522/del_cliente_1104/tatu_b.mp4`, 17 s, 720x1280, SIN subtítulos),
   proponer los **subtítulos exactos con tiempos**, cómo llevarlo a **8 con lo que ya tenemos**
   (solo cortes, texto y audio, sin volver a grabar) y sus dos ángulos.

## Orden exacto de los negocios (lo dictó Carlos)

Adrián tatuador (prioritario) · Mariano · Rafael de carros · Giovanni Pulido · Fernando ·
Rubén Quiropraxia · ginecólogo (prospecto) · oficinas amuebladas León (prospecto) · Lisbeth terrenos ·
Víctor limpieza · Rashel Carrasco (prospecto) · Jesús Puertas (prospecto) · Ignacio Iglesia ·
Jesús cápsulas · Manuel fotografía.

## Lo que ya está hecho (al 4 nov 21:30)

- `entregables/glimmer_imagenes_20261104/clientes/*.md`: ronda 1, 5 ideas de imagen por cliente (17 clientes).
- `entregables/glimmer_imagenes_20261104/lote_prioridad.json`: lote en el orden de arriba, con el
  tatuador primero y con sus 10 cuadros + transcripción. **Corriendo en Modal (charlyfavela666).**
  Log: `entregables/glimmer_imagenes_20261104/prioridad.log`.
- Pendiente: subir a 4 imágenes por negocio (2 por ángulo) y generar las de Mariano, Rafael y Manuel.

## Reglas

- Datos REALES del cliente: nada de precios, tiempos ni resultados inventados. Si falta, `[FALTA: ...]`.
- Las imágenes salen de SUS fotos (Qwen-Image-Edit); el texto va en capa aparte, nunca generado dentro.
- No le escribas a ningún cliente sin que Carlos lo pida en ese mensaje.
- Al terminar cada negocio, deja el archivo en `entregables/glimmer_imagenes_20261104/` y avísale a Carlos
  con rutas y calificación esperada.
