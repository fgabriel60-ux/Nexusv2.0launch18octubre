# Claude: completar el historial comparable de Visión Agencia

Carlos quiere probar una propuesta con el gancho **TU MARCA MERECE VENDER**, conservando la oferta histórica de $500 al mes, campaña lista en 4 horas y video gratis de muestra. No publiques ni actives campañas: este encargo es de consulta y exportación.

## Lo que ya hizo Codex

- Usó tu entrega `entregables/solicitud_datos_facebook_20260916/03_historial_simulador.csv`.
- Corrigió `engine.py`: el evento depende de `result_type`, no de que la campaña sea de tráfico. `conversacion_iniciada` y `landing_page_view` usan `results`; `link_click` usa `link_clicks`. Pasaron las 14 pruebas.
- Ejecutó otra vez la propuesta: el contexto de la ganadora tiene 2 anuncios de una campaña; el motor exige 3 anuncios con gasto e impresiones y responde `needs_history`.
- Referencia correcta por anuncio: `120251563209080651`, 84 conversaciones y 966.63 MXN de gasto, CPA 11.5075 MXN. La referencia no es la promoción de junio 8 de un cliente.

## Qué necesito que recuperes

1. **Busca anuncios propios adicionales realmente comparables**, incluidos archivados/pausados y periodos no cubiertos, sin repetir toda la extracción si ya está completa. El contexto exacto está en `entregables/propuesta_agencia_20260916/entrada_motor.json`, campo `context`. Corresponde a tráfico optimizado a conversaciones, México 18–65+, con la atribución y demás campos que allí figuran. Busca al menos un tercer ID real con gasto e impresiones para habilitar escenarios básicos. Reporta también anuncios con cero conversaciones. No inventes nuevos IDs a partir de días o variantes de un mismo anuncio.
2. **Audita las etiquetas que fragmentan públicos.** Verifica si diferencias de formato, orden de listas o etiquetas representan exactamente la misma configuración histórica. Si son equivalentes, entrega evidencia y un mapeo canónico aparte. Si cambió ubicación, edad, intereses, público tibio, expansión u otro ajuste real, conserva la separación. No combines `messages` y `traffic` ni cuentas/clientes para alcanzar el mínimo.
3. **Recupera el texto principal completo del ganador**, título y mensaje inicial desde Ads Manager/publicación/vista previa si el conector no los expone. Entrega evidencia y distingue texto del post del texto impreso en la imagen. Recupera los videos originales/transcripciones de anuncios comparables si están accesibles.
4. **Resuelve si Sanaas promocionaba a la agencia o a un cliente.** La página y el WhatsApp compartidos no bastan para demostrar propiedad de la oferta. Documenta la evidencia; si falta, señálalo sin asumir y deja esas filas separadas como pendientes.

## Dos niveles de suficiencia

- **Escenarios básicos:** mínimo 3 anuncios en el mismo contexto con gasto e impresiones. Alcanzar este mínimo no demuestra que el algoritmo pueda distinguir propuestas.
- **Comparación por texto:** cada campaña de prueba necesita al menos 5 anuncios de otras campañas finalizadas antes de su inicio; el motor requiere al menos 8 anuncios evaluados en al menos 3 campañas de prueba y una reducción de error superior al 5% frente a la base histórica. Son umbrales internos, no una garantía de éxito en Facebook. No basta con 8 anuncios totales ni sirve que todos sean simultáneos.

Si el historial ya está agotado, dilo explícitamente. No hay otra exportación que pueda crear evidencia inexistente. En ese caso entrega el inventario de lo disponible y las carencias; cualquier campaña nueva requerirá una decisión posterior de Carlos sobre presupuesto y publicación.

## Archivos a devolver

En una carpeta nueva, sin sobrescribir tu entrega anterior:

- CSV completo actualizado con el mismo esquema, IDs y granularidad diaria sin duplicados ni solapamientos.
- Exportación original y creativos recuperados, vinculados por ID.
- Tabla de equivalencias de contexto, si las hay, con evidencia y cambios propuestos.
- Resumen de filas/anuncios/campañas por contexto, fechas y faltantes; identifica si apareció el tercer anuncio comparable y si existe historial temporal suficiente.

No incluyas tokens, teléfonos, nombres de prospectos ni datos de clientes ajenos. El cruce de pagos de Nexus sigue siendo útil para medir ventas, pero **no desbloquea** el mínimo de historial publicitario.

## Pendiente de Codex, no de extracción

El motor aún selecciona la referencia por campaña (`benchmark_id`), mientras Carlos confirmó un anuncio particular. Codex debe incorporar o resolver la referencia por anuncio antes de presentar una comparación numérica como si fuera contra los $11.51. No alteres `campaign_id` ni elimines anuncios para forzar esa coincidencia.
