# Manual de producción para ChatGPT (cuando Claude no esté) · 31 oct 2026

Lee primero `AGENTS.md`, `/vol/claude-config/codex/contexto_carlos.md` y TODA la memoria (`/vol/claude-config/projects/---modal-volumes-vo-N6gOPxHfXSf5HzbsmuqjJ3-workspaces-Nexusv2-0launch18octubre/memory/`, empieza por MEMORY.md).
Raíz: `/workspaces/Nexusv2.0launch18octubre`. Todo comando de GPU con `GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run ...` (reporta gasto y saldo; tope $28).

## 0. Reglas que Carlos repite
- NO mandar nada a clientes/prospectos sin que Carlos lo pida. Todo va primero a Carlos (chat `44522318905388@lid`) con `python3 herramientas/enviar_seguro.py RUTA "texto"`.
- Cada video lleva calificación de Glimmer: **actual** vs **proyectada**. Nunca inventar números.
- Animación SIEMPRE con GPU **MiniMax H3** (salvo que Carlos diga otro), pero barata (sección 4).
- Método: referencia (reel de Instagram) → plan Glimmer 10/10/10 → escenas propias parecidas a la referencia → Glimmer → corregir hasta 8-9.
- Caras parecidas a la persona real, lugares reales, sus fotos reales. Revisar cuadros ANTES de animar.
- Versionar (v3 → v4), nunca borrar archivos de clientes.

## 1. Bajar una referencia de Instagram
```
pip install -q yt-dlp   # si falta
mkdir -p clientes/<Cliente>/referencia && cd $_ && yt-dlp -q -o '<ID>.%(ext)s' 'https://www.instagram.com/reel/<ID>/'
ffmpeg -v error -y -i <ID>.mp4 -vf "fps=18/DURACION,scale=180:-1,tile=6x3" -frames:v 1 hoja.jpg   # hoja de cuadros para verla
```
Transcribir: faster_whisper (pasar audio como numpy: `ffmpeg -f s16le -ac 1 -ar 16000 -` → `np.frombuffer(...)/32768`; NO pasar la ruta, falla con av).

## 2. Fotos/videos del cliente
Si faltan (la mudanza borró `whatsapp/`), bajarlas de su chat:
`accion('fetch-messages',{'chatId':ID,'limit':150})` → para `type in ('image','video')` y `not fromMe`: `accion('download-media',{'messageId':m['id']['_serialized']})['data']['data']['media']['url']` → requests.get.

## 3. Escenas con GPU (Qwen cuadros + MiniMax H3)
Script: `clientes/_escenas_carlos/escenas_carlos_modal.py` con un spec JSON (ejemplos en `entregables/specs_20261031/`):
```json
{"carpeta":"cliente_tema_v1","salida":"clientes/<Cliente>/<tema>/salida","semilla":17,
 "ancho":720,"alto":1280,"pasos":28,
 "refs":{"cara":"ruta/foto_cara.jpg","lugar":"ruta/foto_lugar.jpg"},
 "cuadros":{"C1_nombre":[["cara","lugar"],"Foto realista vertical 9:16 ... el MISMO hombre de la primera imagen ... en la MISMA casa de la segunda imagen ...","negativos extra"]},
 "tomas":[["T1_nombre","C1_nombre","Prompt en inglés del movimiento. Audio: ...",3.0,null,"C2_nombre_final_opcional"]],
 "voces":{"gancho":"ruta/voz.wav"}}
```
- Cuadros: `...::cuadros --spec X.json` → PNG en `salida`. **Revisar con una hoja de contacto** antes de animar.
- Animar: `...::animar --spec X.json` (usa los PNG de `salida`). Toma con voz (lipsync): poner el nombre de la voz en el 5º campo y `seg` = duración de la voz.
- Horizontal (monitor/web): `"ancho":1280,"alto":720`.
- Encolar en la fila de escenas (una GPU a la vez): escribir `entregables/fila_escenas/pendientes/AAAAMMDD_HHMM_cliente.sh` con el comando. Log: `entregables/fila_escenas/fila.log`.
- Errores típicos de Qwen y cómo evitarlos: si pasas una foto de referencia de OTRA casa/persona la copia (Mariano r3 salió con casa gringa) → solo refs del cliente y describir la pose con palabras; si la referencia es una selfie con celular, la copia (tatuador) → añadir «celular, espejo, selfie» a negativos y no usar esa foto.

