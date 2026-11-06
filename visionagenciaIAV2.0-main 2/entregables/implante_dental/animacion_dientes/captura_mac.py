import bpy,tempfile,os,base64,traceback
s=bpy.context.scene;r=s.render;sh=s.display.shading
state=(r.resolution_percentage,r.filepath,r.image_settings.file_format,r.use_sequencer,sh.light,sh.color_type,s.frame_current)
path=None
try:
 s.frame_set(620);r.resolution_percentage=25;r.use_sequencer=False;r.image_settings.file_format='PNG'
 sh.light='STUDIO';sh.color_type='MATERIAL'
 path=os.path.join(tempfile.gettempdir(),'AD_VERIFICACION_620.png');r.filepath=path
 bpy.ops.render.opengl(write_still=True,view_context=False)
 responder({'png':base64.b64encode(open(path,'rb').read()).decode(),'frame':620,'type':'OpenGL SOLID','scene':s.name})
except Exception:
 responder({'error':traceback.format_exc()})
finally:
 r.resolution_percentage,r.filepath,r.image_settings.file_format,r.use_sequencer,sh.light,sh.color_type,f=state;s.frame_set(f)
 if path and os.path.exists(path):os.remove(path)
