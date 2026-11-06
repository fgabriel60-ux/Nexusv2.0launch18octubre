import bpy, os, json, traceback
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];frame=s.frame_current
visibility=[(o,o.hide_render,o.hide_viewport) for o in s.objects]
checks=[]
try:
 assert s.get('STICKER_VERSION')=='STICKER_20260915_v3'
 for f in [265,374,416,740,1050]:
  s.frame_set(f)
  v=[o.name for o in s.objects if not o.hide_render]
  if 416<=f<998:
   assert 'CHICA_Rostro_completo_3D' not in v
   assert sum(n.startswith('AP_Natural_tooth_') for n in v)==4
  assert 'AD_LINEA_CIAN_MOVIL' not in v
  if f==265:assert 'AP_Needle' in v and 'ST_Mandril_fresa' not in v
  checks.append({'frame':f,'face':'CHICA_Rostro_completo_3D' in v,'needle':'AP_Needle' in v,'natural_teeth':sum(n.startswith('AP_Natural_tooth_') for n in v)})
 assert bpy.data.images['ST_CHICA_MEJORADA'].packed_file
 assert bpy.data.images['ST_SONRISA_FINAL'].packed_file
 responder({'verified':True,'scene':s.name,'checks':checks,'voice_packed':any(q.type=='SOUND' and q.sound.packed_file for q in s.sequence_editor.sequences_all),'saved_file_exists':os.path.exists('/Users/juancarlos/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_STICKER_20260915_122252.blend')})
except Exception:
 responder({'error':traceback.format_exc()});raise
finally:
 s.frame_set(frame)
 for o,hr,hv in visibility:o.hide_render=hr;o.hide_viewport=hv
