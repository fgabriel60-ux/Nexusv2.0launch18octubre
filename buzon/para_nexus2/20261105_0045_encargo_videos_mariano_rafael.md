# Encargo (Carlos, 5 nov 2026, 00:45): aplicar las sugerencias a los videos de Mariano y Rafael

## REGLA NUEVA QUE CAMBIA LO ANTERIOR

Carlos: «que las haga Codex pero que el generador de imágenes haga el texto también, no tú por código».
O sea: **Codex genera la imagen COMPLETA, con el texto ya escrito dentro**. Ya no se arma la capa de
texto con PIL. Probado hoy: Codex escribe perfecto, con acentos y precios correctos, y el diseño sale
mejor que el nuestro (ver `entregables/anuncios_imagen_20261104/codex_texto/MARIANO_B1_texto.png`).

Cómo pedírselo: en el prompt va la lista EXACTA de textos (etiqueta, titular, línea de apoyo, viñetas,
nombre del asesor, botón, pie) y se le pide «el texto debe salir perfectamente escrito en español, sin
faltas y sin letras inventadas». **Siempre revisa la imagen generada palabra por palabra** antes de darla
por buena: si un dato salió mal (precio, teléfono), se regenera, no se corrige a mano.

Ojo importante: cuando el anuncio enseña algo REAL del cliente (su casa, su producto, su cara), hay que
pedirle a Codex que **EDITE la foto real** del cliente y le ponga el texto encima, no que invente la casa.
Una casa inventada en un anuncio inmobiliario es engañoso.

## 1) Mariano · video v8 «cuerda mejorada» (6.5 → 8.5)

Está en el tablero como su mejor versión. Lo que dijo Glimmer, aplícalo tal cual:
- **Gancho 6→8**: reemplazar los primeros 0.0-3.0 s por texto en capa «Casa de 2 pisos en Rosarito
  desde $2.45 MDP» sobre la mejor toma de fachada.
- **Oferta 7→8**: reforzar el precio y la palabra clave en cada bloque de beneficio.
- **Confianza 6→8**: microcredenciales en la capa inferior, «Mariano Herrera · Asesor · Vizcaíno
  Residencial».
Precios reales (él los rotuló en sus propios videos del 17 oct): Bugambilia desde 2.4 MDP, Benjamina
desde 2.8 MDP, Salvia desde 3.1 MDP de 4 recámaras. No inventes otros ni les quites el «desde».

## 2) Rafael · autos BYD · video v4c (7.0 → 8.5)

**LA ORDEN DE CARLOS** (se la escribió a Rafael en su chat, 4 nov 22:19):
> «el video no está tan lejos del 8»
> «si mejoramos ese gancho con tus videos reales ya queda»

O sea: **el arreglo principal es el GANCHO, y se hace con las tomas REALES que mandó Rafael**, no con
clips generados. Sus videos reales están en `clientes/Rafael_BYD/whatsapp/del_cliente/` (los del 3 nov)
y ya hay una versión armada con ellas: `clientes/Rafael_BYD/v5_20261104/Rafael_BYD_v5B_sus_tomas.mp4`.
Arranca el video con su mejor toma real (él o el auto de verdad en la agencia) en los primeros 3 s.

**Lo que él mismo pidió por WhatsApp** (notas de voz del 4 nov, chat `225412869304444@lid` — escúchalas
completas antes de trabajar):
- «también a veces la boca cambia» → hay deformación en la boca en los clips animados. Regenera esos
  tramos o sustitúyelos por tomas fijas con push-in; si un clip no se puede salvar, córtalo.
- «no se ve tan mal, solo que con la camisita me vería mejor» → quiere aparecer con su camisa de
  trabajo. Usa sus fotos reales con el polo azul marino de la agencia
  (`clientes/Rafael_BYD/refs/rafael_cara.jpg`, `rafael_cara_auto.jpg`) como referencia.
Además, lo que falta de él y hay que pedirle a Carlos (no a Rafael directo): su oferta comercial del mes,
la ciudad y el nombre de la agencia, para poder ponerlo en el anuncio.

## Cómo cerrar

- Versiona, no sobrescribas (v9, v4d…).
- Al terminar cada uno, califícalo en el portal de Glimmer y deja el archivo de calificación junto al video:
  https://charlyfavela666--glimmer-rapido-web.us-east.modal.run/?k=i7_8usCbRdED_8lp
- Manda a Carlos el video con `herramientas/enviar_seguro.py`, con la calificación **actual** y la
  **proyectada** separadas, y qué falta.
- No le escribas a Mariano ni a Rafael sin que Carlos lo pida en ese mensaje.
