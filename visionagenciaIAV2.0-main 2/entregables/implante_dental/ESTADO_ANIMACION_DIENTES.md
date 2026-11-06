# Animación dental — aplicada y guardada en la Mac

Fecha: 15 septiembre 2026. Versión `DIENTES_20260915_v3`.

## Entrega

- Copia guardada: `/Users/juancarlos/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_ANIMACION_DIENTES.blend` (4 640 264 bytes).
- Sesión viva: `CHICA_IMPLANTE_ESTILO_APROBADO`, cuadro 620, viewport SOLID, 113 objetos. El nombre del archivo abierto sigue siendo el original porque el guardado solicitado fue `copy=True`.
- Respaldo previo: `ANTES_ANIMACION_DIENTES_20260914_230459_3cfefe.blend`, en la misma carpeta del escritorio.
- Voz `VOZ_FISH_IMPLANTE`, canal 1, cuadros 1–1047, conservada y empaquetada. Duración de escena: 1050 cuadros a 30 fps.
- La escena `IMPLANTE_DENTAL_CINEMA` conserva su inventario, geometrías referenciadas, poses y acciones según comparación antes/después.

## Cambios

Cuatro coronas naturales reconstruidas con superficie convexa, bordes incisales redondeados, cuello más estrecho y laterales diferenciados. Contactos próximos; cuatro raíces cónicas con ápices curvados y ligamentos separados. Encía de sección recortada a esos cuatro dientes; los dientes distales solo aparecen con el rostro.

Se conserva el maxilar volumétrico y sus materiales del estilo aprobado. Se añadió una red de trabéculas geométricas, borde cortical fino y una luz frontal amplia de 300 W para ayudar a leer raíces y esmalte durante la órbita. Se conservaron el fondo turquesa, la encía rosa, las texturas y las luces de estilo existentes. No se incorporó Hunyuan: la geometría articulada permite controlar las piezas y el número de dientes.

| Fase | Animación |
| --- | --- |
| 1–150 | Acercamiento continuo del rostro al hueco. |
| 200–347 | Jeringa se aproxima a la encía, avanza el émbolo y se retira. |
| 350–415 | Barrido geométrico diagonal de la cara; línea cian viaja hacia la orilla y desaparece. |
| 420–565 | Fresa gira y asciende; el relleno de hueso se retrae para revelar el canal. |
| 620–704 | Implante gira y asciende por su eje, con la punta hacia el maxilar. En 620 comienza la entrada: todavía se ve debajo de la encía. |
| 722–878 | Tapón entra y permanece durante la integración; se retira antes del pilar. |
| 740–860 | Crecimiento de integración anclado al hueso y texto «MESES DE CICATRIZACIÓN». Órbita suave. |
| 880–914 | Pilar se coloca por separado. |
| 923–977 | Corona asciende y se asienta. La quinta corona corresponde al diente reemplazado. |
| 981–1050 | Regreso al rostro y alejamiento para la sonrisa, conforme al seguimiento de Carlos. La línea cian no regresa. |

Cámara ortográfica vertical animada con curvas Bezier y manejadores AUTO_CLAMPED: acercamiento, desplazamiento lateral, órbitas moderadas y retirada final. Profundidad de campo desactivada para mantener las piezas legibles y reducir coste.

## Verificación

