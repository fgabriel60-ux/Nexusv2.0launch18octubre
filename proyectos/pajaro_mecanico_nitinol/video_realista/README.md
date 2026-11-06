# Pájaro mecánico · visualización realista v1

`pajaro_realista_v1.mp4`: 14.88 segundos, 720×1280, H.264 Main/AAC, aproximadamente 4 MB.

Se recuperaron los clips H3 K1–K5 y K3b que Claude terminó de generar antes del bloqueo. `armar_stream.py` los monta con memoria acotada, rótulos de fases y efectos sintéticos propios; `montaje_v1.json` registra cortes y velocidades. Ejecutar `python proyectos/pajaro_mecanico_nitinol/video_realista/armar_stream.py` para reproducir.

Revisión de cuadros al inicio, durante el despliegue, aleteo y reenrollado: muestra una mano lanzando, corredera, varillas, alas de membrana y repliegue a una bola. Se eligió K3b para un aleteo más visible.

**Límites:** es una visualización de IA, no una simulación mecánica validada. Algunas piezas cambian de forma o tamaño, el vuelo se mantiene suspendido sin física real y el repliegue interpreta el nitinol como una espiral. No se comprobó que la secuencia reproduzca doce aleteos ni la fase exacta de los surcos helicoidales. El modelo técnico original en la carpeta superior es la referencia del mecanismo.

No se generaron clips nuevos para esta versión; se reutilizó el trabajo ya pagado de Claude.
