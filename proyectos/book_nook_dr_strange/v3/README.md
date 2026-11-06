# Sanctum Sanctorum · book nook v3

Continuación del diseño que Claude dejó incompleto el 25 de octubre de 2026.
Caja de **170 × 200 × 240 mm**, MDF nominal de **3 mm**, kerf configurado **0.12 mm**.
32 piezas distintas distribuidas en **3 hojas de 600 × 400 mm**.

La v3 cambia la fachada de la v2 por el interior de la referencia de Harsh Verma: bóveda con cinco costillas escalonadas y grecas, ventana circular de cuatro capas con barras curvas, tarima con escalones y baranda delantera izquierda. Los detalles finos se simplifican para corte láser.

## Archivos

- `generar_booknook_v3.py`: generador completo y reproducible.
- `hoja_1_corte.svg` a `hoja_3_corte.svg`, y sus DXF: CORTE rojo, GRABADO azul, ETIQUETAS verde. No cortar la capa de etiquetas.
- `vista_frontal.png`, `vista_completa.png`: vistas calculadas directamente del diseño. La vista completa transparenta paredes para enseñar el interior.
- `vista_realista_frontal.png`, `vista_realista_tres_cuartos.png`, `detalle_ventana.png`: visualizaciones generadas con IA a partir del diseño. Representan materiales e iluminación; no son fotografías de una pieza fabricada ni planos dimensionales.

## Verificación

`python proyectos/book_nook_dr_strange/v3/generar_booknook_v3.py` termina en **OK**: geometrías conectadas y válidas, sin interferencias detectadas, comprobación de puentes de 2 mm y separación mínima de 2 mm en las hojas. Se corrigieron cuatro choques entre nervios y costillas, puentes residuales y el margen vertical del anidado.

Son comprobaciones geométricas digitales: no sustituyen una prueba física de encastre con el MDF y láser concretos. Medir el espesor real y ajustar T y KERF antes del corte final.

Montaje: caja y cámara de cableado inferior, piso, tarima/escalones, capas de ventana al fondo, costillas y proscenio, baranda y tapas. Papel difusor detrás del vitral; LED cálido en la cámara trasera y superior. Pegar las piezas decorativas según las vistas; mantener acceso a la alimentación por la tapa trasera.

## Fidelidad visual

Conserva la composición principal, barras de la ventana, bóveda y baranda de la referencia. No reproduce exactamente todas las ornamentaciones del escenario original. Las imágenes IA interpretan el acabado, el relieve y la colocación de la luz; usar SVG/DXF como fuente de fabricación.
