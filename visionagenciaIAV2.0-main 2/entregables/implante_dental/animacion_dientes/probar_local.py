import bpy,json,os,hashlib
from pathlib import Path
base=Path('/workspaces/visionagenciaIAV2.0/entregables/implante_dental/animacion_dientes')
def fingerprint(s):
 return [(o.name,o.data.name if o.data else None,tuple(o.location),tuple(o.scale),o.hide_render,o.animation_data.action.name if o.animation_data and o.animation_data.action else None) for o in s.objects]
original=fingerprint(bpy.data.scenes['IMPLANTE_DENTAL_CINEMA'])
exec((base/'aplicar_animacion.py').read_text(),globals())
assert original==fingerprint(bpy.data.scenes['IMPLANTE_DENTAL_CINEMA']),'SOURCE CHANGED'
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];bpy.context.window.scene=s
checks=[]
for frame in [1,150,230,350,380,416,450,550,620,670,704,750,845,900,940,1000,1050]:
 s.frame_set(frame)
 visible=[o.name for o in s.objects if not o.hide_render]
 naturals=[n for n in visible if n.startswith('AP_Natural_tooth')]
 if 416<=frame<981:
  assert len(naturals)==4,(frame,naturals)
  assert not any(n.startswith('CHICA_') for n in visible),(frame,[n for n in visible if n.startswith('CHICA_')])
  assert not any(n.startswith('AP_Diente_distal') for n in visible)
  assert 'AD_LINEA_CIAN_MOVIL' not in visible
  assert all('AP_Root_'+str(i) in visible for i in range(4))
 if frame<620:assert 'AP_Implant_body' not in visible
 if 750<=frame<=845:assert 'AP_Healing_cap' in visible and 'AP_Definitive_crown' not in visible
 checks.append({'frame':frame,'natural_teeth':len(naturals),'roots':len([n for n in visible if n.startswith('AP_Root_')]),'face_visible':[n for n in visible if n.startswith('CHICA_')],'implant':'AP_Implant_body' in visible,'cap':'AP_Healing_cap' in visible,'abutment':'AP_Abutment' in visible,'crown':'AP_Definitive_crown' in visible})
assert any(q.name=='VOZ_FISH_IMPLANTE' and q.sound.packed_file for q in s.sequence_editor.sequences_all)
(base/'verificacion_local.json').write_text(json.dumps({'source_unchanged':True,'checks':checks},indent=2))
s.frame_set(620)
bpy.ops.wm.save_as_mainfile(filepath=str(base/'ANIMACION_LOCAL_VERIFICADA.blend'),check_existing=False,compress=True)
print('GEOMETRY_VERIFICATION_DONE')
