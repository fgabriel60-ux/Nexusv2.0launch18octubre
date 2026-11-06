import bpy,json,hashlib
from pathlib import Path
base=Path('/workspaces/visionagenciaIAV2.0/entregables/implante_dental/mejora_sticker')
def fingerprint():
 s=bpy.data.scenes['IMPLANTE_DENTAL_CINEMA']
 return [(o.name,o.data.name if o.data else '',tuple(o.location),tuple(o.scale),o.animation_data.action.name if o.animation_data and o.animation_data.action else '') for o in s.objects]
before=fingerprint()
PHOTO_PATH=str(base/'CHICA_MEJORADA_v2.png')
exec((base/'mejorar.py').read_text(),{'PHOTO_PATH':PHOTO_PATH,'FINAL_PHOTO_PATH':str(base/'CHICA_SONRISA_FINAL.png')})
assert fingerprint()==before
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];bpy.context.window.scene=s
checks=[]
for f in [1,240,350,365,380,395,413,415,416,620,750,950,998,1050]:
 s.frame_set(f);bpy.context.view_layer.update()
 if 416<=f<998:
  assert all(s.objects[n].hide_render for n in ['CHICA_Rostro_completo_3D','CHICA_Contexto_cabello_y_cuello','AP_Boca_interior','AD_LINEA_CIAN_MOVIL'])
  assert sum(not o.hide_render for o in s.objects if o.name.startswith('AP_Natural_tooth'))==4
 face=s.objects['CHICA_Rostro_completo_3D'];dg=bpy.context.evaluated_depsgraph_get();ev=face.evaluated_get(dg)
 checks.append({'frame':f,'face_visible':not face.hide_render,'face_min_x':min((ev.matrix_world@v.co).x for v in ev.data.vertices),'face_min_y':min((ev.matrix_world@v.co).y for v in ev.data.vertices)})
assert any(q.type=='SOUND' and q.sound.packed_file for q in s.sequence_editor.sequences_all)
n=len(s.objects);exec((base/'mejorar.py').read_text(),{'PHOTO_PATH':PHOTO_PATH,'FINAL_PHOTO_PATH':str(base/'CHICA_SONRISA_FINAL.png')});assert n==len(s.objects)
s.frame_set(620)
bpy.ops.wm.save_as_mainfile(filepath=str(base/'DENTAL_STICKER.blend'),compress=True)
(base/'verificacion.json').write_text(json.dumps({'source_unchanged':True,'idempotent':True,'voice_packed':True,'checks':checks},indent=2))
