# Respuesta de Claude a `SOLICITUD_A_CLAUDE_DATOS_FACEBOOK.md`

Para Astra. Carlos pidió que te pasara esto. La extracción ya está terminada. Queda **un pendiente para ti**: cruzar los pagos que están en Nexus con los prospectos (§4).

Todo se hizo en modo lectura: con Windsor.ai no se creó, editó ni activó nada en la cuenta, y en WhatsApp solo se consultó información, no se mandó nada a clientes.

## 1. Cambio importante respecto a tu solicitud

- **La referencia que pedías (`[8/6/2026]`, 48 conversaciones, 210.65) no es de Visión Agencia.** Es una promoción de un cliente (página `216277825416153`). Lo mismo pasa con `[16/6/2026]`. Las cifras coincidían al peso, pero **Carlos pidió excluir todo lo que no sea suyo**. Por eso se quitaron 15 anuncios de 9 campañas: los de otras páginas y las campañas «LEQ» y «Amy vip».
- **La ganadora real es el anuncio `120251563209080651`** de la campaña «Nuevo Tráfico Campaña». Carlos la confirmó con una captura de Ads Manager:
  - **84 conversaciones · 11.51 MXN por conversación · 966.63 de gasto** · 6,904 impresiones · 3,610 de alcance.
  - Pieza «TU MARCA MERECE VENDER»: $500 al mes, campaña lista en 4 horas, video gratis de muestra.
  - Corrió del 17/6 al 5/7, con segmentación México 18–65+, ubicaciones automáticas, sin límite de puja y presupuesto de $50–75 al día.
  - **El objetivo es `LINK_CLICKS` optimizado a `CONVERSATIONS`.** En el CSV va como `traffic` + `conversacion_iniciada`, en un contexto distinto de `messages`. Si decides unirlos, que sea explícito.
- Sanaas se consideró propio porque sale de la página de Visión Agencia y del WhatsApp de Carlos. Hay que confirmarlo.

## 2. Entregables

Carpeta: `entregables/solicitud_datos_facebook_20260916/`. También está en ZIP: `entregables/solicitud_datos_facebook_20260916.zip`.

| Archivo | Contenido |
|---|---|
| `01_campana_ganadora.md` | Reconstrucción completa del ganador: IDs, pieza, oferta, puja, historial de presupuesto y segmentación, ubicaciones, tabla diaria |
| `02_historial_original.json` / `02_historial_original_diario.csv` | Consultas originales, solo con anuncios propios, sin reinterpretar |
| `03_historial_simulador.csv` | **119 filas, 43 anuncios, 19 campañas**, del 2026-03-25 al 2026-08-10, con tu encabezado exacto |
| `04_creativos.csv` | 47 filas: una por variante de texto de cada uno de los 46 anuncios |
| `05_calidad_y_faltantes.md` | Mapeo, audiencias, exclusiones, conteos por contexto, faltantes y avisos |
| `06_prospectos_whatsapp.md` / `06_prospectos_whatsapp_anonimo.csv` | Cruce con WhatsApp (§3) |
| `creativos/`, `extras/` | Imágenes; ubicaciones, cambios de presupuesto y segmentación, compras marcadas en el chat, historial de 2024, resumen de construcción |

## 3. Datos clave para el motor

- **Moneda:** MXN. **Zona horaria:** America/Tijuana. **Atribución:** `7d_click_1d_view`, con la ventana de atribución madura.
- **`audience`** se calculó **día por día a partir del historial de cambios de segmentación**. Los días en que cambió la segmentación quedaron fuera de `03`: 10 filas.
- **Reglas mínimas:**
  - Ningún contexto de conversaciones cumple **≥5 anuncios previos** del mismo contexto. Para la ganadora hay 0.
  - Ninguno cumple **≥8 anuncios en ≥3 campañas**. No se agruparon públicos ni se fabricaron divisiones de campañas para llegar al mínimo.
- **Faltantes:**
  - Texto principal de 24 de 46 anuncios, incluida la ganadora. Para esos, la `idea` usa el texto visible en la imagen.
  - Archivos y transcripciones de los videos.
  - `attribution_spec` guardado en cada conjunto.
  - Saludo inicial.
- **Aviso:** Meta registra `Idioma: Polaco` en 4 conjuntos propios de mayo. Hay que confirmarlo.
- **Ventas:** Meta solo tiene 2 compras marcadas en el chat, con valor 0. Una es del anuncio ganador, el 19/6.
- **WhatsApp:** hay 48 contactos «Prospecto». En el primer mensaje, WhatsApp guarda `ctwaContext.sourceId`, que es el ID del anuncio de origen:
  - **35 vienen del anuncio ganador** (del 18 al 25 de junio), 3 de la misma pieza en Sanaas y 10 sin dato.
  - Del 18 al 25/6, Meta contó 47 conversaciones; 35 de ellas (74 %) son prospectos guardados.
  - 20 de esos 35 (57 %) siguieron escribiendo.
  - Del 26/6 en adelante no se guardó ningún prospecto, aunque Meta contó 37 conversaciones más. Hay que preguntarle a Carlos por qué.

## 4. Pendiente para ti: pagos en Nexus

Carlos dice que **los clientes que pagaron están en Nexus** (`cartera-rj26.onrender.com/nexus`). No pude entrar: `/api/cartera` pide `x-clave` y esa clave no está en ningún archivo de este Codespace. Tampoco la saqué de Render sin su permiso.

Lo que falta hacer:

1. Obtener de Nexus los clientes que pagaron: teléfono, fecha y monto.
2. Cruzarlos con los 48 prospectos **por teléfono**. Los teléfonos no están en el CSV. Para relacionarlos, vuelve a consultar los contactos de WhatsApp cuyo nombre contiene «Prospecto» con WAAPI `get-contacts`, y el origen de cada chat con `fetch-messages` → `message._data.ctwaContext.sourceId`. Las credenciales están en `visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env`.
   - El orden P01–P48 del CSV es por fecha del primer mensaje y, en empate, el mismo orden que devolvió `get-contacts` (nombres únicos). **No asumas que coincide al 100 %.** Vuelve a generar el cruce desde cero.
3. Agregar al CSV anonimizado las columnas `pago` (sí/no), `fecha_pago` y `monto_mxn`, **sin nombres ni teléfonos**.
4. Con eso, calcular el **costo por cliente pagado de la ganadora** como 966.63 / clientes pagados que tengan `sourceId = 120251563209080651`. Solo debe salir de clientes con evidencia en Nexus. No lo deduzcas de las conversaciones.
5. Cuidado con el sesgo: del 26/6 al 5/7 no hay prospectos guardados, así que un cliente de esas fechas puede no aparecer en los 48. Revisa en Nexus a los clientes que no hagan match antes de descartarlos.

Si hace falta, `_fuente/construir.py` regenera 02–05 a partir de las consultas guardadas en `_fuente/`. Esa carpeta tiene datos de clientes y **no va en el ZIP**.
