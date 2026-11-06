# Encargo: arreglar las 4 imágenes de Mariano (Carlos, 5 nov 2026, 00:30)

Carlos pidió que TÚ hagas estos cambios. Las imágenes ya existen y ya están calificadas; falta aplicarles
lo que Glimmer dijo y volver a calificarlas. Ninguna llega a 8 todavía, así que **no se suben hasta que
lleguen**.

## De qué estamos hablando

- Imágenes: `entregables/anuncios_imagen_20261104/anuncios/MARIANO_*.jpg` (4:5, 1080x1350).
- Calificación de cada una, con el porqué: `entregables/anuncios_imagen_20261104/calificaciones/MARIANO_*.md`.
- El script que las arma: `entregables/anuncios_imagen_20261104/armar_anuncios.py`
  (funciones `anuncio()`, `collage3()`, `logo()`; cada cliente tiene su bloque).
- Fotos y fotogramas reales: `clientes/Mariano/anuncios/refs/` y sus videos en
  `clientes/Mariano/whatsapp/del_cliente/`.
- Ángulos y textos: `entregables/glimmer_imagenes_20261104/prioridad/Mariano.md`.

Las 4 van hoy en **6/10, proyectada 9/10**.

## Lo que hay que cambiarles (sale de la calificación, no lo inventes)

**Las 4, en común**
1. El texto tapa la foto o el rostro. Mover el bloque de texto abajo a la izquierda, con una caja
   semitransparente detrás, y dejar libre la cara de Mariano y la fachada. (+0.5 a +1)
2. Falta el nombre del desarrollo y la marca personal. Agregar sello:
   **«Mariano Herrera · Asesor · Vizcaíno Residencial»** y el logo. (+0.8 a +1)
   → Hay que pedirle a Carlos el logo de Vizcaíno Residencial / Grupo Lagsa y una foto de perfil de
   Mariano; si no llegan, usar solo el sello de texto y anotarlo como `[FALTA: logo]`.
3. CTA genérico. Cambiarlo por uno con promesa:
   · A1 y A2: **«Quiero el recorrido de las 3 casas»**
   · B1 y B2: **«Enviar WhatsApp para recorrido y precios»** (+0.5 a +0.8)

**Por imagen**
- **A1 (las 3 casas)**: agregar la línea de precios por modelo
  «Bugambilia desde $2.4 MDP · Benjamina desde $2.8 MDP · Salvia desde $3.1 MDP, 4 rec» y tres íconos de
  amenidades: acceso controlado, plaza comercial, pádel y área de juegos. (+1.5)
- **A2 (él frente a la casa)**: nombrar los 3 modelos con precios y amenidades en texto breve, mover el
  copy para no taparle el rostro y poner micro-sello «Recorridos diarios». (+1.0 y +0.7)
- **B1 (Benjamina precio)**: bajar el tamaño del titular, subir «BENJAMINA DESDE $2.8 MDP» a la esquina
  superior izquierda y poner 3 bullets de valor (acceso controlado, plaza comercial, pádel y juegos). (+1.0)
- **B2 (cita)**: mostrar «Vizcaíno Residencial», los 3 modelos con precios y las 3 amenidades, y mover el
  texto para dejar libre su cara. (+1.5 y +0.5)

**Los precios son reales**: él mismo los rotuló en sus videos del 17 de oct
(`clientes/Mariano/whatsapp/del_cliente/20261017_1735*.mp4`): Benjamina 2.8M, Bugambilia 2.4M, Salvia 3.1M
de 4 recámaras. No inventes otros ni les quites el «desde».

## Cómo cerrarlo

1. Edita `armar_anuncios.py` (o agrega una función `mariano_v2()`), vuelve a generar las 4 y guárdalas como
   `MARIANO_*_v2.jpg`. No borres las v1.
2. Pásalas por el portal de Glimmer con
   `python3 entregables/anuncios_imagen_20261104/calificar_portal.py` (toma solo las que no tengan
   calificación todavía). Portal:
   https://charlyfavela666--glimmer-rapido-web.us-east.modal.run/?k=i7_8usCbRdED_8lp
3. Si alguna no llega a 8, aplica lo que diga la nueva calificación y repite. No subir nada abajo de 8.
4. Arma una hoja 2x2 y mándasela a Carlos con `python3 herramientas/enviar_seguro.py RUTA "texto"`,
   diciendo la calificación anterior, la nueva y qué falta que mande Mariano.
5. No le escribas a Mariano sin que Carlos lo pida en ese mensaje.
