import bpy,os
s=bpy.data.scenes.get('CHICA_IMPLANTE_ESTILO_APROBADO')
responder({'file':bpy.data.filepath,'active_scene':bpy.context.scene.name,'frame':bpy.context.scene.frame_current,'version':s.get('STICKER_VERSION') if s else None,'versions':[(sc.name,sc.get('STICKER_VERSION')) for sc in bpy.data.scenes],'saved_exists':os.path.exists('/Users/juancarlos/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_STICKER_20260915_122252.blend')})