## 4. Cómo ahorrar GPU con MiniMax (Carlos lo pidió)
- GPU de MiniMax por defecto: L40S (31 oct, ~45% más barata que A100, probada con la Salvia de Mariano). Para volver a A100: GPU_H3=A100-80GB.
- Toma corta: `_largo_corto` ya genera ~3 s (73 cuadros) si `seg` ≤ 3. No pedir 5 s si usarás 2.
- **Primer + último cuadro** (6º campo de la toma): MiniMax acierta el movimiento a la primera. Ej. marometa de Mariano r6 ($0.39): cuadros clave hechos con recortes (`rembg`) sobre el fondo limpio (`cv2.inpaint`) → 2 tomas de 3 s. Ver `clientes/Mariano/video/spiderman/codigo/` y spec `mariano_spiderman_r6.json`.
- Qwen 28 pasos (ya por defecto). Varias tomas en un solo spec (el modelo carga una vez).
- Reusar tomas buenas ya pagadas; solo rehacer la que falló.
- Glimmer es lo más caro: un lote por cliente, no lotes gigantes (uno de 9 videos costó ~$6). `--tokens 4500` para calificar.
- No correr 2 trabajos al mismo tiempo sin necesidad (el reporte los cuenta doble y el volumen se pelea).

## 5. Voz clonada (Fish)
`POST https://api.fish.audio/v1/tts` header `Authorization: Bearer $FISH_API_KEY`, `model: s2-pro` (o `s1`), json `{"text","format":"wav","reference_id":ID}`. 4 tomas por frase; quedarse con la que Whisper medium transcriba igual. Números en letras («siete millones seiscientos mil»), «uatsap» para WhatsApp. Ejemplo completo: `/tmp/vero_voz.py` (copia en `clientes/VeronicaArguelles/video/v3d_v1/voz/`). IDs en AGENTS.md y `clientes/<Cliente>/voz/voz_id_fish.txt`.

## 6. Armar el video (ffmpeg, sin GPU)
- Subtítulos normales: tiempos de Whisper (`word_timestamps=True`) + **texto del guion real** (no el de Whisper; escribe mal nombres: «Rosalito», «loza»). Ejemplo: `clientes/Jose/armado_20261029/armar_jose_v9g.py`.
- Reemplazar solo el gancho de un video ya hecho conservando el resto y su audio: ver la receta de Mariano v6 (concat de tomas nuevas + `trim` del video viejo desde el segundo donde empieza el recorrido; voz con `adelay` al inicio del habla; whoosh/golpe de `clientes/Guillermo/video/sfx/`).
- Recorrido de fotos: `entregables/prospectos_sancarlos_20261031/villabahia_3c/armar_vb.py`.
- Monitor/web 3D: `clientes/VeronicaArguelles/video/armar_v3d.py`.
- Verificar SIEMPRE: hoja de cuadros (`fps=2,tile`) y Whisper del audio final.

## 7. Calificar con Glimmer
`entregables/glimmer_evaluador/anuncios_<id>.json` = `[{"nombre","video","cliente":"datos REALES del negocio"}]` y encolar en `entregables/fila/pendientes/` (formato en AGENTS.md). Resultado: lo que sigue a `assistant to=user` en `glimmer.log`; separado por `######## NOMBRE`. Estrategia 10/10/10 (sin video): lote `[{"nombre","prompt","fotos":[hoja.jpg]}]` (ej. `entregables/glimmer_evaluador/villabahia_estrategia/lote.json`).

## 8. Estado al 31 oct (lo que quedó)
- Mariano: gancho v6 con marometa (MiniMax, $0.39) mandado a Carlos; falta calificación.
- Verónica: recorrido 3D v1b mandado; Carlos pidió versión «con puro código» (pedido en `clientes/VeronicaArguelles/video/codigo_v1/pedido.txt`).
- José: v9g sin paneles, subtítulos normales; v9f = 6/10 → 8.
- Tatuador (Adrián): frames v1 (3 buenos) + v1b rehechos; falta animar y hard cut. Él pidió no verse hecho con IA: preguntar a Carlos.
- Tesla volador México v2 (39 s) mandado. Villa Bahía 3C recorrido mandado; plan B (4 propiedades) en Glimmer.
- Pendientes de Carlos: ¿escribir a prospectos San Carlos (estadía 6-8 nov)?; ¿Tesla para Visión Agencia?
