# Mejora dental, instrumentos y sticker — 15 septiembre 2026

## Pedido

Mejorar el modelo siguiendo la hoja de Alberto, aumentar la aguja, generar una imagen mejor de la chica y retirar el rostro como un sticker que se despega desde un lado. Carlos pidió además renderizar con su GPU online y entregarle el resultado para mostrarlo a Alberto. No pidió enviárselo directamente a Alberto.

## Archivos

- `CHICA_MEJORADA_v2.png`: nueva imagen de la chica, conservando el hueco dental.
- `CHICA_SONRISA_FINAL.png`: sonrisa restaurada para el cierre.
- `imagen_prompt.txt`: herramienta integrada imagegen y prompts utilizados.
- `SESION_ACTUAL.blend`: respaldo descargado de la Mac antes de modificar.
- `DENTAL_STICKER.blend`: copia local editable para render (Blender 4; no sustituir directamente el archivo de Mac 3.3).
- `mejorar.py`: cambios compatibles con Blender 3.3/4, estado de sesión restaurado en finally, copias de materiales/datos/acciones y rollback ante error.
- `build_local.py` y `verificacion.json`: original conservado, cuatro dientes durante la explicación, voz empaquetada, ausencia de duplicados al repetir.

## Diseño

La aguja aumenta 1.65 veces su longitud y diámetro; se conserva el objetivo en X/Z y se sitúa delante de la lámina fotográfica. La jeringa incorpora apoyos y graduaciones; la fresa, mandril con anillos. Esmalte marfil, encía rosa húmeda, raíces más anchas, porosidad irregular y reflejos de estudio.

El rostro se representa con una lámina fotográfica continua subdividida, adecuada al efecto de sticker solicitado. No es una reconstrucción volumétrica nueva de la cabeza. La lámina se curva desde la derecha y se dobla hacia la izquierda entre cuadros 350–415, mostrando su reverso; después queda solo el modelo dental. La sonrisa restaurada regresa al final. Las deformaciones están guardadas como shape keys: no dependen de handlers ni scripts en reproducción.

## GPU online: bloqueo real

Se encontró la conexión existente de Modal y se usó una Tesla T4 con OptiX verificado para cuatro renders de prueba: `preview_v1/`, registro `preview_v1_gpu.json`. Esos cuadros revelaron fallos visuales, por lo que **no son la entrega final**.

Al intentar cargar la versión corregida, Modal rechazó iniciar la aplicación con:

> Please add a payment method to use T4 GPU functions.

Se avisó a Carlos y se pidió habilitar el método de pago o identificar otra GPU conectada. No se modificó la cuenta ni se contrató otro servicio. Las revisiones posteriores se verifican localmente y se identifican como CPU; no se presentan como render GPU.

## Continuación del render

Después de habilitar Modal:

```bash
python3 -m modal run entregables/implante_dental/mejora_sticker/render_modal.py --mode upload
python3 -m modal run entregables/implante_dental/mejora_sticker/render_modal.py --mode preview --folder preview_final_gpu
# Inspeccionar esos cuadros antes de continuar.
python3 -m modal run entregables/implante_dental/mejora_sticker/render_modal.py --mode final --folder final_v3
python3 entregables/implante_dental/mejora_sticker/montar_video.py final_v3
```

El video configurado tiene 1050 cuadros, 30 fps, 35 segundos, 1080×1920, Cycles 64 muestras con denoising y voz existente. Se usa un volumen privado y un máximo de seis contenedores T4. El montaje rechaza secuencias incompletas. No afirmar que existe el MP4 completo hasta terminar y revisar.

## Aplicado en la Mac

Confirmado por el puente: versión `STICKER_20260915_v3`, guardada en `/Users/juancarlos/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_STICKER_20260915_122252.blend`.
Respaldo inmediatamente previo: `ANTES_APLICAR_STICKER_20260915_122232.blend`, en la misma carpeta.
Se restauró el cuadro 1 que Carlos tenía activo al aplicar; la voz y ambas fotografías están empaquetadas. Evidencia: `resultado_mac.json` y comprobación posterior `verificacion_mac.json`.
La foto frontal usa emisión para evitar sombras de geometría residual y conservar la calidad de la imagen; el reverso del sticker y toda la anatomía/instrumentos usan materiales iluminados. La cámara inicial/final se ajustó a escala 23 para cubrir el encuadre sin franja superior.

Revisión local final: `preview_v3_cpu/frame_0265.png` (aguja) y `preview_v3_cpu/frame_0740.png` (modelo). CPU Cycles 32 muestras, 432×768, sin denoiser disponible en este Blender; tienen ruido y no certifican acabado final. El MP4 GPU sigue pendiente por el bloqueo de facturación de Modal.
