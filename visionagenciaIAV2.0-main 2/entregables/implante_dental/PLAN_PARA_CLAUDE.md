# Continuar: chica 3D y close-up del implante según la hoja aprobada

## Pedido actual

Carlos quiere trabajar sobre un modelo 3D con texturas que reproduzca el estilo de la hoja enviada a Alberto. Debe reconocerse que el close-up pertenece a la misma chica. Última instrucción: **dejar el plan y detener la producción para ahorrar uso**. Este documento es el relevo; no implica que la nueva versión ya esté aprobada o instalada en la Mac.

## Dirección artística

Referencia principal:
`visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/clientes/Vision Agencia/veneers_dental/hoja_proceso_implante/hoja_proceso_implante.png`

Rostro original:
`visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/clientes/Vision Agencia/veneers_dental/last_frame_diente_faltante.png`

Conservar piel y labios reconocibles durante el macro, fondo oscuro, iluminación cálida/turquesa, corte diagonal de borde cian discreto, hueso poroso marfil, encía rosa y titanio satinado. La hoja tiene inconsistencias anatómicas: conservar su estética, no sus errores. El diente faltante está en la arcada superior; el implante entra hacia arriba al maxilar.

## Qué existe realmente

### En la Mac

Blender 3.3.1 conectado por el puente HTTP. Archivo abierto y guardado:
`/Users/juancarlos/Desktop/IMPLANTE_DENTAL/IMPLANTE_DENTAL_CINEMA.blend`

Escena `IMPLANTE_DENTAL_CINEMA`, 120 objetos, 1050 cuadros a 30 fps (35 s), Eevee. Tiene implante helicoidal, dientes, hueso, encía, jeringa, herramienta, pilar/corona, cámara y visibilidades animadas. La versión inicial usaba imágenes planas de la chica al comienzo/final y una maqueta dental separada durante el proceso.

Carlos reportó que se trababa: quedó **viewport SOLID**, sin subdivisión de trabajo, con detalle conservado para render. No volver a activar MATERIAL/RENDERED automáticamente. Esa activación llegó a bloquear el puente unos cinco minutos. No hay video completo renderizado.

**La nueva versión de rostro aún NO se envió ni se abrió en la Mac.** La última inspección remota al comenzar esta tarea encontró la escena anterior en cuadro 1004. No asumir que sigue ahí: Carlos puede estar trabajando.

### Aquí, carpeta `entregables/implante_dental/`

- `IMPLANTE_DENTAL_CINEMA.blend`: copia descargada de la maqueta inicial; anterior al último ajuste de viewport ligero.
- `crear_closeup.py`: construcción de la nueva escena `CHICA_IMPLANTE_ESTILO_APROBADO`, compatible por intención con Blender 3.3 y 4.0; se ejecutó localmente en 4.0.2. Duplica objetos/datos/materiales de la escena anterior, añade rostro y corte, conserva la escena fuente.
- `CHICA_IMPLANTE_ESTILO_APROBADO.blend`: construcción local editable, guardada en Blender **4.0.2**. No abrir directamente este archivo en la Mac con 3.3.1; construir allí con el script o realizar una conversión compatible comprobada.
- `ROSTRO_PRUEBA_200.png`, `ROSTRO_PRUEBA_620.png`: renders de trabajo. Ambos corresponden ya a la segunda revisión: renderizados el 14 de septiembre, a las 22:50 y 22:51 UTC.
- `construir.py`, `ajustar_seccion.py`: fuentes de la primera maqueta; no volver a ejecutar por defecto.
- `extraer_rostro.py`, `preparar_malla.py`: extracción/adaptación de la cara y exportación de OBJ/UV.

### Assets persistentes en `rostro_assets/`

- `CHICA_ROSTRO.obj`, `CHICA_ROSTRO.mtl`: superficie facial 3D reutilizable, con UV.
- `CHICA_ALBEDO.png`: copia de la fotografía original, usada como textura. Contiene iluminación fotográfica; no es un albedo neutralizado.
- `face_mesh.json`: vértices, caras, UV y malla de contexto de cabello/cuello; es la entrada final del constructor. No requiere MediaPipe para construir en Blender.
- `landmarks.json`: 478 puntos detectados; se usan 468 para la malla canónica.
- `canonical_face_model.obj`, `LICENSE_MEDIAPIPE.txt`, `FUENTES.md`: base, licencia y procedencia.

La cara tiene 468 vértices y 880 triángulos antes de subdividir. Se retiraron 18 triángulos de la boca para crear una apertura real y poder insertar dientes detrás de los labios. El corte diagonal usa geometría seccionada, no una imagen plana superpuesta.

**Alcance honesto:** es una superficie facial ajustada desde una fotografía, con contexto fotográfico independiente de cabello/cuello. No es un escaneo completo de cabeza, una reconstrucción multivista ni un cuerpo riggeado. Limitar órbitas a unos pocos grados; el parecido está pensado para el close-up de referencia.

## Estado de la verificación

