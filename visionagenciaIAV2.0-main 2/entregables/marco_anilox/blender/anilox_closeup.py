"""Close-up del rodillo anilox de Marco (Anilox Express), paneles 2–7 del storyboard del 22 ago.

Carlos (19 sep): «en blender hagas la animación del rodillo de Marco, que se muestre lo que se dice en el audio,
con un close up, con simulación de cómo se comporta la tinta». Se hace en el Blender de la Mac por el puente.

Va en una ESCENA NUEVA («ANILOX_MARCO_CLOSEUP»): no toca la escena de la Catania ni cambia la escena activa.
Los frames usan los mismos segundos del storyboard (6–30 s a 24 fps), así cuadra con la voz de Marco.

Guion (voz de Marco) → lo que se ve. Cámara FIJA todo el tiempo, corte de la superficie con celdas hexagonales
de 60° (panal), la fila del frente partida a la mitad para ver la profundidad:
  6–12 s  «cada celda mide 25 micras; un pelo es tres veces más gordo» → baja un pelo y se acuesta junto a
          las celdas; una regla naranja mide la boca de la celda (25 µm).
 12–15 s  «la tinta sube y llena cada celda hasta el borde» → la tinta sube desde el fondo con menisco cóncavo
          (moja la cerámica), rebasa en domo y deja una película sobre las paredes.
 15–18 s  «la rasqueta cruza raspando y se lleva la que sobró» → la cuchilla cruza de derecha a izquierda,
          aplana cada domo al pasar, junta un cordón de tinta enfrente y deja limpia la cara.
 18–22 s  «el rodillo gira y deja su gota en el papel» → la tinta se parte: la mitad se va hacia arriba en un
          hilo que se estira y se rompe, la otra mitad se queda en la celda.
 22–27 s  «en el fondo se va quedando una costra seca y la celda se hace menos honda» → se vacía y la costra
          café, mate, crece desde el piso.
 27–30 s  «cabe menos tinta, y por fuera se ve idéntico» → la tinta vuelve a llenar, pero sobre la costra.

Tinta: no es FLIP (Mantaflow tardaría horas y aquí el líquido son 25 micras). Es un modelo de su conducta real:
nivel por shape keys que siguen la pared inclinada de la celda, menisco cóncavo al subir, domo convexo al
rebasar, ondas por ruido animado sólo en la superficie, cordón que crece enfrente de la rasqueta, hilo que se
estira y se rompe al transferir, y película sobre la cara que la cuchilla barre.
Uso por el puente: python3 puente.py anilox_closeup.py   ·   local: blender -b -P anilox_closeup.py -- prueba"""
import base64, math, os, sys, tempfile
import bpy, bmesh

ESC = "ANILOX_MARCO_CLOSEUP"
FPS = 24
PITCH, BOCA, PROF, FONDO = 2.9, 2.5, 1.25, 0.42      # 1 unidad = 10 µm; boca 25 µm entre caras planas
FILAS, COLS = 7, 7
LAD = 18                                            # puntos por anillo de la celda (hexágono partido en 3)
ANILLOS = 5                                         # anillos del tapón de tinta (domo/menisco)
X_INI, X_FIN = 13.0, -13.0                          # recorrido de la rasqueta


def F(t):
    return round(t * FPS)


