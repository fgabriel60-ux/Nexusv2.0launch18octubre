import bpy, os, datetime, json, traceback
s=bpy.context.scene
try:
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    path=os.path.expanduser('~/Desktop/IMPLANTE_DENTAL/ANTES_STICKER_'+stamp+'.blend')
    assert not os.path.exists(path)
    bpy.ops.wm.save_as_mainfile(filepath=path,copy=True,compress=True)
    target=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']
    responder({'backup':path,'scene':s.name,'frame':s.frame_current,'version':target.get('AD_ANIM_VERSION'),'objects':len(target.objects),'file':bpy.data.filepath})
except Exception:
    responder({'error':traceback.format_exc()})
    raise
finally:
    pass # save copy and inventory do not change scene settings
