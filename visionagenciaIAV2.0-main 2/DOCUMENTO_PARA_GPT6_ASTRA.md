# Catania — corte fotorrealista por cuarto (contexto para retomar la tarea)

## Quién es el cliente y qué se está haciendo

**Vision Agencia IA** produce contenido de marketing inmobiliario con IA. El cliente
**Mariano Herrera** es agente en **San Marino Residencial** (zona costa Tijuana–Rosarito)
y vende 4 modelos de casa: Portofino ($5.2M), **Catania ($5.0M)**, Siena ($4.4M) y
Brescia ($3.8M). Mariano mandó por WhatsApp clips en video reales de cada casa amueblada.

La tarea actual: convertir el modelo 3D de **Catania** (Blender) en una **imagen fotorrealista
de corte de casa de muñecas** — la casa entera en corte, los tres niveles + roof garden,
cada cuarto amueblado y con el acabado real que se ve en los videos de Mariano.

## Por qué no basta una sola generación de IA

Ya se probó (GPT Image edit y Seedream) mandar el corte 3D en gris + una hoja con las fotos
reales, pidiéndole a la IA que lo vista completo en una sola pasada. Resultado: cada intento
acierta unos cuartos e inventa otros — un sillón del color equivocado, muebles de un cuarto
que aparecen en otro, el roof garden confundido con la sala de TV. La IA no tiene forma de
saber "esta referencia va SOLO en este cuarto" cuando todo llega en una imagen.

**La solución en construcción:** máscara por cuarto (blanco donde se ve ESE cuarto, negro en
todo lo demás, generada geométricamente desde el propio Blender) + `bria/fibo-edit/genfill`
(Wavespeed) para vestir cada cuarto por separado usando `mask_image` — así vestir la cocina
ya no puede mover la recámara. Antes, un ControlNet de aristas (`flux-controlnet-union-pro-2.0`)
fija la geometría para que la IA no redibuje la planta.

## Dónde vive todo

- **El .blend real**: `catania_LIGERA.blend`, en la Mac de Carlos (`/Users/juancarlos/`),
  Blender 3.3, motor Workbench, escena `Scene`, view_transform **Filmic**.
- **El puente**: `https://conectorblender.onrender.com/api/blender/execute` — recibe un
  string de Python por POST y lo ejecuta DENTRO del Blender de Carlos (tiene que estar
  abierto con el panel Seedance conectado). Se manda así:
  ```python
  import json, urllib.request
  d = json.dumps({"python": codigo_fuente, "meta": {"tipo": "libre"}}).encode()
  r = urllib.request.Request("https://conectorblender.onrender.com/api/blender/execute",
                              data=d, headers={"Content-Type": "application/json"})
  print(json.loads(urllib.request.urlopen(r, timeout=580).read()))
  ```
  El script termina con `responder({...})` para regresar datos (incluyendo imágenes en
  base64) en la respuesta HTTP. Si Blender no está conectado, responde 503.
- **Scripts clave** (repo, `clientes/Mariano/blender/`):
  - `cuartos_camara.py` — diccionario `CUARTOS` (16 cuartos: posición de cámara, hacia
    dónde mira, lente, descripción) y `limpia()`.
  - `corte_mascaras.py` — genera `corte_gris.png`, `corte_blanco.png` y una
    `mascara_<cuarto>.png` por cuarto, deduciendo la silueta de cada cuarto por geometría
    (cuadrícula de 15 cm + flood-fill + qué cámara de `CUARTOS` cae en cada mancha).
  - `ESTADO-CATANIA.md` — bitácora larga de todo lo aplicado a la escena (terreno, mar,
    vecinas, remate al mar, giroscopio del addon, etc.) y trampas ya conocidas.
- **Referencias reales**: `clientes/Mariano/referencias_3d/ref_1_catania_por_cuarto.jpg`
  (10 fotos de los clips de Mariano) y `clientes/Mariano/de_whatsapp/video_3sep/` (frames
  sueltos de roof garden, baños, terraza, comedor).