# ---------------------------------------------------------------- geometría de la celda
def hex_perimetro(cx, cy, escala):
    """LAD puntos sobre el hexágono (punta arriba) de la boca de la celda, escalado."""
    r = BOCA / math.sqrt(3) * escala
    vs = [(cx + r * math.cos(math.radians(90 + 60 * k)), cy + r * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
    pts = []
    for k in range(6):
        (x0, y0), (x1, y1) = vs[k], vs[(k + 1) % 6]
        for j in range(LAD // 6):
            f = j / (LAD // 6)
            pts.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    return pts


def escala_en(z):
    """La pared es una pirámide truncada: la boca mide 1 y el fondo FONDO."""
    return FONDO + (1 - FONDO) * (z + PROF) / PROF


def centros():
    dy = PITCH * math.sqrt(3) / 2
    for fila in range(FILAS):
        for col in range(-(COLS // 2), COLS // 2 + 1):
            yield fila, col, col * PITCH + (PITCH / 2 if fila % 2 else 0), fila * dy


def forma_liquido(cx, cy, nivel, domo):
    """Vértices de un «tapón» de líquido dentro de la celda: fondo, pared hasta `nivel` y tapa con curvatura
    `domo` (>0 convexo, <0 menisco cóncavo). Siempre el mismo número de vértices → sirve para shape keys."""
    z0 = -PROF + 0.02
    v = [(cx, cy, z0)] + [(x, y, z0) for x, y in hex_perimetro(cx, cy, escala_en(z0))]
    s = escala_en(min(nivel, 0.0))
    for a in range(ANILLOS, 0, -1):                 # del borde hacia el centro
        f = a / ANILLOS
        z = nivel + domo * (1 - f * f)
        v += [(x, y, z) for x, y in hex_perimetro(cx, cy, s * f)]
    v.append((cx, cy, nivel + domo))
    return v


def caras_liquido(base):
    n = LAD
    c = []
    c.append([base] + [base + 1 + i for i in range(n)][::-1])        # fondo (como n-gono)
    anillos = [base + 1] + [base + 1 + n * (a + 1) for a in range(ANILLOS)]
    for a in range(ANILLOS):                        # pared (a=0) y tapa (a>0)
        r0, r1 = anillos[a], anillos[a + 1]
        for i in range(n):
            c.append([r0 + i, r0 + (i + 1) % n, r1 + (i + 1) % n, r1 + i])
    centro = base + 1 + n * (ANILLOS + 1)
    ult = anillos[-1]
    for i in range(n):
        c.append([ult + i, ult + (i + 1) % n, centro])
    return c


def malla_liquido(nombre, celdas, formas, suave=True):
    """Un objeto con varias celdas y una shape key por cada forma (nivel, domo). formas[0] es la base."""
    verts, caras = [], []
    for cx, cy in celdas:
        base = len(verts)
        verts += forma_liquido(cx, cy, *formas[0][1])
        caras += caras_liquido(base)
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(verts, [], caras)
    me.update()
    for p in me.polygons:
        p.use_smooth = suave and p.normal.z > 0.3
    ob = bpy.data.objects.new(nombre, me)
    ob.shape_key_add(name=formas[0][0])
    for nom, (nivel, domo) in formas[1:]:
        k = ob.shape_key_add(name=nom, from_mix=False)
        i = 0
        for cx, cy in celdas:
            for co in forma_liquido(cx, cy, nivel, domo):
                k.data[i].co = co
                i += 1
    # grupo de la superficie (tapa) para que las ondas no muevan las paredes
    g = ob.vertex_groups.new(name="superficie")
    por_celda = 1 + LAD * (ANILLOS + 1) + 1
    tapa = [i for i in range(len(verts)) if (i % por_celda) >= 1 + LAD * 2]
    g.add(tapa, 1.0, 'REPLACE')
    return ob


def caja(nombre, x0, x1, y0, y1, z0, z1):
    me = bpy.data.meshes.new(nombre)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
    bm.to_mesh(me); bm.free()
    return bpy.data.objects.new(nombre, me)


def huecos():
    """Las cavidades (pirámides truncadas hexagonales) que se restan a la placa de cerámica."""
    verts, caras = [], []
    for _, _, cx, cy in centros():
        b = len(verts)
        for z, s in ((-PROF, FONDO), (0.0, 1.0), (0.4, 1.0)):
            verts += [(x, y, z) for x, y in hex_perimetro(cx, cy, s)]
        n = LAD
        caras.append([b + i for i in range(n)][::-1])
        for a in range(2):
            for i in range(n):
                caras.append([b + a * n + i, b + a * n + (i + 1) % n, b + (a + 1) * n + (i + 1) % n, b + (a + 1) * n + i])
        caras.append([b + 2 * n + i for i in range(n)])
    me = bpy.data.meshes.new("ANX_huecos")
    me.from_pydata(verts, [], caras); me.update()
    return bpy.data.objects.new("ANX_huecos", me)


# ---------------------------------------------------------------- materiales
def material(nombre, color, rugosidad, metal=0.0, extra=None):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rugosidad
    p.inputs["Metallic"].default_value = metal
    if extra:
        extra(m, p)
    return m


def ceramica_extra(m, p):
    """Óxido de cromo grabado con láser: gris oscuro con micro-rugosidad."""
    nt = m.node_tree
    ru = nt.nodes.new("ShaderNodeTexNoise"); ru.inputs["Scale"].default_value = 18
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
    nt.links.new(ru.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])


def tinta_extra(m, p):
    for nombre, val in (("Coat Weight", 0.6), ("Coat Roughness", 0.04), ("Subsurface Weight", 0.08)):
        if nombre in p.inputs:
            p.inputs[nombre].default_value = val


def costra_extra(m, p):
    nt = m.node_tree
    ru = nt.nodes.new("ShaderNodeTexNoise"); ru.inputs["Scale"].default_value = 9; ru.inputs["Detail"].default_value = 8
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.8
    nt.links.new(ru.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])


def pelo_extra(m, p):
    """Cutícula del pelo: escamas en anillos."""
    nt = m.node_tree
    ola = nt.nodes.new("ShaderNodeTexWave"); ola.bands_direction = 'X'; ola.wave_profile = 'SAW'
    ola.inputs["Scale"].default_value = 1.2; ola.inputs["Distortion"].default_value = 3
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35
    nt.links.new(ola.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])


def pelicula_material(barrido):
    """Película de tinta sobre la cara del rodillo: sólo se ve donde la rasqueta todavía no pasa
    (x local del barrido < 0) y con un factor que se anima para que aparezca al rebasar."""
    m = material("ANX_pelicula", (0.95, 0.33, 0.05), 0.06, extra=tinta_extra)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]; out = nt.nodes["Material Output"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.object = barrido
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    cmp_ = nt.nodes.new("ShaderNodeMath"); cmp_.operation = 'LESS_THAN'; cmp_.inputs[1].default_value = 0.0
    fac = nt.nodes.new("ShaderNodeMath"); fac.operation = 'MULTIPLY'; fac.name = "aparece"; fac.inputs[1].default_value = 0.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], cmp_.inputs[0])
    nt.links.new(cmp_.outputs[0], fac.inputs[0])
    nt.links.new(fac.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(p.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    if hasattr(m, "blend_method"):
        m.blend_method = 'HASHED'
    return m


# ---------------------------------------------------------------- animación
def clave(ob, ruta, pares, indice=-1, interp='BEZIER'):
    for t, val in pares:
        if indice >= 0:
            getattr(ob, ruta)[indice] = val
            ob.keyframe_insert(ruta, index=indice, frame=F(t))
        else:
            setattr(ob, ruta, val)
            ob.keyframe_insert(ruta, frame=F(t))
    ad = ob.animation_data if hasattr(ob, "animation_data") else None
    if ad and ad.action and interp != 'BEZIER':
        for fc in ad.action.fcurves:
            if fc.data_path == ruta:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp


def clave_sk(ob, nombre, pares):
    kb = ob.data.shape_keys.key_blocks[nombre]
    for t, val in pares:
        kb.value = val
        kb.keyframe_insert("value", frame=F(t))


def construir():
    vieja = bpy.data.scenes.get(ESC)
    if vieja:
        bpy.data.scenes.remove(vieja)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.objects, bpy.data.textures, bpy.data.curves,
                 bpy.data.cameras, bpy.data.lights, bpy.data.worlds):
        for d in [d for d in coll if d.name.startswith("ANX_") and d.users == 0]:
            coll.remove(d)

    sc = bpy.data.scenes.new(ESC)
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = F(6), F(30)
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    motores = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in motores else "BLENDER_EEVEE"
    ee = sc.eevee
    for attr, val in (("use_gtao", True), ("use_ssr", True), ("use_bloom", False), ("taa_render_samples", 64),
                      ("use_raytracing", True), ("use_shadows", True)):
        if hasattr(ee, attr):
            setattr(ee, attr, val)
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    sc.render.filepath = "//anilox_marco_closeup/frame_"
    sc.render.image_settings.file_format = "PNG"

    w = bpy.data.worlds.new("ANX_mundo"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.014, 0.018, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sc.world = w
    col = sc.collection

    def liga(ob):
        col.objects.link(ob)
        return ob

    m_cer = material("ANX_ceramica", (0.20, 0.21, 0.22), 0.33, 0.6, ceramica_extra)
    m_tin = material("ANX_tinta", (0.95, 0.33, 0.05), 0.05, extra=tinta_extra)
    m_cos = material("ANX_costra", (0.22, 0.12, 0.05), 0.9, extra=costra_extra)
    m_ace = material("ANX_acero", (0.75, 0.76, 0.78), 0.18, 1.0)
    m_pel = material("ANX_pelo", (0.10, 0.06, 0.035), 0.45, extra=pelo_extra)
    m_reg = material("ANX_regla", (1.0, 0.42, 0.08), 0.4)
    m_reg.node_tree.nodes["Principled BSDF"].inputs["Emission Color" if "Emission Color" in m_reg.node_tree.nodes["Principled BSDF"].inputs else "Emission"].default_value = (1.0, 0.42, 0.08, 1)
    if "Emission Strength" in m_reg.node_tree.nodes["Principled BSDF"].inputs:
        m_reg.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0

    # --- placa de cerámica con el panal, cortada en la fila 0 (y=0) para ver la profundidad
    ancho = (COLS // 2 + 1) * PITCH
    placa = liga(caja("ANX_placa", -ancho, ancho, 0.0, FILAS * PITCH, -4.0, 0.0))
    hu = liga(huecos()); hu.hide_render = True; hu.hide_viewport = True
    b = placa.modifiers.new("panal", 'BOOLEAN'); b.object = hu; b.operation = 'DIFFERENCE'; b.solver = 'EXACT'
    placa.data.materials.append(m_cer)
    bv = placa.modifiers.new("bisel", 'BEVEL'); bv.width = 0.04; bv.segments = 2; bv.limit_method = 'ANGLE'

    corte = liga(caja("ANX_corte", -50, 50, -50, 0.0, -50, 50)); corte.hide_render = True; corte.hide_viewport = True

    # --- ruido animado para las ondas de la tinta
    tex = bpy.data.textures.new("ANX_ondas", 'CLOUDS'); tex.noise_scale = 0.9
    ondas = bpy.data.objects.new("ANX_ondas_mov", None); liga(ondas)
    clave(ondas, "location", [(6, 0), (30, 9)], indice=0, interp='LINEAR')
    clave(ondas, "location", [(6, 0), (30, 5)], indice=1, interp='LINEAR')

    # --- rasqueta: pivote en la línea de contacto, se inclina ~30° y cruza de derecha a izquierda
    piv = bpy.data.objects.new("ANX_rasqueta_pivote", None); liga(piv)
    piv.rotation_euler = (0, math.radians(-32), 0)
    hoja = liga(caja("ANX_rasqueta", -0.09, 0.09, -2, FILAS * PITCH + 2, 0.0, 9.0)); hoja.parent = piv
    hoja.data.materials.append(m_ace)
    clave(piv, "location", [(6, X_INI + 20)], indice=0)
    clave(piv, "location", [(6, 0), (30, 0)], indice=1)
    clave(piv, "location", [(6, 0.01), (30, 0.01)], indice=2)
    clave(piv, "location", [(14.9, X_INI), (18.0, X_FIN)], indice=0, interp='LINEAR')
    clave(piv, "location", [(18.4, X_FIN - 25)], indice=0)
    barrido = bpy.data.objects.new("ANX_barrido", None); liga(barrido)
    clave(barrido, "location", [(14.9, X_INI), (18.0, X_FIN)], indice=0, interp='LINEAR')

    # cordón de tinta que junta la rasqueta enfrente
    bpy_me = bpy.data.meshes.new("ANX_cordon")
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0); bm.to_mesh(bpy_me); bm.free()
    cordon = liga(bpy.data.objects.new("ANX_cordon", bpy_me)); cordon.parent = barrido
    for p in bpy_me.polygons:
        p.use_smooth = True
    cordon.data.materials.append(m_tin)
    cordon.location = (-0.35, FILAS * PITCH / 2, 0.0)
    clave(cordon, "scale", [(14.9, 0.05), (15.3, 0.18), (18.0, 0.55)], indice=0)
    clave(cordon, "scale", [(14.9, 0.0), (15.1, FILAS * PITCH / 2)], indice=1)
    clave(cordon, "scale", [(14.9, 0.05), (15.3, 0.16), (18.0, 0.5)], indice=2)
    cd = cordon.modifiers.new("ondas", 'DISPLACE'); cd.texture = tex; cd.strength = 0.08
    cd.texture_coords = 'OBJECT'; cd.texture_coords_object = ondas

    # película sobre la cara (rebasa al llenar, la rasqueta la barre)
    pel = liga(caja("ANX_pelicula", -ancho, ancho, 0.0, FILAS * PITCH, 0.0, 0.025))
    m_pel_tin = pelicula_material(barrido)
    pel.data.materials.append(m_pel_tin)
    nodo = m_pel_tin.node_tree.nodes["aparece"]
    for t, v in ((14.3, 0.0), (14.9, 1.0), (18.2, 1.0), (18.3, 0.0)):
        nodo.inputs[1].default_value = v
        nodo.inputs[1].keyframe_insert("default_value", frame=F(t))

    # --- tinta: un objeto por columna para que la rasqueta aplane cada domo cuando pasa
    formas_tinta = [("vacio", (-PROF + 0.03, 0.0)), ("ras", (-0.03, -0.13)), ("domo", (0.0, 0.22)),
                    ("mitad", (-PROF * 0.52, -0.16))]
    por_col = {}
    for fila, colu, cx, cy in centros():
        por_col.setdefault(colu, []).append((cx, cy))
    tintas = []
    for colu, celdas in sorted(por_col.items()):
        ob = liga(malla_liquido("ANX_tinta_col%+d" % colu, celdas, formas_tinta))
        ob.data.materials.append(m_tin)
        ob.modifiers.new("corte", 'BOOLEAN').object = corte
        ob.modifiers["corte"].operation = 'DIFFERENCE'; ob.modifiers["corte"].solver = 'EXACT'
        d = ob.modifiers.new("ondas", 'DISPLACE'); d.texture = tex; d.vertex_group = "superficie"
        d.texture_coords = 'OBJECT'; d.texture_coords_object = ondas; d.direction = 'Z'
        for t, v in ((6, 0.0), (12.2, 0.05), (14.6, 0.09), (15.5, 0.05), (18.0, 0.02), (19.0, 0.07), (21.5, 0.0),
                     (27.2, 0.05), (29.3, 0.015)):
            d.strength = v; d.keyframe_insert("strength", frame=F(t))
        cx = celdas[0][0]
        t_pasa = 14.9 + 3.1 * (X_INI - cx) / (X_INI - X_FIN)
        # Las shape keys se SUMAN sobre la base: nunca dos formas llenas a la vez, siempre se cruzan.
        # 12–15 s sube con rebote viscoso · 14.4–14.9 rebasa en domo · la rasqueta lo regresa al ras al pasar
        # 18.5–19.6 se parte (mitad al papel) · 21.6 se vacía · 27–29 vuelve a llenar sobre la costra
        clave_sk(ob, "ras", [(12.0, 0.0), (13.9, 1.04), (14.2, 0.98), (14.4, 1.0), (14.9, 0.0),
                             (t_pasa - 0.06, 0.0), (t_pasa + 0.12, 1.0), (18.5, 1.0), (19.6, 0.0),
                             (27.0, 0.0), (29.0, 1.03), (29.35, 1.0)])
        clave_sk(ob, "domo", [(14.4, 0.0), (14.9, 1.0), (t_pasa - 0.06, 1.0), (t_pasa + 0.12, 0.0)])
        clave_sk(ob, "mitad", [(18.5, 0.0), (19.6, 1.0), (20.4, 1.0), (21.6, 0.0)])
        clave(ob, "hide_render", [(6, True), (11.9, False), (21.7, True), (26.9, False)], interp='CONSTANT')
        tintas.append(ob)

    # hilos que se estiran y se rompen al transferir (sólo la fila del frente, que se ve en corte)
    for colu in (-1, 0, 1):
        me = bpy.data.meshes.new("ANX_hilo")
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.9, radius2=0.25, depth=1.0)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
        bm.to_mesh(me); bm.free()
        for p in me.polygons:
            p.use_smooth = True
        h = liga(bpy.data.objects.new("ANX_hilo%+d" % colu, me)); h.data.materials.append(m_tin)
        h.location = (colu * PITCH, PITCH * math.sqrt(3) / 2 * 0.0 + 0.9, -0.1)
        clave(h, "scale", [(18.5, 0.0), (18.6, 0.9), (19.4, 0.45), (19.8, 0.12), (19.9, 0.0)], indice=0)
        clave(h, "scale", [(18.5, 0.0), (18.6, 0.9), (19.4, 0.45), (19.8, 0.12), (19.9, 0.0)], indice=1)
        clave(h, "scale", [(18.5, 0.0), (18.6, 0.6), (19.4, 3.4), (19.85, 6.0), (19.9, 0.0)], indice=2)
        clave(h, "location", [(18.5, -0.1), (19.4, -0.3), (19.85, 1.2)], indice=2)
        clave(h, "hide_render", [(6, True), (18.5, False), (19.95, True)], interp='CONSTANT')

    # --- costra seca: crece desde el piso 22–27 s y se queda
    cos = liga(malla_liquido("ANX_costra", [(cx, cy) for _, _, cx, cy in centros()],
                             [("nada", (-PROF + 0.015, 0.0)), ("costra", (-PROF * 0.55, 0.05))], suave=False))
    cos.data.materials.append(m_cos)
    cos.modifiers.new("corte", 'BOOLEAN').object = corte
    cos.modifiers["corte"].operation = 'DIFFERENCE'; cos.modifiers["corte"].solver = 'EXACT'
    tex2 = bpy.data.textures.new("ANX_grumos", 'CLOUDS'); tex2.noise_scale = 0.35
    dc = cos.modifiers.new("grumos", 'DISPLACE'); dc.texture = tex2; dc.strength = 0.09; dc.vertex_group = "superficie"
    clave_sk(cos, "costra", [(22.3, 0.0), (26.6, 1.0)])

    # --- pelo (75 µm) que baja y se acuesta junto a las celdas; regla de 25 µm en la boca
    me = bpy.data.meshes.new("ANX_pelo")
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=3.75, radius2=3.75, depth=70)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    pelo = liga(bpy.data.objects.new("ANX_pelo", me)); pelo.data.materials.append(m_pel)
    pelo.rotation_euler = (0, math.radians(90), math.radians(22))    # acostado en diagonal detrás de la fila cortada
    clave(pelo, "location", [(6.0, 0.0)], indice=0)
    clave(pelo, "location", [(6.0, 7.5)], indice=1)
    clave(pelo, "location", [(6.2, 16.0), (7.8, 3.76), (11.2, 3.76), (12.0, 22.0)], indice=2)

    regla = liga(caja("ANX_regla", -BOCA / 2, BOCA / 2, -0.06, 0.0, -1.95, -1.83)); regla.data.materials.append(m_reg)
    for x in (-BOCA / 2, BOCA / 2):
        t = liga(caja("ANX_regla_tope", x - 0.06, x + 0.06, -0.06, 0.0, -2.15, -1.63)); t.data.materials.append(m_reg)
        t.parent = regla
    clave(regla, "scale", [(6.0, 0.0), (8.0, 0.0), (8.6, 1.0), (11.6, 1.0), (11.9, 0.0)], indice=0)
    txt_c = bpy.data.curves.new("ANX_25um", 'FONT'); txt_c.body = "25 µm"; txt_c.size = 0.55; txt_c.align_x = 'CENTER'
    txt = liga(bpy.data.objects.new("ANX_25um", txt_c)); txt.data.materials.append(m_reg)
    txt.rotation_euler = (math.radians(90), 0, 0); txt.location = (0, -0.07, -2.85)
    clave(txt, "hide_render", [(6, True), (8.6, False), (11.9, True)], interp='CONSTANT')

    # --- luces y cámara fija
    def luz(nombre, tipo, energia, loc, rot, tam=6.0, color=(1, 1, 1)):
        l = bpy.data.lights.new(nombre, tipo); l.energy = energia; l.color = color
        if tipo == 'AREA':
            l.size = tam
        o = liga(bpy.data.objects.new(nombre, l)); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
        return o
    luz("ANX_clave", 'AREA', 2600, (-9, -10, 14), (40, 0, -38), 10, (1.0, 0.93, 0.85))
    luz("ANX_relleno", 'AREA', 700, (12, -8, 5), (70, 0, 55), 8, (0.8, 0.88, 1.0))
    luz("ANX_contra", 'AREA', 1500, (0, 22, 9), (-60, 0, 180), 12)

    cam_d = bpy.data.cameras.new("ANX_cam"); cam_d.lens = 40; cam_d.sensor_fit = 'VERTICAL'
    cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 5.6
    cam = liga(bpy.data.objects.new("ANX_cam", cam_d))
    cam.location = (0.0, -13.5, 5.2)
    obj_foco = bpy.data.objects.new("ANX_foco", None); liga(obj_foco); obj_foco.location = (0, 0.6, -0.6)
    cam_d.dof.focus_object = obj_foco
    tr = cam.constraints.new('TRACK_TO'); tr.target = obj_foco; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    sc.camera = cam
    return sc


def vista_previa(sc, segundos, pct=25):
    """Renderiza unos cuadros de la escena nueva (sin volverla la activa) y los junta en una tira."""
    carpeta = tempfile.mkdtemp()
    sc.render.resolution_percentage = pct
    rutas = []
    for s in segundos:
        sc.render.filepath = os.path.join(carpeta, "p_%05.1f.png" % s)
        # render(scene=...) solo no reevalúa la animación de una escena que no está en la ventana; con
        # temp_override el contexto es la escena nueva sin cambiar lo que Carlos ve en pantalla.
        with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
            sc.frame_set(F(s))
            bpy.ops.render.render(write_still=True)
        rutas.append(sc.render.filepath)
    sc.render.resolution_percentage = 100
    sc.render.filepath = "//anilox_marco_closeup/frame_"
    imgs = [bpy.data.images.load(r) for r in rutas]
    w, h = imgs[0].size
    tira = bpy.data.images.new("ANX_tira", w * len(imgs), h)
    import array
    px = array.array('f', [0.0]) * (w * len(imgs) * h * 4)
    for k, im in enumerate(imgs):
        src = im.pixels[:]
        for y in range(h):
            a = (y * w * len(imgs) + k * w) * 4
            px[a:a + w * 4] = array.array('f', src[y * w * 4:(y + 1) * w * 4])
    tira.pixels[:] = px
    salida = os.path.join(carpeta, "tira.png")
    tira.filepath_raw = salida; tira.file_format = 'PNG'; tira.save()
    for im in imgs + [tira]:
        bpy.data.images.remove(im)
    return salida


# ---------------------------------------------------------------- ejecución segura en la sesión viva
if "responder" not in globals():
    def responder(d):
        if "png" in d:
            open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[-1])) if False else "/tmp", "anilox_tira.png"), "wb").write(base64.b64decode(d.pop("png")))
        print("RESPUESTA", d)

