"""Estilo de la hoja de Alberto (hoja_proceso_implante.png) sobre la escena CHICA_IMPLANTE_ESTILO_APROBADO.

Solo toca los materiales, luces y mundo AP_* de esa escena (copias; IMPLANTE_DENTAL_CINEMA queda intacta),
más un objeto nuevo AP_Boca_interior. Compatible con Blender 3.3 (Mac) y 4.x (prueba local): los nombres
de entradas del Principled cambian. Guarda los valores anteriores en scene['ESTILO_HOJA_ANTES'] para poder
deshacer. Si ya se aplicó esta versión, no la vuelve a aplicar encima (scene['ESTILO_HOJA_VERSION']).

Guía visual: GPT2_CUADRO_1_ROSTRO.png, GPT2_CUADRO_150_CLOSEUP.png y la hoja: fondo oscuro turquesa, luz
principal cálida + contraluz turquesa, piel fotográfica que reacciona a la luz, esmalte marfil, encía rosa
húmeda con borde cálido brillante, interior de boca oscuro, hueso marfil poroso, titanio satinado y línea
de corte cian.
v2 (prueba local 1): dientes salían verdosos → esmalte más cálido y menos SSS; encía gris-café → rosa más
saturada; fondo turquesa dentro de la boca → AP_Boca_interior en los cuadros con la cara completa."""
import bpy, json

VERSION = 4   # v4: dientes juntos (ANCHOS)
ESCENA = 'CHICA_IMPLANTE_ESTILO_APROBADO'
# v3: la boca de la v2 era un plano que se asomaba sobre mejillas/barbilla; ahora es una cavidad extruida
# desde el borde de los labios. Contorno de labios: y de -0.96 a 2.15; dientes: y de -0.34 a 0.58.
PROFUNDIDAD_BOCA = 2.5
if 'responder' not in globals():
    def responder(d): print(json.dumps(d, ensure_ascii=False))

sc = bpy.data.scenes[ESCENA]
antes = {}


def entrada(p, *nombres):
    for n in nombres:
        if n in p.inputs:
            return p.inputs[n]
    return None


def pon(nodo, nombres, valor, clave):
    s = entrada(nodo, *nombres)
    if s is None:
        return
    v = s.default_value
    antes.setdefault(clave + '|' + s.name, list(v) if hasattr(v, '__len__') else v)
    s.default_value = valor


def principled(m):
    return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.use_nodes else None


def borde_calido(m, color, fuerza):
    """Brillo cálido en los bordes (Layer Weight → emisión), como el contorno luminoso de la hoja."""
    nt = m.node_tree
    if 'HOJA_borde' in nt.nodes:
        nt.nodes['HOJA_borde'].inputs['Color'].default_value = (*color, 1)
        nt.nodes['HOJA_borde_escala'].inputs[1].default_value = fuerza
        return
    p = principled(m)
    salida = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    # Facing (0 de frente, 1 en el borde) → rampa 0..1 → × fuerza → intensidad de la emisión cálida
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.name = 'HOJA_borde_peso'; lw.inputs['Blend'].default_value = 0.35
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.name = 'HOJA_borde_rampa'
    ramp.color_ramp.elements[0].position = 0.55; ramp.color_ramp.elements[1].position = 0.95
    esc = nt.nodes.new('ShaderNodeMath'); esc.name = 'HOJA_borde_escala'; esc.operation = 'MULTIPLY'
    esc.inputs[1].default_value = fuerza
    em = nt.nodes.new('ShaderNodeEmission'); em.name = 'HOJA_borde'
    em.inputs['Color'].default_value = (*color, 1)
    add = nt.nodes.new('ShaderNodeAddShader'); add.name = 'HOJA_borde_suma'
    nt.links.new(lw.outputs['Facing'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], esc.inputs[0])
    nt.links.new(esc.outputs[0], em.inputs['Strength'])
    nt.links.new(p.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], salida.inputs['Surface'])


