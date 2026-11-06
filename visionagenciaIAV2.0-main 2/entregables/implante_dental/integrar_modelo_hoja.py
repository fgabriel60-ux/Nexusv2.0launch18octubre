"""Mete el modelo 3D generado desde el panel PASO 5 de la hoja (HOJA_PASO5_hunyuan_LIGERO.glb) en la escena
CHICA_IMPLANTE_ESTILO_APROBADO, para las tomas del corte con pilar y corona.

Antes de exec() debe existir GLB_PATH (ruta local) o GLB_B64 (contenido en base64, para la Mac).
Orientación medida en las vistas de revisión: alto = Z (dientes arriba), cara del corte hacia -Y.
La escena usa la arcada SUPERIOR (dientes abajo, implante hacia arriba en x = 0), así que se gira 180°
sobre Y y se escala ~4.2 (dientes de ~1.0 e implante de ~2.2 como los de Astra).
Visible de TRAMO[0] a TRAMO[1]: pilar sin corona igual que el panel; la corona de Astra (804+) queda encima.
En ese tramo se esconden las piezas de Astra que chocan con el modelo (hueso, implante, pilar, encía,
raíces y dientes cuyo rango en X se cruza). La cara, la línea cian y la corona se conservan.
Idempotente: si ya existe AP_HOJA_Modelo lo quita y lo vuelve a colocar."""
import bpy, base64, json, math, os, tempfile
from mathutils import Vector

ESCENA = 'CHICA_IMPLANTE_ESTILO_APROBADO'
TRAMO = (765, 934)
# Prueba 1 (ESCALA 4.2, IMPLANTE_X_LOCAL -0.075): caja 3.03×3.59×3.2 correcta, pero dientes del modelo
# ~0.55 contra 1.0 de Astra e implante 0.34 a la derecha del hueco → escala ×1.8 y offset medido -0.156.
# Prueba 2 (ESCALA 7.5, -0.156): tamaño correcto; implante ~0.25 a la izquierda del hueco → -0.123.
ESCALA = 7.5
IMPLANTE_X_LOCAL = -0.123   # posición del implante en el modelo sin girar (medida en el render de prueba)
BORDE_DIENTES_Z = -1.10      # borde de los dientes del modelo en la escena
FRENTE_Y = -0.35             # cara del corte, a la altura del frente de los dientes de Astra
if 'responder' not in globals():
    def responder(d): print(json.dumps(d, ensure_ascii=False))

sc = bpy.data.scenes[ESCENA]
resultado = {'escena': ESCENA}


def llaves_constantes(o):
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = 'CONSTANT'


def oculto_en(o, f):
    ad = o.animation_data
    fc = ad.action.fcurves.find('hide_render') if ad and ad.action else None
    return bool(round(fc.evaluate(f))) if fc else o.hide_render


def esconder_en_tramo(o, a, b):
    antes_a, despues_b = oculto_en(o, a - 1), oculto_en(o, b + 1)
    for f, valor in [(a - 1, antes_a), (a, True), (b, True), (b + 1, despues_b)]:
        o.hide_render = valor; o.hide_viewport = valor
        o.keyframe_insert(data_path='hide_render', frame=f); o.keyframe_insert(data_path='hide_viewport', frame=f)
    llaves_constantes(o)


def visible_solo_en(o, a, b):
    o.animation_data_clear()
    for f, valor in [(1, True), (a - 1, True), (a, False), (b, False), (b + 1, True)]:
        o.hide_render = valor; o.hide_viewport = valor
        o.keyframe_insert(data_path='hide_render', frame=f); o.keyframe_insert(data_path='hide_viewport', frame=f)
    llaves_constantes(o)


