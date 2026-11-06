# Encargo (Carlos, 5 nov 2026, 02:10): las imágenes de TODOS los clientes, hechas con ChatGPT (Codex)

Carlos: «pídele a nexus que saque las imágenes de todos los clientes con la estrategia de Glimmer,
pero en ChatGPT». Es decir: la estrategia ya está escrita, lo que falta es **producirlas**, y se producen
con **Codex**, que además **escribe el texto dentro de la imagen**.

## De dónde sale el contenido de cada anuncio

- `entregables/glimmer_imagenes_20261104/prioridad/*.md` → 2 ángulos + 2 anuncios de imagen + guion,
  de 15 negocios (tatuador, Mariano, Rafael, Giovanni, Fernando, Rubén, ginecólogo, oficinas amuebladas,
  Lisbeth, Víctor, Rashel Carrasco, Jesús Puertas, Ignacio Iglesia, Jesús cápsulas, Manuel).
- `entregables/glimmer_imagenes_20261104/clientes/*.md` → 5 ideas de imagen por cliente, de 17 clientes.
- Prospectos que faltan de estrategia: `entregables/glimmer_imagenes_20261104/lote2_prospectos.json`
  (córrelo con `entregables/glimmer_estrategias_20261029/glimmer_modal.py --lote ... --tokens 3500`).

**Ya hechos, no los repitas**: Mariano, Rafael y Manuel tienen 4 cada uno en
`entregables/anuncios_imagen_20261104/anuncios_v2/` (aunque Rafael y Mariano hay que rehacerlos con
Codex, ver el encargo de PRIORIDAD).

## Cómo se produce cada imagen

```
codex exec --skip-git-repo-check --sandbox workspace-write -C /workspaces/Nexusv2.0launch18octubre "<instrucción>"
```
En la instrucción va:
1. Qué se ve (sacado del ángulo de Glimmer).
2. **Los textos exactos**: etiqueta, titular (máx. 7 palabras), línea de apoyo, 3 viñetas con palomita,
   nombre o sello del cliente, botón verde de WhatsApp, pie si hace falta.
3. «El texto debe salir perfectamente escrito en español, con acentos y sin letras inventadas».
4. Diseño: vertical 4:5, bloque de texto abajo sobre degradado oscuro, tipografía gruesa blanca,
   sin taparle la cara a la persona, sin logotipos de marcas inventados.
5. Si el anuncio enseña algo REAL del cliente (su cara, su casa, su producto), **que EDITE la foto real**
   que está en `clientes/<Cliente>/`, no que invente.

Ejemplos que ya salieron bien: `entregables/anuncios_imagen_20261104/codex_texto/MARIANO_B1_texto.png`,
`proyectos/amyvip/anuncios/AMY_A1_precio_fijo.png` (este sacó 7/10 a la primera).

## Cómo cerrar cada cliente

1. Revisa la imagen palabra por palabra: si un dato salió mal, se regenera, no se corrige a mano.
2. Califícala con el portal de Glimmer (si el portal da error 303, llama al servicio directo con
   `modal.Cls.from_name('glimmer-rapido','Rapido')` y `MODAL_PROFILE=charlyfavela666`).
3. Manda a Carlos **cada imagen por separado** con su nota y sus sugerencias
   (`entregables/anuncios_imagen_20261104/mandar_una_por_una.py` hace eso).
4. Nada abajo de 8 se sube a pauta. No le escribas a ningún cliente sin que Carlos lo pida.

Orden: primero **Rafael y Mariano** (encargo de PRIORIDAD), luego el resto de clientes, al final los
prospectos.
