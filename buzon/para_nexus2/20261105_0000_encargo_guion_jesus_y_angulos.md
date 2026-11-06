# Encargo (4 nov 2026, noche) · guion de Jesús cápsulas, ángulos, imágenes y portal de Glimmer

Carlos lo pidió en el chat con Claude del Codespace. Se copia aquí para que **no quede en el aire**:
Claude ya hizo la primera parte; tú continúas lo que falte o si él se queda sin uso.

## 1) Jesús · cápsulas Rar~Amore (PRIORIDAD) — HECHO, falta seguimiento

Ya se le mandó por WhatsApp (chat `31606932787332@lid`) el **guion de 6 tomas, 25-30 s** para que él grabe,
pensado para llegar fácil a 8: él hablando, el frasco con etiqueta legible, su WhatsApp 81 8466 8456,
y **sin una sola promesa de salud** (nada de curar, aliviar, regenerar, antes y después, ni «garantizado»).
Le pedimos: foto del frasco con etiqueta, foto suya con el producto y confirmación de su WhatsApp Business.

**Pendiente tuyo:** cuando mande el video y las fotos → armarlo, calificarlo y avisarle a Carlos con la nota
actual y la proyectada. Si pasan horas sin respuesta, recordárselo una vez (y solo si Carlos lo autoriza).

## 2) Estrategia de ángulos e imágenes — en curso

- Ángulos, static ads y guiones escritos: `entregables/glimmer_imagenes_20261104/prioridad/*.md` (15 negocios,
  en el orden que dictó Carlos) y `entregables/glimmer_imagenes_20261104/clientes/*.md` (ronda de 5 ideas).
- **Imágenes ya generadas (12)**: `entregables/anuncios_imagen_20261104/anuncios/` → Mariano, Rafael y Manuel,
  4 cada uno (2 ángulos x 2 imágenes). La receta exacta está en el encargo
  `20261104_2320_encargo_imagenes_como_rafael.md`.
- **Falta**: las 4 imágenes de los demás negocios y los 10 prospectos
  (`entregables/glimmer_imagenes_20261104/lote2_prospectos.json`).

## 3) Por qué funciona cada imagen (PRIORIDAD de Carlos)

Cada anuncio debe entregarse con su **calificación de Facebook y el porqué**, para poder convencer al cliente.
Ya está el script que lo hace solo: `entregables/anuncios_imagen_20261104/calificar_portal.py` — pasa cada
imagen por el portal de Glimmer y guarda en `calificaciones/<ANUNCIO>.md` la nota por rubro, POR QUÉ FUNCIONA,
QUÉ LO FRENA, el PLAN para llegar a 9-10 y el texto listo para mandarle al cliente por WhatsApp.
Úsalo con cada imagen nueva que generes.

## 4) Portal de Glimmer rápido (para Carlos y para los clientes)

https://charlyfavela666--glimmer-rapido-web.us-east.modal.run/?k=i7_8usCbRdED_8lp
(la clave es la misma del tablero, secreto `tablero-clave`). Se suben imágenes del anuncio, se escribe el
negocio y contesta el plan de calidad. API: `POST /calificar` con `{"fotos":["data:image/jpeg;base64,..."],
"contexto":"...","tokens":900}` y `?k=` o header `x-clave`. La primera consulta tarda ~2-4 min porque prende
la A100; las siguientes salen en segundos (se queda caliente 4 min). Código: `modelos_modal/glimmer_rapido.py`.

## 5) Adrián · tatuador — HECHO, revisar

`clientes/Tatuador9983316522/v3_subs/Adrian_v3_subs.mp4`: su video de 17 s con subtítulos palabra por palabra
(tiempos reales de Whisper), tarjeta de nombre y de ubicación, color y audio normalizado. Glimmer: **5/10 hoy
→ 9/10 proyectada**; lo que falta es CTA más concreto, que los subtítulos no corten palabras y prueba social.
Script: `clientes/Tatuador9983316522/v3_subs/armar_tatuador_v3.py`.

## Reglas de siempre

- Datos reales del cliente; si falta algo, `[FALTA: ...]`, nunca inventado.
- No escribirle a ningún cliente sin que Carlos lo pida en ese mensaje.
- Todo lo que se entregue lleva su calificación de Glimmer: actual y proyectada, separadas.
