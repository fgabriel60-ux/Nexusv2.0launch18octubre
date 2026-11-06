"""Prueba LOCAL (sin tocar la Mac): estilo_hoja.py + integrar_modelo_hoja.py sobre una copia del blend y
render Cycles de los cuadros 780 (pilar, sin corona) y 900 (con corona).
Uso: PYTHONPATH=/usr/local/python/current/lib/python3.12/site-packages \
     blender -b COPIA.blend -P probar_modelo_local.py"""
import bpy, os

AQUI = '/workspaces/visionagenciaIAV2.0/entregables/implante_dental'
exec(open(os.path.join(AQUI, 'estilo_hoja.py')).read())
GLB_PATH = os.path.join(AQUI, 'modelo_3d_hoja', 'HOJA_PASO5_hunyuan_LIGERO.glb')
exec(open(os.path.join(AQUI, 'integrar_modelo_hoja.py')).read())
sc = bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = False
sc.render.resolution_percentage = 35
os.makedirs(os.path.join(AQUI, 'prueba_modelo'), exist_ok=True)
for f in (780, 900):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(AQUI, 'prueba_modelo', 'MODELO_%04d.png' % f)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDER', f)
