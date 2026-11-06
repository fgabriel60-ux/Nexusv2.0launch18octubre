import bpy
w = bpy.context.window
responder({"version": bpy.app.version_string, "escenas": [s.name for s in bpy.data.scenes],
           "activa": bpy.context.scene.name, "motor": bpy.context.scene.render.engine,
           "archivo": bpy.data.filepath, "frame": bpy.context.scene.frame_current,
           "gpu": [(d.name, d.type) for d in bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('METAL')] if hasattr(bpy.context.preferences.addons['cycles'].preferences, 'get_devices_for_type') else "?"})
