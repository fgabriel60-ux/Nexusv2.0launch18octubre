# Flyer 2 de Mariano animado con end frame — 15 septiembre 2026

Mismo método que usó Astra en el flyer 1 (Carlos: «haz el siguiente flyer como lo hizo Astra el último con end frame»).

## Cómo se hizo

1. `quitar_texto.py 2` → `fondo_flyer_2.png`: GPT Image 2 borra textos, precios, logos e íconos y reconstruye el
   cielo y el paisaje detrás. Quedan las tres fotos de casas en la composición diagonal.
2. `kling_flyer_endframe.py 2` → `kwaivgi/kling-v2.6-pro/image-to-video` con `image` = fondo sin texto y
   `end_image` = `flyer_2.jpg`, 5 s, `sound: false`. El texto y los logos entran animados y el último cuadro es el
   flyer exacto, listo para publicar.
3. SFX con `mirelo-ai/sfx-1.6/video-to-video`: viento costero, whoosh suave y golpe bajo al asentarse. Sin música ni voz.

## Entrega

- `FLYER2_5S_TEXTO_ANIMADO_CON_SFX.mp4` (5.0 s, con audio) — el que se manda.
- `FLYER2_5S_TEXTO_ANIMADO_SIN_AUDIO.mp4` (5.08 s) — por si se quiere otro diseño sonoro.
- `ULTIMO_CUADRO_FLYER2.png` y `REVISION_FLYER2.jpg` — revisión del texto.
- Jobs reanudables: `kling_flyer2_job.json`, `sfx_flyer2_job.json`. Si se vuelve a correr el script, retoma y no
  vuelve a pagar la generación.

## Revisión

El último cuadro queda igual al original: escudo, RESIDENCIAL SAN MARINO, «3 formas / de vivir en San Marino»,
DESDE $3.8MDP*, «Diferentes espacios, misma calidad de vida.» y el pie de Grupo Lagsa. Sin letras deformadas ni
palabras inventadas. La falta de ortografía de «*APLICAN RESTRICIONES» viene del flyer original de la desarrolladora.

## Costo

$0.35 USD el clip de Kling, más la pasada de SFX. Faltan los flyers 3, 4, 5 y 6; cada uno necesita primero su
`fondo_flyer_N.png` con `quitar_texto.py N` y luego `kling_flyer_endframe.py N` (los prompts de cada uno ya están
escritos en ese script).
