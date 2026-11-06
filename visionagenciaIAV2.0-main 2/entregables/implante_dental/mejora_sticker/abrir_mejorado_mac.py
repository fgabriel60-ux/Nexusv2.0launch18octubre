import bpy,os,datetime,traceback
path='/Users/juancarlos/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_STICKER_20260915_122252.blend'
try:
 assert os.path.isfile(path)
 backup=os.path.expanduser('~/Desktop/IMPLANTE_DENTAL/SESION_ANTES_ABRIR_STICKER_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')
 assert not os.path.exists(backup)
 bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True,compress=True)
 for a in bpy.context.screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.shading.type='SOLID'
 bpy.ops.wm.open_mainfile(filepath=path,load_ui=False)
 bpy.context.window.scene=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']
 bpy.context.scene.frame_set(265)
 for a in bpy.context.screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.shading.type='SOLID'
 responder({'opened':bpy.data.filepath,'version':bpy.context.scene.get('STICKER_VERSION'),'frame':265,'backup':backup,'render_started':False})
except Exception:
 responder({'error':traceback.format_exc()});raise
finally:
 # Opening the requested saved version is the intended persistent change.
 pass