ventana = bpy.context.window
escena_antes = ventana.scene if ventana else None
activa_antes = bpy.context.scene
frame_antes = activa_antes.frame_current
try:
    sc = construir()
    if os.environ.get("ANX_GUARDAR"):             # sólo para el render en Modal: guarda la escena sola y sale
        for otra in [x for x in bpy.data.scenes if x != sc]:
            bpy.data.scenes.remove(otra)
        bpy.ops.wm.save_as_mainfile(filepath=os.environ["ANX_GUARDAR"])
        raise SystemExit(0)
    PREVIA = [float(x) for x in os.environ.get("ANX_PREVIA", "7.0,9.5,13.4,14.8,16.4,19.3,24.5,29.5").split(",")]
    ruta = vista_previa(sc, PREVIA, int(os.environ.get("ANX_PCT", "25")))
    responder({"ok": True, "escena": sc.name, "motor": sc.render.engine, "frames": [sc.frame_start, sc.frame_end],
               "segundos_previa": PREVIA, "png": base64.b64encode(open(ruta, "rb").read()).decode()})
except Exception as e:
    import traceback
    responder({"ok": False, "error": repr(e), "traza": traceback.format_exc()[-3000:]})
finally:
    if ventana and escena_antes and ventana.scene != escena_antes:
        ventana.scene = escena_antes
    if activa_antes.frame_current != frame_antes:
        activa_antes.frame_set(frame_antes)
