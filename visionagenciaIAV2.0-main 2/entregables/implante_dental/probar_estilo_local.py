"""Prueba LOCAL (Blender 4.0.2, sin tocar la Mac): aplica estilo_hoja.py a una copia de
CHICA_IMPLANTE_ESTILO_APROBADO.blend y renderiza los cuadros 1, 150 y 620 con Cycles CPU a baja resolución.
Uso: blender -b CHICA_IMPLANTE_ESTILO_APROBADO.blend -P probar_estilo_local.py"""
import bpy, os

AQUI = '/workspaces/visionagenciaIAV2.0/entregables/implante_dental'
exec(open(os.path.join(AQUI, 'estilo_hoja.py')).read())
sc = bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']   # en -b no hay ventana: se renderiza con scene=
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = False
sc.render.resolution_percentage = 35
os.makedirs(os.path.join(AQUI, 'prueba_estilo'), exist_ok=True)
for f in (1, 150, 620):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(AQUI, 'prueba_estilo', 'ESTILO_%04d.png' % f)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDER', f)