- **Wavespeed**: `https://api.wavespeed.ai/api/v3`, llave en `.env` como
  `WAVESPEED_API_KEY` (no incluida en este documento — vive en un `.env` local, gitignored).

## Los dos bugs que ya se arreglaron (verificado en vivo el 4 sep 2026)

1. **`apunta_muros()` sólo veía 22 de ~158 muros** porque filtraba por nombre
   (`muro`/`div`). Se cambió a filtrar por geometría: delgado en planta
   (`min(dx,dy) < 0.40`) y alto (`dz > 1.50`). Confirmado en vivo: ahora detecta **112 muros**
   y los 14 cuartos (`n1_*`, `pb_*`, más `pa` y `rg` que van juntos) generan mancha.
2. **Las máscaras salían completamente NEGRAS.** `ob.color = (1,1,1,1)` es lineal, y con
   `view_transform = 'Filmic'` (el de esta escena) un blanco lineal se aplasta a ~1/255 al
   guardar el PNG — la máscara no tenía nada que ofrecerle a `genfill`. Fix: dentro de
   `modo("mascara")`, forzar antes de renderizar:
   ```python
   vs = bpy.context.scene.view_settings
   vs.view_transform = 'Standard'
   vs.look = 'None'
   vs.exposure = 0.0
   vs.gamma = 1.0
   ```
   Confirmado en vivo: las 14 máscaras ahora salen a intensidad **1.0 (blanco puro)**.

## Lo que falta — en orden

1. **Partir `pa` de `rg`.** Ahora mismo dan el MISMO área (51.1 m²) porque no hay un muro
   entre la planta alta cubierta (cocina/sala/comedor) y la terraza descubierta — es una
   sola mancha en el flood-fill. Sin partirlo, cualquier máscara del roof garden en realidad
   incluye TODA la planta alta. Idea: además de la cuadrícula en planta, probar si hay techo
   arriba de cada celda (raycast hacia +Z) — si no hay techo, es `rg`; si lo hay, es `pa`.
2. **Vestir por cuarto con `genfill`** usando las máscaras ya arregladas. Ese script
   (`bria/fibo-edit/genfill` vía Wavespeed) todavía no existe — hay que escribirlo,
   análogo a `corte_fotorrealista.py` pero recibiendo `mask_image` y UNA sola referencia
   por cuarto (no la hoja completa de 10 fotos).
3. **Correcciones puntuales ya detectadas** comparando la última generación
   (`casa_seedream_v2.png`) contra las fotos reales:
   - **Roof garden**: la referencia real (#17, "ya se ve el mar") es una banca y mesa de
     madera sobre piso claro, paredes bajas blancas — NO un lounge con sillones y sofá.
   - **Sala / estancia TV**: el sillón real es curvo, color crema/hueso — ha salido
     terracota/naranja en las generaciones.
   - **Segunda recámara**: la referencia real (#19) tiene un cabecero REDONDO color
     terracota — se ha perdido en las generaciones, sale con ropa de cama lisa.
   - **Baños, cocina, pasillo y escalera**: Catania NO TIENE video propio de estos
     espacios (confirmado en `_manda_referencias_catania.py`). Hay que vestirlos con las
     fotos de **Siena o Brescia** (misma constructora, mismo acabado) — no dejar que la
     IA los invente sin referencia.

## Qué se necesita para poder trabajar esto

- Blender abierto en la Mac de Carlos, con el panel Seedance conectado (si no, el puente
  responde 503 "Blender no está conectado").
- `WAVESPEED_API_KEY` para las llamadas de generación de imagen (`genfill`,
  `flux-controlnet-union-pro-2.0`).
- Ojo con la Trampa #2 de `ESTADO-CATANIA.md`: **"Construir/actualizar" del panel del addon
  rehace la animación de la cámara** — cualquier keyframe puesto a mano sobre
  `CAM_RECORRIDO` se pierde si se le da a Construir de nuevo.
