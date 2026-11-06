"""Renderiza en local los cuadros que no alcanzó Modal CPU (la cuenta charlyfavela1 se deshabilitó a media corrida:
«workspace … is disabled»). Mismos ajustes que render_modal_cpu.py para que no se note el empalme.
Uso: nice -n 10 blender -b DENTAL_STICKER.blend -t 2 -P render_faltantes_local.py -- 500 510"""
import bpy, os, sys, time

args = sys.argv[sys.argv.index('--') + 1:]
ini, fin = int(args[0]), int(args[1])
AQUI = os.path.dirname(bpy.data.filepath)
DEST = os.path.join(AQUI, 'cpu_final')

s = bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']; bpy.context.window.scene = s
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'
s.render.use_sequencer = False; s.render.use_compositing = False
s.render.resolution_x = 1080; s.render.resolution_y = 1920; s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGB'
s.render.use_simplify = False; s.render.film_transparent = False
s.cycles.samples = 32; s.cycles.use_adaptive_sampling = True; s.cycles.adaptive_threshold = .05
s.cycles.max_bounces = 4; s.cycles.diffuse_bounces = 2; s.cycles.glossy_bounces = 2; s.cycles.transmission_bounces = 4
s.cycles.use_denoising = True
try:
    s.cycles.denoiser = 'OPENIMAGEDENOISE'
except TypeError:
    # Sin OIDN en este build: más muestras para acercarse al ruido de los cuadros vecinos
    s.cycles.use_denoising = False; s.cycles.samples = 256
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED' and 'Subsurface Weight' in n.inputs and n.inputs['Subsurface Weight'].default_value > .5:
            n.inputs['Subsurface Weight'].default_value = .035
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = 0

os.makedirs(DEST, exist_ok=True)
for f in range(ini, fin + 1):
    ruta = os.path.join(DEST, 'frame_%04d.png' % f)
    if os.path.exists(ruta): continue
    s.frame_set(f); s.render.filepath = ruta; t = time.monotonic()
    bpy.ops.render.render(write_still=True)
    print('FALTANTE', f, round(time.monotonic() - t, 1), 's', 'denoise' if s.cycles.use_denoising else 'sin denoise', flush=True)
