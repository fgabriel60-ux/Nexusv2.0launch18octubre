# Manuel · Fotografía de eventos — estrategia de audiencias en Meta

Fuente: texto que Carlos pegó el 16 oct 2026, generado por Meta AI. Se guarda tal cual; las notas de verificación al final son mías y no vienen de Meta.

## Estructura recomendada

### 1. Audiencia principal · Quinceañeras (decisores: padres)
- **Ubicación:** radio alrededor de la ciudad base y donde entrega servicio.
- **Edad:** 35–55 (padres). Para alcance complementario, 13–15 si se usa Advantage+ Audience.
- **Intereses:** Quinceañera, Fiesta de quince años, Vestidos de quinceañera, Organización de eventos, Salones de fiestas, Banquetes, Fotografía (interés amplio).
- **Comportamientos:** Padres con hijos adolescentes (si está disponible en la región); "Aniversarios próximos".

### 2. Audiencia principal · Bodas
- **Edad:** 22–40.
- **Estado civil:** Comprometido, En una relación.
- **Intereses:** Boda, Planificación de bodas, Vestidos de novia, Luna de miel, Wedding planner, Banquetes para bodas, Anillos de compromiso, Fotografía de boda.
- **Comportamientos:** Comprometidos (6–12 meses), Nuevamente comprometidos.

### 3. Audiencia amplia · Todo tipo de eventos
- **Intereses:** Eventos sociales, Cumpleaños, Bautizo, Graduación, Fotografía profesional, Fotografía de eventos, Decoración de fiestas.
- Ad set de prueba con Advantage+ Audience activado, para que el sistema encuentre conversiones fuera de intereses fijos.

## Configuración
- 1 campaña con objetivo Interacción, Mensajes o Clientes potenciales según cómo cierre ventas (WhatsApp ideal para este nicho).
- 3 ad sets separados: Quinceañeras, Bodas, Eventos generales. No mezclar intereses de boda y XV en el mismo ad set.
- En cada ad set: Ubicación → Edad → Segmentación detallada, intereses con "Coincidir con al menos uno".
- Advantage+ Audience activado.
- Ubicaciones: Feed de Facebook e Instagram + Stories/Reels (Reels y Stories funcionan bien para portafolio).

## Paquetes
- No segmentar por paquete. Segmentar por tipo de evento (XV vs Boda) y dejar que el cliente elija paquete en la conversación de WhatsApp/Messenger.
- Retargeting: ad set adicional con público personalizado de quienes interactuaron con su Instagram/Facebook o vieron su video en los últimos 30 días.

## Presupuesto y prueba
- $100–150 MXN diarios por ad set, 5–7 días, conservar solo el ad set con menor costo por conversación iniciada.

---

## Notas de verificación (de Claude, 16 oct 2026)
- **IDs de intereses:** el texto da nombres, no IDs. Meta AI ya dio IDs inexistentes o descontinuados en el caso de Guillermo (herrería): los intereses y comportamientos se deben buscar y validar en Ads Manager (Público → Segmentación detallada) antes de usarlos. Un comportamiento como "Recién mudados" ya no estaba disponible; "Comprometidos" y "Padres con hijos adolescentes" pueden estar igual.
- **Edad 13–15:** Meta no permite segmentar anuncios a menores con estos fines y los conjuntos con Advantage+ no dejan fijar una edad mínima superior a 25 ni una máxima inferior a 65 (solo como sugerencia). Por API se usa `age_min` 25, `age_max` 65 y `age_range` como sugerencia. Para esta campaña conviene fijar la edad como sugerencia y no a menores.
- **Estado civil** como segmentación detallada ya no está disponible en varias cuentas; confirmar en la interfaz.
- Cuenta publicitaria, página y WhatsApp de Manuel: aún sin definir. Pendiente conectar en Windsor y confirmar moneda (la cuenta de Guillermo "baez" estaba en USD y la "Bez" en MXN: revisar antes de poner presupuestos).
- Windsor no puede crear conjuntos con destino WhatsApp salvo que el número esté vinculado a la página y a la cuenta (caso 21058369 con soporte de Windsor).