- Prueba aislada del barrido con copia temporal de la cara: 880, 645 y 0 polígonos en tres posiciones; sin modificar la escena principal.
- Blender local: una instancia, `nice -n 10`, dos hilos, memoria disponible comprobada >2.5 GB. Sin nuevos fallos de memoria.
- Comprobaciones locales de visibilidad en 18 cuadros: cuatro dientes y cuatro raíces durante el corte, sin cara, línea ni dientes distales; secuencia de implante, tapón y corona; voz empaquetada. Resultado: `animacion_dientes/verificacion_local.json`.
- Capturas Cycles a 25 % (270×480), 12 muestras, máximo cinco cuadros por corrida. Archivos en `capturas_animacion/`: 1, 150, 360, 420, 620, 704, 740, 865, 950 y 1000.
- Las previsualizaciones locales ajustan el peso SSS convertido por Blender 4 para reducir ruido. Ese ajuste es exclusivamente de previsualización, no se aplica a los materiales de la Mac 3.3.1; por ello no certifican igualdad exacta de color entre versiones.
- Aplicación real en Mac confirmada por el puente. Segunda ejecución sin duplicados. Verificación real en 420, 620, 704, 740, 865 y 950: cuatro dientes naturales, cuatro raíces, sin cara ni línea. Voz empaquetada y copia guardada confirmadas. Evidencia: `animacion_dientes/resultado_mac.json`.

## Capturas

[Close-up](capturas_animacion/FASE_0150.png) · [Transición](capturas_animacion/FASE_0360.png) · [Preparación](capturas_animacion/FASE_0420.png) · [Entrada del implante](capturas_animacion/FASE_0620.png) · [Integración](capturas_animacion/FASE_0740.png) · [Corona en movimiento](capturas_animacion/FASE_0950.png) · [Sonrisa](capturas_animacion/FASE_1000.png).

## Limitaciones pendientes

- Eevee de la Mac sigue sin diagnóstico resuelto: no se lanzó ningún render Eevee ni se activó MATERIAL/RENDERED. Se conserva el motor existente.
- Las capturas tienen ruido apreciable por el límite de 12 muestras; no son un render final ni certificación de acabado equivalente a las imágenes GPT aprobadas. Falta render completo y revisión audiovisual del vídeo final.
- El rostro existente es una superficie fotográfica con geometría limitada. En las capturas se aprecia una unión en la frente y la integración labios/dientes requiere pulido para una entrega final; no se reconstruyó la cabeza completa.
- La legibilidad y el acabado de las raíces, el borde del hueso y la encía requieren revisión con render final de mayor calidad. No se presenta esta previsualización como fotorrealismo terminado.

Código aplicado: `animacion_dientes/aplicar_animacion.py`. Copia local de pruebas: `animacion_dientes/ANIMACION_LOCAL_VERIFICADA.blend` (Blender 4; no abrir directamente en Mac 3.3: usar la copia guardada allí).

Captura adicional real de la Mac: [SOLID cuadro 620](capturas_animacion/MAC_SOLID_0620.png), obtenida con OpenGL y restauración de los ajustes temporales. Sirve para verificar geometría y encuadre; SOLID no muestra el acabado de materiales.


## 2026-09-15 · Mejora posterior: instrumentos, nueva chica y sticker

Aplicado en la Mac y guardado como `~/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_STICKER_20260915_122252.blend` (versión `STICKER_20260915_v3`). Respaldo previo `ANTES_APLICAR_STICKER_20260915_122232.blend`.

Aguja 1.65× de largo/diámetro, cuerpo de jeringa más legible, apoyos y graduaciones, mandril de fresa. Nuevos materiales de esmalte/encía/raíces/metal y luces de reflejo. Fotografías nuevas de inicio y sonrisa final empaquetadas. El barrido plano se sustituye por una lámina fotográfica continua que se curva desde un lado entre 350–415 con reverso visible; sin línea cian. Los dientes 3D se revelan durante la transición y la sonrisa fotográfica restaurada vuelve en 998. Se conserva la voz y se restaura el cuadro activo del usuario (1 al aplicar).

Carlos pidió render GPU para Alberto. Modal/T4/OptiX produjo cuatro pruebas iniciales; al intentar actualizar la versión corregida bloqueó nuevas funciones con «Please add a payment method to use T4 GPU functions». Avisado al usuario. No hay MP4 final. Revisiones posteriores locales CPU: se identifican como tales y conservan ruido. Detalles, código, imágenes y comprobaciones: [mejora_sticker/ESTADO.md](mejora_sticker/ESTADO.md).
