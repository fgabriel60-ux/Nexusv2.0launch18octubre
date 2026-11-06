"""Aligera el GLB elegido para mandarlo a la Mac por el puente HTTP (no hay archivos compartidos: todo va
en base64 dentro del script, así que 50 MB no es viable). Decima cada malla hasta CARAS_META en total,
conserva UV y texturas, reduce texturas a TEXTURA_MAX px y exporta GLB con compresión Draco si está.
Uso: PYTHONPATH=/usr/local/python/current/lib/python3.12/site-packages \
     blender -b --factory-startup -P aligerar_glb.py -- ENTRADA.glb SALIDA.glb [caras_meta]"""
import bpy, os, sys

args = sys.argv[sys.argv.index('--') + 1:]
entrada, salida = os.path.abspath(args[0]), os.path.abspath(args[1])
CARAS_META = int(args[2]) if len(args) > 2 else 60000
TEXTURA_MAX = 1024

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=entrada)
mallas = [o for o in bpy.context.scene.objects if o.type == 'MESH']
total = sum(len(o.data.polygons) for o in mallas)
ratio = min(1.0, CARAS_META / max(total, 1))
for o in mallas:
    if ratio < 1.0:
        m = o.modifiers.new('aligerar', 'DECIMATE'); m.ratio = ratio; m.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.modifier_apply(modifier=m.name)
        o.select_set(False)
for img in bpy.data.images:
    if img.size[0] > TEXTURA_MAX or img.size[1] > TEXTURA_MAX:
        f = TEXTURA_MAX / max(img.size)
        img.scale(int(img.size[0] * f), int(img.size[1] * f))
despues = sum(len(o.data.polygons) for o in mallas)
opciones = dict(filepath=salida, export_format='GLB', export_image_format='JPEG')
try:
    bpy.ops.export_scene.gltf(export_draco_mesh_compression_enable=True, **opciones)
except Exception:
    bpy.ops.export_scene.gltf(**opciones)
print('ALIGERADO', os.path.basename(entrada), 'caras', total, '->', despues,
      '| MB', round(os.path.getsize(entrada) / 1e6, 1), '->', round(os.path.getsize(salida) / 1e6, 1))
