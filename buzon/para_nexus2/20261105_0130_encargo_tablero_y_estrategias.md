# Encargo (Carlos, 5 nov 2026, 01:30): lo que toma más tiempo

Carlos: «prioridad las propuestas a prospectos que mandaron información; lo que tome más tiempo
encárgaselo al Claude de Modal». Las propuestas urgentes ya salieron (Homau, SERTEC y CASER tienen su
muestra y su calificación). Esto es lo largo, y es tuyo:

## 1) Reordenar el tablero: primero los más fáciles de llevar a 8

El tablero lee `entregables/tablero/datos.json` y pinta a los clientes **en el orden del archivo**.
Reordénalo para que arriba queden los más fáciles de subir a 8, y despliega.
Criterio (en este orden):
1. Nota más alta hoy (`mejor`): el que ya está en 7.5 necesita menos que el que está en 5.
2. Que **no dependa del cliente** (`depende_cliente: false`): si lo que falta lo hacemos nosotros, es fácil.
3. Que el salto a la proyectada sea corto.
4. Hasta abajo los que ya tienen campaña corriendo (`campana: true`) y los prospectos.
Deja en el JSON un campo `facilidad_orden` con el número de posición, para que se note por qué quedó así.

## 2) La estrategia de imágenes de TODOS los clientes

Ya están los 2 ángulos y los anuncios escritos de 15 negocios en
`entregables/glimmer_imagenes_20261104/prioridad/*.md` y de 17 en `.../clientes/*.md`.
Lo que falta es **generar las imágenes** de los que no tienen todavía (solo Mariano, Rafael y Manuel
las tienen, en `entregables/anuncios_imagen_20261104/anuncios_v2/`), y los 10 prospectos
(`lote2_prospectos.json`).

**Regla nueva**: las imágenes las hace **Codex y él escribe el texto dentro** (ya no capa de PIL).
Cómo: `codex exec --skip-git-repo-check --sandbox workspace-write -C /workspaces/Nexusv2.0launch18octubre "..."`,
dándole la lista exacta de textos y pidiéndole que edite la foto real del cliente cuando el anuncio
enseñe algo suyo (su cara, su casa, su producto). Revisa cada imagen palabra por palabra antes de darla
por buena. Ejemplos que funcionaron: `entregables/anuncios_imagen_20261104/codex_texto/MARIANO_B1_texto.png`
y `proyectos/amyvip/anuncios/AMY_A1_precio_fijo.png`.

Después de generar cada tanda, califícala con
`python3 entregables/anuncios_imagen_20261104/calificar_portal_v2.py` (portal de Glimmer) y manda a Carlos
cada imagen **por separado** con su nota y sus sugerencias, igual que hice yo
(`entregables/anuncios_imagen_20261104/mandar_una_por_una.py`).

## 3) Terminar las 4 imágenes nuevas de Rafael

Quedó corriendo un trabajo de Codex que no alcanzó a terminar: 4 anuncios con el texto dentro, con él
en su polo azul, el texto abajo a la izquierda sin taparle la cara, CTA «Agendar prueba por WhatsApp» y
las viñetas. La tarea exacta está en el historial del encargo
`20261105_0045_encargo_videos_mariano_rafael.md`. Si no hay nada en
`entregables/anuncios_imagen_20261104/codex_texto/RAFAEL_*`, vuélvelo a lanzar.
Falta de Rafael (pídeselo a Carlos, no a él): ciudad y nombre de la sucursal, y el modelo del auto.

## Reglas

- Nada abajo de 8 se sube a pauta.
- Cada entrega lleva calificación actual y proyectada, separadas.
- No le escribas a ningún cliente sin que Carlos lo pida en ese mensaje.
