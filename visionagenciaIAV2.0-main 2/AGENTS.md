# AGENTS.md — guía para Codex en este repo

Este repo (`visionagenciaIAV2.0`) es un Codespace de trabajo para **Vision Agencia IA**.
Codex aquí se enfoca en **modelos de Blender** — específicamente el pipeline de Catania
(cliente Mariano). Para el resto del negocio (Wavespeed, WhatsApp/Nexus, GitHub multi-cuenta)
ver `DOCUMENTO_PARA_GPT6_ASTRA.md` en la raíz, que trae el panorama completo.

## Dónde está el trabajo real

El contenido del proyecto vive descomprimido en
`visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/` (no es la raíz
del repo git). Hay un symlink en `/workspaces/visionagenciaIAv2.0/VisionagenciaIAv2.0-main`
que apunta ahí — muchos scripts tienen esa ruta en minúsculas hardcodeada (`RAIZ = ...`),
así que úsala tal cual en vez de la ruta real, o los scripts no van a encontrar su `.env`.

Docs a leer primero:
- `clientes/Mariano/blender/ESTADO-CATANIA.md` — bitácora larga de todo lo aplicado a la
  escena 3D y trampas ya conocidas. **Léela antes de tocar la escena** — tiene ~10 "trampas
  que ya costaron caro" documentadas (Ctrl+Z borra lo que manda el puente, Construir/
  actualizar rehace la animación de cámara, Workbench ignora el Alpha del nodo, etc.).
- `PENDIENTES-2026-09-03.md` — pendientes activos de TODOS los clientes, no solo Catania.

## El Blender real NO está en este Codespace

`catania_LIGERA.blend` vive en la Mac de Carlos. Se opera EXCLUSIVAMENTE a través de un
puente HTTP:

```python
import json, urllib.request
d = json.dumps({"python": codigo_fuente, "meta": {"tipo": "libre"}}).encode()
r = urllib.request.Request("https://conectorblender.onrender.com/api/blender/execute",
                            data=d, headers={"Content-Type": "application/json"})
print(json.loads(urllib.request.urlopen(r, timeout=580).read()))
```

- Si Blender no está abierto con el panel Seedance conectado del lado de Carlos, esto
  responde **503** `"Blender no está conectado"`. No hay forma de arrancarlo remotamente.
- El script se ejecuta con `exec()` dentro de la sesión viva de Blender — **no hay
  `__file__`**, así que no se puede hacer `sys.path.append(os.path.dirname(__file__))`
  como hacen los `.py` del repo cuando corren via `blender -b -P`. Si un script del repo
  importa otro (p.ej. `corte_mascaras.py` importa `cuartos_camara.py`), hay que concatenar
  el código fuente de ambos en el string que se manda, no confiar en el import.
- No hay ningún archivo compartido entre este Codespace y la Mac de Carlos — todo lo que
  se necesita leer/escribir del `.blend` tiene que ir en el string de Python (usar
  `responder({"png": base64...})` para regresar imágenes, como hace `toma_de_carlos.py`).

## REGLA DE ORO: es la sesión de Blender EN VIVO de alguien

No es un archivo batch desechable — es la sesión abierta que Carlos/Mariano puede estar
viendo en su pantalla en ese momento. Cualquier script que se mande:

1. **Debe capturar el estado antes de tocar nada**: cámara activa (`scene.camera`),
   frame actual, `hide_render` de los objetos que se vayan a esconder, `scene.display.shading`,
   `scene.world` (use_nodes/color), `scene.view_settings`, resolución/formato de render.
2. **Debe envolver todo en try/except/finally** y restaurar ese estado exacto en el
   `finally`, incluso si algo falla a medio camino.
3. **Antes de una corrida completa, probar aislado.** Por ejemplo, para verificar un fix de
   color/shading no hace falta mover la cámara del recorrido ni esconder los ~1000 objetos
   de `camara_del_corte()` — basta un objeto de prueba temporal frente a la cámara actual,
   renderizar, medir, borrar el objeto, restaurar shading. Así se prueba sin arriesgar la
   escena completa.
4. Para leer un pixel/color de un render: **NO uses `bpy.data.images["Render Result"].pixels`
   directo** — a veces regresa longitud 0. Guarda con `save_render()` a un temp, cárgalo con
   `bpy.data.images.load()`, lee `.pixels` de ESA imagen, bórrala con
   `bpy.data.images.remove()`.

## Estado actual del pipeline de máscaras por cuarto (2026-09-04/05)

Ya arreglado y verificado en vivo:
- `apunta_muros()` en `corte_mascaras.py` detecta 112 muros (filtro por geometría, no por
  nombre).
- El bug de máscaras negras: `modo("mascara")` ahora fuerza
  `scene.view_settings.view_transform = 'Standard'` (con `look='None'`, `exposure=0`,
  `gamma=1`) antes de renderizar — si no, un blanco lineal se aplasta a ~1/255 al guardar
  el PNG porque la escena usa Filmic. Las 14 máscaras ya salen a intensidad 1.0.

Falta:
1. **Partir `pa` de `rg`** — hoy dan el mismo área (51.1 m²) porque no hay muro entre la
   planta alta cubierta y la terraza descubierta. Idea: raycast hacia +Z desde cada celda;
   si pega con techo es `pa`, si no es `rg`.
2. **Escribir el script de `genfill` por cuarto** (Wavespeed, `bria/fibo-edit/genfill`) —
   no existe todavía. Debe tomar UNA máscara + UNA referencia específica de ese cuarto
   (no la hoja completa de 10 fotos, que es lo que causa que la IA mezcle acabados de un
   cuarto a otro — ver `corte_fotorrealista.py` como ejemplo de lo que NO hacer).
3. Correcciones puntuales conocidas (contra las fotos reales en
   `clientes/Mariano/referencias_3d/ref_1_catania_por_cuarto.jpg`): roof garden debe llevar
   banca/mesa de madera (no sillones lounge ni sofá+TV), el sillón de sala/estancia TV es
   crema no naranja, la segunda recámara lleva cabecero redondo terracota. Baño/cocina/
   pasillo/escalera no tienen video propio de Catania — vestir con referencias de Siena o
   Brescia (misma constructora).

## Credenciales

`WAVESPEED_API_KEY` está en `/workspaces/visionagenciaIAv2.0/VisionagenciaIAv2.0-main/.env`
(gitignored). No la copies a otros archivos ni la imprimas en logs — Codex corre en este
mismo Codespace así que puede leer ese `.env` directamente cuando la necesite.
