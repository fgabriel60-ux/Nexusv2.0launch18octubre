# MISIÓN: los prospectos son tuyos (Carlos, 5 nov 2026, 01:00)

Carlos lo dijo así: «encárgale al Claude de Modal la misión de los prospectos».
De aquí en adelante **tú atiendes a los prospectos**: contestas, pides material, haces la muestra y
los cierras. Carlos te autorizó **hacer muestras de video a prospectos** («te doy permiso de hacer muestra
de video, si logras que paguen»). Eso NO cambia la regla de los clientes: a un cliente no se le escribe sin
que Carlos lo pida en ese mensaje.

## Cómo se atiende un prospecto (lo que ya funciona)

1. **Primer mensaje** (cuando llega «¡Hola! Quiero más información»): se explica que calificamos el anuncio
   con la IA de Facebook y que **solo lanzamos con 8 de 10**, con los números reales de la agencia
   (limpieza: 33 mensajes a $1.39; impermeabilización: 18 mensajes a $2.87), y se piden 4 cosas:
   giro y ciudad · 3 fotos o videos · qué precio o promoción quiere anunciar · un reel de referencia.
   Somos de Sonora y trabajamos 100% en línea con todo México.
2. **En cuanto manden material**: descargarlo, transcribir si es video (faster_whisper), calificarlo en el
   portal de Glimmer y contestar con la nota actual, la proyectada y **los rubros que lo tienen abajo**.
3. **Muestra**: si tiene video, recortarlo a 25-30 s con lo que vende, subirlo a 720x1280, color, audio
   normalizado, subtítulos limpios palabra por palabra y tarjetas con SUS datos reales, y cierre con
   llamado a WhatsApp. Mandársela con la calificación. Es lo que los convence de pagar.
4. **Pedir lo que falta** para llegar a 8, en lista corta y concreta.

## Hecho hoy (no lo repitas, dale seguimiento)

- **Homau · jardín de eventos y food garden** (`62350124183625@lid`): su video califica **4/10 → 8.5**.
  Ya se le mandó la muestra `prospectos/jardin_eventos_5539964102/Homau_muestra_v1.mp4` (29 s) con la
  calificación y lo que falta: ciudad y dirección, el video **sin los textos de colores**, qué incluye la
  renta y cómo se aparta, y su logo. Script: `prospectos/jardin_eventos_5539964102/armar_muestra.py`.
- `220679848853639@lid` y `249915959713792@lid`: leads nuevos, ya tienen el primer mensaje, **esperan respuesta**.
- Revisados 140 chats: los demás sin contestar eran bancos, Meta y bots, no prospectos.

## Herramientas

- **Portal de Glimmer** (calificación y plan de calidad, segundos cuando está caliente):
  https://charlyfavela666--glimmer-rapido-web.us-east.modal.run/?k=i7_8usCbRdED_8lp
  API: `POST /calificar` con `{"fotos":["data:image/jpeg;base64,..."],"contexto":"...","tokens":1100}`.
- **WhatsApp**: `herramientas/wa.py` (`fetch-messages`, `send-message`, `send-media`, `download-media`).
- **Codex hace imágenes** (probado hoy): `codex exec --skip-git-repo-check --sandbox workspace-write -C <raíz> "..."`
  genera imágenes 4:5 realistas y **puede editar a partir de la foto real del cliente** manteniendo su cara.
  Sirve para ambientes y escenarios; para la cara real también funciona. No gasta GPU de Modal.
- **Muestra de video**: ffmpeg + ASS con tiempos reales de Whisper (`word_timestamps=True`).

## Reglas

- Nunca inventes ciudad, precio, promoción ni resultados: si falta, pídelo y escríbelo como `[FALTA: ...]`.
- Cada video o imagen que mandes lleva su calificación: **actual** y **proyectada**, separadas.
- Nada se sube a pauta abajo de 8.
- Reporta a Carlos: a quién atendiste, qué mandaste, qué falta y quién está por pagar.

---

# AÑADIDO (Carlos, 5 nov 01:20): «atiende a los que no se les contestó»

Barrido de los 140 chats más recientes: estos son los que **quedaron sin respuesta nuestra** (el último
mensaje es de ellos). Ya se quitaron los bots de bancos, Meta y WhatsApp Business. Ve uno por uno,
lee su conversación completa antes de escribir, y contesta según lo que ya se le había dicho.

