Astra, Carlos añadió mientras trabajabas: **«Modelos 3D bellos, movimientos de cámara»**.
Aplícalo sobre lo que ya hiciste en `CHICA_IMPLANTE_ANIMACION_DIENTES.blend` (mismas reglas: copia con nombre nuevo,
try/finally, viewport SOLID, sin renders Eevee largos, verificación con capturas OpenGL o Cycles local).

## Modelos 3D bellos

- Dientes con forma anatómica real (incisivos centrales/laterales distintos, bordes suaves, ligera translucidez en el borde
  incisal), no bloques. Juntos, con contactos naturales. Exactamente 4 en el corte.
- Raíces cónicas y ligamento sutil; hueso cortical con borde y trabecular poroso con volumen (no un plano con textura).
- Encía con festoneado natural entre dientes, volumen húmedo y borde luminoso cálido como en las imágenes aprobadas.
- Implante con rosca real, tapón, pilar y corona como piezas separadas que se ensamblan en su fase.
- Si el modelo Hunyuan (`modelo_3d_hoja/HOJA_PASO5_hunyuan_LIGERO.glb`) se ve mejor que la geometría procedural, úsalo
  para las tomas de sección cuidando escala, posición del implante y continuidad.

## Movimientos de cámara

- Un solo movimiento continuo y cinematográfico por fase, suave (Bezier con ease in/out), sin cortes bruscos ni saltos.
- Entrada: push-in lento del rostro al hueco (ROSTRO → CLOSEUP).
- Corte: la cámara acompaña la línea cian con un leve travelling lateral mientras se abre la sección y la cara desaparece.
- Preparación / implante: dolly-in hacia el hueso con una pequeña órbita (8–15°) para dar volumen al corte; el implante
  bajando en el eje, siempre legible.
- Integración: órbita lenta que muestra el hueso rodeando el implante; profundidad de campo suave si no pesa en la Mac.
- Corona: pull-back que revela los 4 dientes completos y la corona integrada.
- Sonrisa: regreso al rostro con movimiento suave, cerrando en la sonrisa completa.
- Encuadres 9:16 limpios; nada importante cortado por el borde. Coordina cada movimiento con las frases de la voz
  (`voz_fish/tiempos.json`).

Actualiza `ESTADO_ANIMACION_DIENTES.md` y deja capturas por fase (1, 150, 360, 420, 620, 740, 865, 1000) en
`entregables/implante_dental/capturas_animacion/`. Contesta a Carlos en español.
