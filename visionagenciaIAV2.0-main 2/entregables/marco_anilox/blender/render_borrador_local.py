"""Borrador del render del anilox en el Codespace (Modal sin saldo, Mac desconectada): 540×960, 16 muestras,
un cuadro sí y uno no (12 fps). armar_borrador.sh lo interpola a 24 fps y lo escala a 1080×1920.
Uso: blender -b ANILOX_MARCO.blend -P render_borrador_local.py"""
import bpy, os, time
s = bpy.data.scenes['ANILOX_MARCO_CLOSEUP']
s.render.resolution_percentage = 50
s.eevee.taa_render_samples = 16
s.render.image_settings.file_format = 'PNG'
carpeta = os.path.join(os.path.dirname(bpy.data.filepath), 'anilox_borrador')
os.makedirs(carpeta, exist_ok=True)
with bpy.context.temp_override(scene=s, view_layer=s.view_layers[0]):
    for f in range(s.frame_start, s.frame_end + 1, 2):
        ruta = os.path.join(carpeta, 'frame_%04d.png' % f)
        if os.path.exists(ruta):
            continue
        t = time.monotonic(); s.frame_set(f); s.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
        print('CUADRO', f, round(time.monotonic() - t, 1), flush=True)