| Fecha | Chat | ID | Msjs nuestros | Último mensaje de él |
|---|---|---|---|---|
| 04/11 23:09 | +52 1 55 3996 4102 · Homau | `62350124183625@lid` | 2 | «Dentro de este espacio tengo un food garden» — YA tiene muestra y calificación; falta su respuesta |
| 04/11 19:14 | +52 1 729 118 9182 | `214925314125860@lid` | 4 | «Okey» |
| 03/11 19:00 | +52 1 833 616 5993 | `99811114111056@lid` | 1 | mandó un documento, nadie lo abrió |
| 03/11 16:00 | +52 1 33 3008 0919 | `162337281585355@lid` | 0 | mandó una imagen y nunca se le contestó |
| 31/10 20:41 | Gordo | `14023470874814@lid` | 3 | mandó imagen |
| 31/10 19:50 | Danny Sapiens Socio | `251419567337705@lid` | 4 | nota de voz sin escuchar |
| 30/10 16:10 | Finanzas e Inmobiliaria | `74333166797031@lid` | 7 | «¿Cómo podemos ayudarte?» |
| 30/10 05:37 | +52 1 662 188 6655 | `178997107413183@lid` | 2 | «Ok» |
| 29/10 22:34 | +52 1 631 106 6972 | `7967818657796@lid` | 6 | «Aah bueno» |
| 28/10 20:28 | +52 1 631 168 6022 | `249992900006009@lid` | 4 | mandó imagen |
| 28/10 19:35 | +52 1 55 1621 8110 | `155358110683290@lid` | 1 | mandó imagen |
| 28/10 16:37 | +1 (205) 341-2765 | `26917315031157@lid` | 0 | sin contenido legible |
| 27/10 20:06 | +1 (645) 200-5378 | `252136776572995@lid` | 3 | respuesta automática de rentas de autos |
| 27/10 17:01 | +52 1 449 819 0392 | `213095507062970@lid` | 3 | «?» — se quedó esperando |

Cómo contestarlos:
- Si ya había conversación de venta, **retómala donde se quedó**, no mandes el mensaje de bienvenida otra vez.
- Si mandaron foto, video o documento: ábrelo (`download-media`), míralo, y contesta sobre eso. Si es su
  negocio, califícalo en el portal y dile la nota con lo que le falta para 8.
- Si solo pusieron «Ok» o «?», reengancha con algo útil: la calificación de su material o una idea concreta
  para su giro, y pide lo que falte.
- Si resulta que no es prospecto (bot, personal, otro asunto), déjalo anotado y no insistas.
- Reporta a Carlos la lista con qué contestaste a cada uno y quién quedó caliente.

---

# AÑADIDO 2 (Carlos, 5 nov 01:35)

## Regla nueva: TODAS las imágenes se generan con Codex

Ya no se usan Qwen ni fotos de internet para generar. Se usa **Codex**:

```
codex exec --skip-git-repo-check --sandbox workspace-write -C /workspaces/Nexusv2.0launch18octubre "<instrucción>"
```

- Acepta la **foto real del cliente como referencia** y le conserva la cara y la ropa. Pídeselo explícito:
  «EDITA a partir de la foto real tal, misma cara, misma ropa, una sola persona, sin texto dentro de la imagen».
- Saca 4:5 (1120x1400) con calidad de foto publicitaria. Probado el 4 nov contra Qwen: Codex muy superior
  (Qwen duplicaba a la persona y arrastraba rótulos viejos de los videos).
- No prende GPU de Modal; usa la suscripción de ChatGPT de Carlos. Qwen queda solo de respaldo si Codex se
  niega o si ya se topó el uso de ChatGPT.
- El **texto del anuncio siempre va en capa aparte** (PIL, con `armar_anuncios.py`), nunca generado dentro
  de la imagen. Si el cliente tiene fotos reales buenas, esas ganan sobre cualquier generación.

## Prioridad de los sin contestar: SOLO los de HOY

De la lista de arriba, hoy nada más estos dos. Los demás pueden esperar:

1. **+52 1 55 3996 4102 · Homau** (`62350124183625@lid`) — ya tiene muestra y calificación 4/10 → 8.5.
   Está en que mande ciudad y dirección, el video sin textos de colores, qué incluye la renta y su logo.
2. **+52 1 729 118 9182** (`214925314125860@lid`) — **el más caliente**. El 31 de oct dijo:
   «Me interesa la propuesta, especialmente porque también desarrollan la campaña», se le ofreció una
   llamada y quedó «pendiente». Hoy se le mandó la imagen del 8 y contestó «Okey». Hay que retomarlo:
   proponerle hora de llamada o mandarle propuesta concreta y una muestra con su material.
   Antes de escribirle, lee toda su conversación: ya hay trato avanzado, no le mandes el mensaje de bienvenida.
