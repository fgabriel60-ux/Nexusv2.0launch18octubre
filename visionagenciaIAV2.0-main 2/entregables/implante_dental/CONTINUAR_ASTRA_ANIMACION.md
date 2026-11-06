Astra, soy Claude. Tu tarea anterior **se cortó por falta de memoria** (el Codespace tiene 8 GB sin swap; VS Code, Codex y
Claude ocupan ~4 GB). Se cayó justo cuando lanzaste `blender -b SESION_ANTES.blend -t 6 --python probar_local.py`: el log
`/tmp/animacion_dientes_local.log` quedó vacío y no quedó ningún proceso vivo.

## Cómo quedó todo (verificado)

- Mac: escena `CHICA_IMPLANTE_ESTILO_APROBADO`, cuadro 560, SOLID, **sin cambios pendientes**, 101 objetos. Tu respaldo
  `~/Desktop/IMPLANTE_DENTAL/ANTES_ANIMACION_DIENTES_20260914_230459_3cfefe.blend` existe. No se aplicó la animación en la Mac.
- Local `entregables/implante_dental/animacion_dientes/`: `SESION_ANTES.blend`, `inventario_antes.json`,
  `aplicar_animacion.py` (DIENTES_20260915_v1) y `probar_local.py`. No existe `ANIMACION_LOCAL_VERIFICADA.blend` ni renders.

## Continúa desde ahí, con límites de memoria

- Blender local siempre con `nice -n 10 blender -b … -t 2`, un solo proceso a la vez, nunca en paralelo con otro render.
- Verificación local ligera: resolución 20–25 %, Cycles 8–12 muestras, máximo 5 cuadros por corrida; si hace falta más,
  varias corridas cortas.
- Revisa `free -m` antes de lanzar Blender; si hay menos de 2.5 GB disponibles, no lo lances y usa capturas OpenGL del
  viewport de la Mac (sin MATERIAL/RENDERED).
- Todas las demás reglas de `INSTRUCCION_ASTRA_ANIMACION_DIENTES.md` siguen vigentes.

## Además, lo que añadió Carlos: «Modelos 3D bellos, movimientos de cámara»

Incorpóralo en esta misma pasada; el detalle está en `SEGUIMIENTO_ASTRA_CAMARA_MODELOS.md` (dientes con forma anatómica y
juntos, 4 en el corte; hueso con volumen; encía festoneada con borde luminoso; implante, tapón, pilar y corona separados;
un movimiento de cámara continuo y suave por fase coordinado con la voz; capturas por fase en `capturas_animacion/`).

Al terminar: aplica en la Mac solo si la verificación local pasó, guarda la copia `CHICA_IMPLANTE_ANIMACION_DIENTES.blend`,
documenta en `ESTADO_ANIMACION_DIENTES.md` y contesta a Carlos en español.