La primera prueba local de la nueva escena se vio: la nariz, piel y labios conservan el aspecto de la chica y hay profundidad facial. Se detectaron tres problemas:
1. Encía demasiado recta, con papilas que parecían bolitas.
2. El corte diagonal ocultaba buena parte del implante.
3. La luz saturaba los dientes hacia blanco/cian y la sección parecía demasiado rectangular.

La segunda revisión de `crear_closeup.py` ya incorpora:
- Encía continua con contorno ondulado por diente y acceso para el implante, retirando barra y papilas esféricas anteriores.
- Corte desplazado a `x - 0.18*z = -1.2`, dejando visible el tornillo.
- Maxilar de contorno superior curvo y capa cortical/trabecular separada, con canal abierto.
- Potencias de luces reducidas y encuadre macro algo más abierto.
- Variaciones pequeñas de anchura y borde de dientes vecinos.

**Falta inspeccionar y validar visualmente esa segunda revisión.** No dar por aprobada solo porque el script termina. Los renders locales son de baja resolución y 12 muestras; el ruido no es la calidad final prevista.

## Próximos pasos, en orden

1. Leer este documento y mirar la hoja aprobada, la foto original y las dos últimas pruebas.
2. La segunda prueba **ya terminó correctamente**: `/tmp/dental_closeup_v2.log` confirma guardado del blend, 100 objetos y ambos renders. No repetir la construcción antes de mirar las imágenes existentes.
3. Abrir la copia local nueva y verificar cuadros 200 y 620: rostro reconocible, encía integrada bajo el labio, hueco en la posición correcta, tornillo visible completo dentro del hueso, sin dobles dientes ni penetraciones. Verificar también 1, 420, 740, 865 y 1000 para comprobar visibilidad de fases y encuadres. No hace falta renderizar toda la animación para ello.
4. Corregir solo lo que esas imágenes revelen. Prioridad: integración anatómica y semejanza con la hoja, no añadir efectos ni nuevas cámaras innecesarias. Mejorar dientes si siguen pareciendo una fila uniforme de bloques.
5. Una vez validado, ejecutar `crear_closeup.py` por el puente en la Mac, con los datos e imagen incluidos en el payload. Mantener la escena anterior intacta y guardar el nuevo archivo con nombre distinto.
6. Confirmar guardado y objetos/texturas empaquetados. Mostrar la nueva escena solo al terminar y conservar viewport SOLID; se puede preparar una imagen renderizada para ver el estilo sin dejar Eevee calculando permanentemente.
7. Entregar el `.blend` compatible de la Mac y una vista de close-up validada. No afirmar que el video completo está renderizado.

## Cómo ejecutar el constructor sin rehacer extracción

Variables que deben existir antes de `exec(codigo_de_crear_closeup)`:

```python
FACE_DATA = ... # JSON de rostro_assets/face_mesh.json
PHOTO_PATH = ... # ruta LOCAL a Blender de la foto
LOCAL = False   # remoto: libraries.write y responder; restaura escena original
OUT_BLEND = '/Users/juancarlos/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_ESTILO_APROBADO.blend'
```

En remoto, enviar la foto como base64 y escribirla en una ruta temporal de la Mac, cargarla y empaquetarla. No hay archivos compartidos Codespace/Mac. El constructor espera que exista `IMPLANTE_DENTAL_CINEMA` y sus objetos originales `DI_*`; inspeccionar nombres antes. No ejecutar dos veces sin controlar los nombres: Blender crea sufijos `.001`.

Puente:
`POST https://conectorblender.onrender.com/api/blender/execute`
con `{"python": codigo, "meta": {"tipo": "libre"}}`.

Helper temporal existente: `/tmp/catania_realismo/bridge.py SCRIPT RESPUESTA_JSON`. No depende del archivo de Blender y evita imprimir base64 grande. Si falta, recrearlo según AGENTS.md.

Leer `AGENTS.md` y respetar la sesión viva: preservar estado, `try/except/finally`, prueba aislada, guardar por separado. Para renders remotos, **activar temporalmente `bpy.context.window.scene = escena_objetivo` antes de `frame_set()` y renderizar**, restaurando después. Un render con solo `scene=nombre` mientras otra escena era activa terminó dibujando el cuadro 1 aunque se había solicitado el 580.

## Entorno local de prueba

Blender `/usr/bin/blender` = 4.0.2. Cycles CPU funciona con `scene.cycles.use_denoising=False`; esta compilación no incluye OpenImageDenoiser. Prueba aislada del cubo pasó. No activar denoise sin comprobar disponibilidad.

Runner temporal: `/tmp/dental_run_closeup.py`. Carga los datos, ejecuta constructor con `LOCAL=True`, guarda el blend con Eevee, luego cambia solo la sesión de prueba a Cycles, 12 muestras, 35% de resolución y renderiza 200/620. Logs `/tmp/dental_closeup.log` y `/tmp/dental_closeup_v2.log`.

Si hay que repetir landmarks: entorno `/tmp/dental_face_env`, modelo `/tmp/face_landmarker.task`; requiere `LD_LIBRARY_PATH=/tmp/dental_graphics/usr/lib/x86_64-linux-gnu` y `MPLCONFIGDIR=/tmp/dental_mpl`. No hace falta instalar nada de esto en la Mac: los JSON y la foto ya son suficientes.
