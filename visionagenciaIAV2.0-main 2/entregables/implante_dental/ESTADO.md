# Implante dental — 2026-09-14

Construido por el puente HTTP en Blender 3.3.1 de la Mac. Escena `IMPLANTE_DENTAL_CINEMA`, 1050 cuadros a 30 fps (35 segundos), 1080 × 1920, Eevee. Materiales, cámara, herramientas, implante helicoidal, integración esquemática, pilar y corona animados. Fotografías de referencia empaquetadas para entrada/salida. Modelo educativo procedural; no es una reconstrucción anatómica exacta de la paciente.

Archivo Mac: `/Users/juancarlos/Desktop/IMPLANTE_DENTAL/IMPLANTE_DENTAL_CINEMA.blend`.

Fuentes: `construir.py` (recibe diccionario ASSETS con JPEG base64), `ajustar_seccion.py` (ajuste aplicado al corte). La construcción original preserva la escena anterior; por petición posterior del usuario se activa la escena dental y se guarda el archivo en la Mac.

No hay render completo de video ni voz. Las referencias de antes y después tienen encuadres diferentes: transición editorial, no reconstrucción 3D del rostro.

Confirmado: archivo abierto en la Mac, escena dental activa, frame 580, vista de cámara con materiales. Copia del blend descargada aquí. La primera prueba de render mostró el cuadro inicial por el contexto de escena del operador; PREVIEW_580.png corresponde en realidad al inicio y no certifica el cuadro 580. No se ha validado visualmente el macro anatómico renderizado.
