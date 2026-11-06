# Flyers de Mariano animados con end frame — 15 y 16 septiembre 2026

Mariano mandó 6 flyers el 12 de septiembre. Los 6 quedaron animados con el método que usó Astra en el flyer 1: el clip
abre con la foto sin texto y termina EXACTAMENTE en el flyer original, así el último cuadro sirve tal cual para publicar.

## Método (dos pasos por flyer)

1. `python3 quitar_texto.py N` → `fondo_flyer_N.png`. GPT Image 2 borra textos, precios, logos e íconos y reconstruye
   lo que iba detrás (cielo, mar, cerros, calle).
2. `python3 kling_flyer_endframe.py N` → `kwaivgi/kling-v2.6-pro/image-to-video` con `image` = fondo sin texto y
   `end_image` = flyer original, 5 s, `sound: false`; después SFX con `mirelo-ai/sfx-1.6/video-to-video`.
   Los jobs quedan guardados (`kling_flyerN_job.json`, `sfx_flyerN_job.json`): si se vuelve a correr, retoma y no
   vuelve a pagar.

## Sonido: uno por flyer (Carlos, 16 sep: «mejores sonidos»)

Antes había un solo audio genérico. Ahora cada flyer tiene su diseño sonoro en capas, con los acentos a tiempo con lo
que aparece en pantalla, y en todos: sin música, sin voz.

- **2** costa: oleaje y viento, whoosh al asentarse, tres swishes al entrar cada panel, brillo en el barrido de luz.
- **3** fiesta: papel picado ondeando, estallidos de confeti, clics de madera al caer las cartas de lotería, gente y
  niños a lo lejos, shaker suave y golpe cálido final.
- **4** aéreo: viento de altura, tres whooshes al apilarse las fotos, ticks en los íconos, sub profundo al cierre.
- **5** vista abierta: viento costero, movimiento de tela y manos, subida aérea en el precio, golpe limpio final.
- **6** atardecer: olas lentas y viento cálido, whoosh al titular, cuatro toques redondos en las tarjetas de beneficios.

El flyer 1 es de Astra y se generó antes de este cambio, con el sonido genérico.

## Entregado (los 6)

| Flyer | Tema | Archivo con sonido | Kling |
|---|---|---|---|
| 1 | Familia caminando | `FLYER_5S_TEXTO_ANIMADO_CON_SFX.mp4` (Astra) | $0.35 |
| 2 | 3 formas de vivir | `FLYER2_5S_TEXTO_ANIMADO_CON_SFX.mp4` | $0.35 |
| 3 | Tarde Mexicana | `FLYER3_5S_TEXTO_ANIMADO_CON_SFX.mp4` | $0.35 |
| 4 | Últimos lotes | `FLYER4_5S_TEXTO_ANIMADO_CON_SFX.mp4` | $0.35 |
| 5 | El mar pone la vista | `FLYER5_5S_TEXTO_ANIMADO_CON_SFX.mp4` | $0.35 |
| 6 | Lotes en zona costa | `FLYER6_5S_TEXTO_ANIMADO_CON_SFX.mp4` | $0.35 |

De cada uno hay también la versión sin audio (`..._SIN_AUDIO.mp4`) y su `ULTIMO_CUADRO_FLYERN.png` para comparar
contra el original. Todos duran 5 s. Los 5 que hizo Claude (2 al 6) costaron $1.75 USD de Kling más las pasadas de SFX.

## Revisión

En los 6 el texto sale legible y el último cuadro coincide con el flyer original: títulos, precios, íconos, fechas y
pies de página. No hubo palabras inventadas ni letras deformadas. La falta de ortografía de «*APLICAN RESTRICIONES»
viene de los flyers originales de la desarrolladora, no de Kling.

Detalle del flyer 4: en el original la mitad izquierda es un panel azul liso que solo lleva texto, así que su fondo sin
texto queda casi vacío de ese lado y Kling tiene poco que mover ahí. El resultado igual cierra bien porque el último
cuadro es el flyer exacto.

## Audio corregido (16 sep)

El flyer 1 (de Astra) y el 2 se habían generado con el sonido genérico, y Carlos pidió además «en la mexicana un mejor
sonido». Se rehízo SOLO el audio de los tres con `rehacer_audio.py`, sin volver a generar video: $0.01 cada uno.

- **1** se le escribió su propio sonido: pasos en el asfalto, brisa con oleaje lejano, el collar del perro, niños a lo
  lejos y cierre cálido.
- **2** pasó al sonido de costa por capas (swishes al entrar cada panel).
- **3** quedó más rico: papel picado en estéreo, dos estallidos de confeti, cartas que se azotan y una barajeada,
  shaker de barro, **un rasgueo de guitarra** al caer el título, destello de triángulo en la fecha, gente y niños de
  fondo y golpe redondo final. Sigue sin música de fondo ni voces.

Salen como `FLYER1/2/3_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4`. Los archivos viejos NO se borraron.
**Para publicar se usan: v2 en el 1, 2 y 3, y `..._CON_SFX.mp4` en el 4, 5 y 6.**

## Envío a Mariano

`enviar_a_mariano.py` manda a `27337584279694@lid` un mensaje corto y luego los 6 clips numerados, uno por uno con
45 a 90 s de pausa. Antes de mandar revisa que los 6 existan y traigan audio; si falta uno, no manda nada. Lleva
recibo en `recibos_mariano.json`, así que si se corta y se vuelve a correr, no le repite ninguno.
**Enviado el 16 sep**: mensaje de presentación y los 6 clips, los 7 envíos con status `success`, ninguno falló.
Evidencia: `envio_mariano.log` y `recibos_mariano.json`.