def caja_mundo(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


# Quitar una colocación anterior
viejo = bpy.data.objects.get('AP_HOJA_Modelo')
if viejo:
    for h in list(viejo.children):
        bpy.data.objects.remove(h, do_unlink=True)
    bpy.data.objects.remove(viejo, do_unlink=True)

ruta = globals().get('GLB_PATH')
if not ruta:
    ruta = os.path.join(tempfile.gettempdir(), 'HOJA_PASO5_modelo.glb')
    open(ruta, 'wb').write(base64.b64decode(GLB_B64))

win = bpy.context.window
escena_antes = win.scene if win else None
existentes = set(bpy.data.objects)
try:
    if win:
        win.scene = sc
    bpy.ops.import_scene.gltf(filepath=ruta)
finally:
    if win:
        win.scene = escena_antes
nuevos = [o for o in bpy.data.objects if o not in existentes]
mallas = [o for o in nuevos if o.type == 'MESH']
for o in nuevos:
    if o.name not in sc.collection.all_objects:
        sc.collection.objects.link(o)
    for col in list(o.users_collection):
        if col.name not in [c.name for c in sc.collection.children_recursive] and col != sc.collection:
            col.objects.unlink(o)

# Centrar el modelo en su origen y colgarlo de un vacío que se gira, escala y coloca
mn, mx = caja_mundo(mallas)
centro = (mn + mx) / 2
padre = bpy.data.objects.new('AP_HOJA_Modelo', None)
sc.collection.objects.link(padre)
for i, o in enumerate(mallas):
    o.location -= centro
    o.parent = padre
    o.name = 'AP_HOJA_Modelo_malla_%d' % i
for o in nuevos:
    if o.type != 'MESH' and o is not padre:
        bpy.data.objects.remove(o, do_unlink=True)
padre.rotation_euler = (0.0, math.pi, 0.0)
padre.scale = (ESCALA, ESCALA, ESCALA)
# Tras girar 180° sobre Y la X local cambia de signo: el implante queda en -ESCALA*IMPLANTE_X_LOCAL del
# centro, así que el vacío va en ESCALA*IMPLANTE_X_LOCAL para dejar el implante en x = 0.
padre.location = Vector((ESCALA * IMPLANTE_X_LOCAL, 0.0, 0.0))
sc.view_layers[0].update()
mn, mx = caja_mundo(mallas)
padre.location.z += BORDE_DIENTES_Z - mn.z
padre.location.y += FRENTE_Y - mn.y
sc.view_layers[0].update()
mn, mx = caja_mundo(mallas)
visible_solo_en(padre, *TRAMO)
for o in mallas:
    visible_solo_en(o, *TRAMO)
    for m in o.data.materials:
        if m and m.use_nodes:
            p = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if p and 'Specular IOR Level' not in p.inputs and 'Specular' in p.inputs:
                p.inputs['Specular'].default_value = 0.45

# Esconder en el tramo toda la anatomía dental de Astra (mallas Y curvas: la rosca helicoidal es curva),
# salvo la corona definitiva y los dientes que quedan enteros del lado de la cara (a la izquierda de la
# línea de corte, x < CORTE_X a la altura de la boca), que siguen viéndose bajo el labio.
CORTE_X = -0.85
PREFIJOS = ('AP_Maxilar', 'AP_Hueso', 'AP_Implant', 'AP_Machined', 'AP_Healing', 'AP_Abutment', 'AP_Encía',
            'AP_Root_', 'AP_Integration_', 'AP_Natural_tooth_', 'AP_Diente_distal_', 'AP_Drill')
escondidos = []
for o in sc.objects:
    if o in mallas or o is padre or o.type not in ('MESH', 'CURVE') or not o.name.startswith(PREFIJOS):
        continue
    if o.name.startswith(('AP_Natural_tooth_', 'AP_Diente_distal_')) and caja_mundo([o])[1].x < CORTE_X:
        continue
    esconder_en_tramo(o, *TRAMO)
    escondidos.append(o.name)

resultado.update({'mallas': len(mallas), 'caras': sum(len(o.data.polygons) for o in mallas),
                  'caja_escena': [tuple(round(v, 2) for v in mn), tuple(round(v, 2) for v in mx)],
                  'tramo': TRAMO, 'escondidos_en_tramo': escondidos})
sc['MODELO_HOJA'] = json.dumps(resultado)
responder(resultado)