def visible_en(o, tramos):
    """Visible solo dentro de los tramos [(inicio, fin)], con claves constantes."""
    o.animation_data_clear()
    claves = {1: False}
    for a, b in tramos:
        claves[a] = True; claves[b + 1] = False
    for f, ver in sorted(claves.items()):
        o.hide_render = not ver; o.hide_viewport = not ver
        o.keyframe_insert(data_path='hide_render', frame=f); o.keyframe_insert(data_path='hide_viewport', frame=f)
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = 'CONSTANT'


resultado = {'escena': ESCENA}
if sc.get('ESTILO_HOJA_VERSION') == VERSION:
    resultado['aviso'] = 'ya aplicado, sin cambios'
else:
    if sc.get('ESTILO_HOJA_ANTES'):
        antes.update(json.loads(sc['ESTILO_HOJA_ANTES']))   # conserva los valores originales de la v1
    mats = {m.name: m for m in bpy.data.materials if m.name.startswith('AP_')}
    # Piel: menos emisión fotográfica para que la luz cálida/turquesa la modele; poro fino y SSS leve.
    piel = mats.get('AP_Piel_fotografica_con_poroso')
    if piel:
        p = principled(piel)
        pon(p, ['Roughness'], 0.42, 'piel')
        pon(p, ['Subsurface Weight', 'Subsurface'], 0.08, 'piel')
        pon(p, ['Specular IOR Level', 'Specular'], 0.45, 'piel')
        mixn = next((n for n in piel.node_tree.nodes if n.type == 'MIX_SHADER'), None)
        if mixn:
            antes.setdefault('piel|mezcla_emision', mixn.inputs[0].default_value)
            mixn.inputs[0].default_value = 0.28
        for n in piel.node_tree.nodes:
            if n.type == 'BUMP':
                antes.setdefault('piel|bump', n.inputs['Strength'].default_value); n.inputs['Strength'].default_value = 0.08
    # Esmalte marfil cálido (poca translucidez: con más, la luz turquesa lo teñía de verde).
    for nombre, color, rough, sss in [('AP_Enamel', (0.96, 0.89, 0.76), 0.18, 0.04), ('AP_Root', (0.90, 0.80, 0.64), 0.45, 0.02)]:
        m = mats.get(nombre); p = principled(m)
        if p:
            pon(p, ['Base Color'], (*color, 1), nombre)
            pon(p, ['Roughness'], rough, nombre)
            pon(p, ['Subsurface Weight', 'Subsurface'], sss, nombre)
            pon(p, ['Subsurface Color'], (1.0, 0.85, 0.65, 1), nombre)
            pon(p, ['Specular IOR Level', 'Specular'], 0.55, nombre)
            m.diffuse_color = (*color, 1)
            for n in m.node_tree.nodes:
                if n.type == 'BUMP':
                    antes.setdefault(nombre + '|bump', n.inputs['Strength'].default_value); n.inputs['Strength'].default_value = 0.03
    # Encía rosa húmeda con borde cálido.
    m = mats.get('AP_Gingiva'); p = principled(m)
    if p:
        pon(p, ['Base Color'], (0.88, 0.36, 0.40, 1), 'encia')
        pon(p, ['Roughness'], 0.28, 'encia')
        pon(p, ['Subsurface Weight', 'Subsurface'], 0.12, 'encia')
        pon(p, ['Subsurface Color'], (0.95, 0.35, 0.30, 1), 'encia')
        pon(p, ['Coat Weight', 'Clearcoat'], 0.35, 'encia')
        m.diffuse_color = (0.88, 0.36, 0.40, 1)
        borde_calido(m, (1.0, 0.50, 0.32), 1.3)
    # Hueso: cortical marfil con borde cálido; trabecular poroso marfil/café claro.
    m = mats.get('AP_Cortical'); p = principled(m)
    if p:
        pon(p, ['Base Color'], (0.92, 0.86, 0.72, 1), 'cortical')
        pon(p, ['Roughness'], 0.55, 'cortical')
        m.diffuse_color = (0.92, 0.86, 0.72, 1)
        borde_calido(m, (1.0, 0.52, 0.30), 1.2)
    m = mats.get('AP_Trabecular')
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'VALTORGB':
                antes.setdefault('trabecular|rampa', [list(e.color) for e in n.color_ramp.elements])
                n.color_ramp.elements[0].color = (0.42, 0.33, 0.22, 1)
                n.color_ramp.elements[-1].color = (0.94, 0.88, 0.74, 1)
            if n.type == 'TEX_VORONOI':
                antes.setdefault('trabecular|voronoi', n.inputs['Scale'].default_value)
                n.inputs['Scale'].default_value = max(n.inputs['Scale'].default_value, 28.0)
    # Titanio satinado.
    for nombre, color, rough in [('AP_Titanium', (0.74, 0.75, 0.77), 0.26), ('AP_Titanium_shadow', (0.36, 0.37, 0.39), 0.34)]:
        m = mats.get(nombre); p = principled(m)
        if p:
            pon(p, ['Base Color'], (*color, 1), nombre)
            pon(p, ['Metallic'], 1.0, nombre)
            pon(p, ['Roughness'], rough, nombre)
            pon(p, ['Anisotropic'], 0.35, nombre)
            m.diffuse_color = (*color, 1)
    # Línea de corte cian más limpia.
    m = mats.get('AP_Cyan_cutline')
    if m and m.use_nodes:
        e = next(n for n in m.node_tree.nodes if n.type == 'EMISSION')
        antes.setdefault('cian', [list(e.inputs[0].default_value), e.inputs[1].default_value])
        e.inputs[0].default_value = (0.30, 0.86, 0.95, 1); e.inputs[1].default_value = 3.0
    # Interior de la boca: cavidad rojo muy oscuro que sigue el contorno real de la apertura de los labios
    # (el borde abierto de la malla de la cara más cercano a los dientes), extruida hacia atrás sin
    # encogerse, así nunca se asoma fuera de los labios ni tapa los dientes. Solo con la cara completa.
    from collections import Counter
    from mathutils import Vector
    cara = sc.objects.get('CHICA_Rostro_completo_3D')
    dientes = [o for o in sc.objects if o.name.startswith(('AP_Natural_tooth', 'AP_Diente_distal'))]
    if cara and dientes:
        me_c = cara.data; mw = cara.matrix_world
        cuenta = Counter(ek for p in me_c.polygons for ek in p.edge_keys)
        vecinos = {}
        for (a, b), c in cuenta.items():
            if c == 1:
                vecinos.setdefault(a, []).append(b); vecinos.setdefault(b, []).append(a)
        lazos, vistos = [], set()
        for v0 in vecinos:
            if v0 in vistos:
                continue
            lazo, prev, cur = [v0], None, v0; vistos.add(v0)
            while True:
                sig = [n for n in vecinos[cur] if n != prev and n not in vistos]
                if not sig:
                    break
                prev, cur = cur, sig[0]; lazo.append(cur); vistos.add(cur)
            lazos.append(lazo)
        centro_d = sum((o.matrix_world @ Vector(o.bound_box[i]) for o in dientes for i in range(8)), Vector()) / (8 * len(dientes))
        grande = max(lazos, key=len)
        candidatos = [l for l in lazos if l is not grande and len(l) >= 6]
        lazo = min(candidatos, key=lambda l: ((sum((mw @ me_c.vertices[i].co for i in l), Vector()) / len(l)) - centro_d).length)
        frente = [mw @ me_c.vertices[i].co for i in lazo]
        fondo = [p + Vector((0, PROFUNDIDAD_BOCA, 0)) for p in frente]
        n = len(frente)
        caras = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)] + [tuple(range(2 * n - 1, n - 1, -1))]
        vieja = bpy.data.objects.get('AP_Boca_interior')
        if vieja:
            bpy.data.objects.remove(vieja, do_unlink=True)
        me_b = bpy.data.meshes.new('AP_Boca_interior'); me_b.from_pydata([tuple(p) for p in frente + fondo], [], caras); me_b.update()
        boca = bpy.data.objects.new('AP_Boca_interior', me_b)
        mb = bpy.data.materials.get('AP_Boca_interior') or bpy.data.materials.new('AP_Boca_interior')
        mb.use_nodes = True
        pb = principled(mb); pb.inputs['Base Color'].default_value = (0.10, 0.025, 0.025, 1)
        pb.inputs['Roughness'].default_value = 0.6; mb.diffuse_color = (0.10, 0.025, 0.025, 1)
        me_b.materials.append(mb)
        sc.collection.objects.link(boca)
        visible_en(boca, [(1, 289), (935, 1050)])
        resultado['boca_interior'] = {'vertices_labios': n, 'lazos_abiertos': len(lazos)}
    # Dientes juntos (Carlos: «no quiero que se vean tan abiertos los dientes»). Los centros están a ~1.0
    # pero cada corona medía 0.72–0.82 (y las distales 0.43–0.56): se escala cada malla en X alrededor de
    # su centro hasta el ancho que llena el espacio. Se mide el ancho actual, así aplicarlo dos veces no
    # los sigue ensanchando. Las raíces y el hueco del diente faltante (x = 0) no se tocan.
    ANCHOS = {'AP_Natural_tooth_0': 1.00, 'AP_Natural_tooth_1': 1.02, 'AP_Natural_tooth_2': 1.00,
              'AP_Natural_tooth_3': 0.98, 'AP_Definitive_crown': 1.00,
              'AP_Diente_distal_2': 0.84, 'AP_Diente_distal_0': 0.80, 'AP_Diente_distal_1': 0.60}
    anchos_hechos = {}
    for nombre, meta in ANCHOS.items():
        o = sc.objects.get(nombre)
        if not o or o.type != 'MESH':
            continue
        xs = [v.co.x for v in o.data.vertices]
        centro, ancho = (min(xs) + max(xs)) / 2, max(xs) - min(xs)
        if ancho <= 0:
            continue
        antes.setdefault('ancho|' + nombre, ancho)
        factor = meta / ancho
        for v in o.data.vertices:
            v.co.x = centro + (v.co.x - centro) * factor
        o.data.update()
        anchos_hechos[nombre] = [round(ancho, 2), meta]
    resultado['dientes_ensanchados'] = anchos_hechos
    # Mundo oscuro turquesa.
    w = sc.world
    if w and w.use_nodes:
        bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
        antes.setdefault('mundo', [list(bg.inputs[0].default_value), bg.inputs[1].default_value])
        bg.inputs[0].default_value = (0.006, 0.020, 0.024, 1); bg.inputs[1].default_value = 0.6
    # Luces: principal cálida y contraluz turquesa (desde los valores originales, no acumulando la v1).
    for nombre, factor, color in [('AP_Key', 1.9, (1.0, 0.72, 0.50)), ('AP_Teal', 1.6, (0.10, 0.78, 0.95)),
                                  ('AP_Fill', 1.0, None), ('AP_Top', 1.2, None)]:
        o = sc.objects.get(nombre)
        if o and o.type == 'LIGHT':
            original = antes.setdefault('luz|' + nombre, [o.data.energy, list(o.data.color)])
            o.data.energy = original[0] * factor
            if color:
                o.data.color = color
    # Eevee: reflejos, bloom suave y SSS.
    ee = sc.eevee
    antes.setdefault('eevee', {'ssr': ee.use_ssr, 'bloom': ee.bloom_intensity, 'soft': ee.use_soft_shadows})
    ee.use_ssr = True; ee.use_bloom = True; ee.bloom_intensity = 0.06; ee.bloom_threshold = 0.9; ee.use_soft_shadows = True
    antes.setdefault('exposicion', sc.view_settings.exposure)
    sc.view_settings.exposure = 0.0
    sc['ESTILO_HOJA_ANTES'] = json.dumps(antes)
    sc['ESTILO_HOJA_VERSION'] = VERSION
    resultado['cambios'] = len(antes)
responder(resultado)
