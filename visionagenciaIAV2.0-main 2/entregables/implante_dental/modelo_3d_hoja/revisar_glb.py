"""Revisa un GLB generado desde la hoja: lo importa en una escena vacía, reporta caras, tamaño y materiales,
y renderiza 3 vistas (frente, 3/4 y lado) con fondo oscuro turquesa y luz cálida + turquesa como la hoja.
Uso: blender -b --factory-startup -P revisar_glb.py -- MODELO.glb"""
import bpy, math, os, sys
from mathutils import Vector

glb = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
base = os.path.splitext(glb)[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glb)
mallas = [o for o in sc.objects if o.type == 'MESH']
caras = sum(len(o.data.polygons) for o in mallas)
pts = [o.matrix_world @ Vector(c) for o in mallas for c in o.bound_box]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
centro, tam = (mn + mx) / 2, (mx - mn)
mats = sorted({m.name for o in mallas for m in o.data.materials if m})
print('GLB', os.path.basename(glb), '| mallas', len(mallas), '| caras', caras, '| tamaño', tuple(round(x, 3) for x in tam), '| materiales', mats)

w = bpy.data.worlds.new('fondo'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.006, 0.02, 0.024, 1)
radio = max(tam) * 1.6
for nombre, col, pos, e in [('calida', (1, .72, .5), (-1, -1.2, 1), 900), ('turquesa', (.1, .78, .95), (1.2, 1, .6), 700)]:
    ld = bpy.data.lights.new(nombre, 'AREA'); ld.color = col; ld.energy = e * max(tam) ** 2; ld.size = max(tam)
    lo = bpy.data.objects.new(nombre, ld); sc.collection.objects.link(lo)
    lo.location = centro + Vector(pos) * radio
    lo.rotation_euler = (centro - lo.location).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = 'CYCLES'; sc.cycles.samples = 32; sc.cycles.use_denoising = False
sc.render.resolution_x = 640; sc.render.resolution_y = 640
for nombre, ang in [('frente', 0), ('tres_cuartos', 40), ('lado', 90)]:
    a = math.radians(ang)
    cam.location = centro + Vector((math.sin(a), -math.cos(a), 0.15)) * radio * 1.4
    cam.rotation_euler = (centro - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = '%s_%s.png' % (base, nombre)
    bpy.ops.render.render(write_still=True)
    print('VISTA', nombre)
