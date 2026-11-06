# Traspaso al Claude de Modal 666 · 30 oct 2026

Eres el Claude de Carlos (Visión Agencia) corriendo en el sandbox `nexus-claude` de la cuenta Modal **charlyfavela666**. La computadora/codespace anterior se apaga: desde ahora todo corre aquí. **Responde SIEMPRE en español.** Lee también tu memoria (`/vol/claude-config/projects/*/memory/MEMORY.md`).

## Cómo trabajar
- Workspace: `/workspaces/Nexusv2.0launch18octubre` (volumen `nexus-workspace`). Secreto `nexus-env` ya cargado (WAAPI_TOKEN, WAAPI_INSTANCE, FISH_API_KEY, APIFY_TOKEN).
- Trabajos de GPU: `GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run <script.py> ...` (reporta gasto y saldo; tope $28 de los $30). Saldo: `GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py saldo`. **Dile siempre a Carlos el gasto del trabajo y el saldo.**
- Volúmenes de modelos ya en 666: `qwen-image-edit-2511`, `h3-comprimido-gastro` (MiniMax H3 + ComfyUI), `muse-glimmer-30b` (Glimmer: `entregables/glimmer_estrategias_20261029/glimmer_modal.py`).
- Pipeline y reglas: memoria `pipeline-videos-modal`. NO correr dos GPU en paralelo contra el mismo volumen. H3: ancho/alto múltiplos de 32 (704×1280).
- `fgabriel60` (saldo ≈ $7) queda solo de reserva.
- WhatsApp (WaAPI instancia 106321): chat de Carlos consigo mismo `44522318905388@lid` para entregarle todo (`/client/action/send-media` con `mediaBase64`, `asDocument` false). A clientes SOLO si Carlos lo pide. Da 429/500/409 a ratos: espacia 6-8 s y reintenta. Helper: `entregables/continuacion_claude_20261025/enviar_videos_carlos.py` (`call`, `failures`). Chat de Guillermo `256998142660619@lid`; José Grupo JR `186389366857933@lid`; Giovanni `147832891793521@lid`. Audios de clientes: `download-media` + `faster_whisper` (small, es) para transcribir.
- Carlos te controla desde el celular: «descansa» (apaga este sandbox, no gasta) y «despierta» (vuelve) escribiéndolos en su chat de WhatsApp consigo mismo. Un vigía recrea este sandbox si se cae. Código: `nexus_666.py`.
- Comandos de Modal: `MODAL_IMAGE_BUILDER_VERSION=2025.06` (ya está en gasto_modal.py).

## Estado y pendientes (por prioridad)
1. **Giovanni · video v2**: se estaba generando en fgabriel60 (`clientes/Giovanni/video_v2_20261030/`, tomas con su voz `clientes/lote_30oct/voz/G1,G2a,G2b.wav`). Cuando existan `salida/G1.mp4, G2a.mp4, G2b.mp4`, armar con `armar_giovanni_v2.py` (voz Fish ya hecha, subtítulos, tarjeta final $20,000 · 624 136 3328) y mandárselo a Carlos. Si no llegaron a generarse: relanzar `giovanni_modal.py` con GASTO_PERFIL=charlyfavela666. Que confirme precio $20,000.
2. **Guillermo**: techo v6 (A: láminas caen / B: suben, vigas visibles debajo) ya enviado a Carlos; esperar cuál elige. Scripts: `clientes/Guillermo/techo_20261029/lamina_exacta.py` (compone sobre su captura; `--sube` para la variante B). Su audio de las 00:46: quiere que el discurso/anuncio sea de **zaguanes, cortinas, puertas y pérgolas, menos voluminoso** (más accesible) → rehacer el video Pixar `clientes/Guillermo/obrero_20261029/` (trabajo.json, voces c_*.mp3 y g_*.wav) con esos servicios, sin la nave grande. Espera también su foto de otro techo.
3. **José (Grupo JR)**: v4 «como la referencia» terminado: `clientes/Jose/Jose_GrupoJR_Pixar_obrero_v4.mp4` (scripts `clientes/Jose/obrero_v4_20261030/jose_v4_modal.py`, `armado_20261029/armar_jose_v4.py`). Mandárselo a Carlos si no se envió. José dice que el que Meta apruebe es el bueno (v3 vs v4).
4. **Artifact de Gantt para clientes** (video de ConstructIQ «Claude + Excel: AI Gantt Charts», pero como Artifact, no Excel): si no está publicado, hacerlo (primero `Artifact action quickstart`).
5. **Cola** (de la sesión anterior): Mariano (gancho del Tesla llegando a Vizcaíno, voz `clientes/lote_30oct/voz/MT.wav`); Rubén y Jesús Puertas (video de proceso de sus puertas); Víctor (video obra fina con escenas reales, sin mezclar industria); Fumigador (escenas nuevas como Iván); Alberto (nueva versión de la doctora); Fernando (unir su video; impresora, lector y caja); Lisbeth (tarjetas y cierre; espera su página, presupuesto, plano y documentos); pistas de baile (estrategia 10/10/10 con Glimmer + 2 ideas de video y servicios de audio/eventos); Manuel Fotografía (calificación de Glimmer; Windsor no tiene su página).
6. **Cobros**: Ignacio $500 pendiente; pistas de baile pagó 24 oct → cobro mensual 24 nov.

Lista resumida: `entregas_para_carlos/LISTA_CLIENTES_20261030.md`. Entregables de hoy: `entregas_para_carlos/`.

## Reglas de Carlos
- Reels: se presenta como conversación con Claude, no con la IA de Meta. Nunca prometas plazos/garantías en anuncios legales. Entrega videos H.264 Main 720p (<16 MB).
- Antes de acciones difíciles de revertir o hacia afuera (enviar a clientes, borrar) confirma con él.
