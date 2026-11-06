import bpy, json
from pathlib import Path
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];bpy.context.window.scene=s
out={}
for ob in s.objects:
 if ob.type=='LIGHT' or ob.name.startswith(('CHICA_Rostro_completo','CHICA_Contexto_cabello','AP_Needle','AP_Syringe','AP_Plunger','AP_Drill','AP_Natural','AP_Root','AP_Hueso')):
  out[ob.name]={'loc':list(ob.location),'scale':list(ob.scale),'bounds':[list(v) for v in ob.bound_box],'modifiers':[(m.name,m.type) for m in ob.modifiers],'vertices':len(ob.data.vertices) if ob.type=='MESH' else None,'materials':[m.name if m else None for m in ob.data.materials] if hasattr(ob.data,'materials') else [],'energy':ob.data.energy if ob.type=='LIGHT' else None}
Path('/workspaces/visionagenciaIAV2.0/entregables/implante_dental/mejora_sticker/inventory.json').write_text(json.dumps(out,indent=2))
