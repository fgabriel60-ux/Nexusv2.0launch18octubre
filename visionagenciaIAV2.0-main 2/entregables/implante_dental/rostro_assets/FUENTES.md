# Procedencia y alcance

- Malla facial canónica: Google MediaPipe, https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model.obj (Apache 2.0; licencia adjunta).
- Ajuste facial: MediaPipe Face Landmarker, https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python . Pesos oficiales: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task .
- Textura: fotografía proporcionada en el proyecto `last_frame_diente_faltante.png`; no se sustituyó por una persona de stock.
- Referencia estética: `hoja_proceso_implante/hoja_proceso_implante.png`.

Modificaciones: vértices adaptados a 468 puntos detectados en la fotografía, coordenadas UV proyectadas, apertura geométrica de la boca (18 triángulos retirados), corte diagonal, materiales y modelo dental propios. El archivo OBJ permite reutilizar la cara fuera de Blender.

Es una superficie facial 3D ajustada desde una vista, con contexto fotográfico independiente de cabello/cuello. No es un escaneo de cabeza completa ni un cuerpo riggeado. La textura conserva parte de la iluminación de la fotografía; mantener órbitas pequeñas en los planos destinados a conservar parecido. El modelo dental es una visualización educativa aproximada, no una planificación clínica de esa persona.
