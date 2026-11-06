# 06: Prospectos de WhatsApp que llegaron por los anuncios

**Fuente:** los contactos del WhatsApp del anunciante (5216312470486) cuyo nombre contiene «Prospecto». Se consultaron el 16 sep 2026 con WAAPI, a pedido del anunciante.

**Privacidad:** no se incluyen nombres, teléfonos ni el contenido de los mensajes. De cada chat solo se tomaron fechas, cuántos mensajes hubo en cada sentido y el **identificador del anuncio de origen** (`ctwaContext.sourceId`). WhatsApp agrega ese identificador al primer mensaje cuando alguien escribe desde un anuncio de clic a WhatsApp.

Detalle por prospecto, anonimizado: `06_prospectos_whatsapp_anonimo.csv`.

## Resultado

| Origen (según WhatsApp) | Prospectos | Primer mensaje | Siguieron escribiendo (más de 1 mensaje) | Con 5 mensajes o más |
|---|---:|---|---:|---:|
| **`120251563209080651`, la ganadora «Tu marca merece vender»** | **35** | 18 al 25 de junio | 20 (57 %) | 10 |
| `120251557968510651`, la misma pieza en «Sanaas… Audiencia Tibia MENSAJES - Copia 2» | 3 | 18 y 19 de junio | 3 | 2 |
| Sin dato de anuncio (llegaron por otra vía o el dato no se guardó) | 10 | del 12 de mayo al 16 de septiembre | 7 | 4 |
| **Total de contactos «Prospecto»** | **48** | | | |

**La vinculación es directa, no se deduce de las fechas.** Los 35 chats traen el `ad_id` exacto de la ganadora. La URL de origen es su publicación de Instagram, `DZuCLsTDCCe`, con el título «Chatea en Messenger».

## Comparación diaria con Meta (anuncio ganador)

| Fecha | Conversaciones según Meta | Prospectos en WhatsApp con ese origen |
|---|---:|---:|
| 2026-06-18 | 5 | 3 |
| 2026-06-19 | 2 | 2 |
| 2026-06-20 | 5 | 4 |
| 2026-06-21 | 6 | 5 |
| 2026-06-22 | 10 | 7 |
| 2026-06-23 | 6 | 4 |
| 2026-06-24 | 6 | 3 |
| 2026-06-25 | 7 | 7 |
| **18 al 25 de junio** | **47** | **35 (74 %)** |
| 26 de junio al 5 de julio | 37 | 0 |

## Cómo leer esto

- Del **18 al 25 de junio**, 35 de las 47 conversaciones que contó Meta (74 %) están registradas como prospectos con su anuncio de origen. La diferencia puede venir de:
  - conversaciones por **Messenger**, porque el destino era Messenger + WhatsApp y aquí solo se revisó WhatsApp;
  - personas que no se guardaron como contacto;
  - la forma de contar de Meta, que usa la ventana de atribución de 7 días.
  Con estos datos no se puede separar cuánto pesa cada causa.
- **Del 26 de junio en adelante no hay ningún prospecto guardado**, aunque Meta contó 37 conversaciones más. Lo más probable es que se dejara de guardar contactos con la etiqueta «Prospecto», pero no está verificado. **No hay que interpretarlo como que el anuncio dejó de traer gente real.**
- **Calidad (aproximada):** 20 de los 35 prospectos de la ganadora escribieron más de un mensaje y 10 escribieron 5 o más. Es solo un conteo de actividad, **no indica ventas ni interés calificado**, porque no se leyó el contenido.
- **Fechas del último mensaje:** casi todos los chats tienen último mensaje el 15/9/2026. Parece un envío masivo del anunciante, así que esa fecha no sirve para medir seguimiento.
- **Límite de historial:** 3 contactos solo muestran mensajes del 16/9. Puede que su historial anterior no esté cargado en la sesión de WhatsApp Web.

## Uso sugerido para Andromeda Lab

- Sirve como **validación externa**: la mayoría de las conversaciones que Meta atribuye a la ganadora eran personas reales que escribieron por WhatsApp y más de la mitad siguió conversando.
- Da una **tasa de continuidad** aproximada: 57 % de los prospectos escribió más de un mensaje. Se puede usar como supuesto de embudo, pero **con una sola campaña de muestra**.
- **No sirve como historial de ventas.** Si Astra necesita ventas o contactos calificados, el anunciante tendría que marcar a mano cuáles de los prospectos P01–P48 compraron.
