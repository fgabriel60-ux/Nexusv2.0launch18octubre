"""Animación dental 35 s. Execute in Blender 3.3/4.x; no renders or saving here.
All operations scoped to target scene; source scene untouched. Version guard prevents duplication.
"""
import bpy,bmesh,math,json,traceback
from mathutils import Vector
VERSION='DIENTES_20260915_v3'
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];w=bpy.context.window
prior_scene=w.scene;prior_frame=s.frame_current;prior_camera=s.camera
prior_render=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.image_settings.file_format,s.render.filepath)
prior_view=(s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma)
prior_world=s.world
prior_shading=[(a.spaces.active,a.spaces.active.shading.type) for a in bpy.context.screen.areas if a.type=='VIEW_3D']
previous={o.name:{'object':o,'data':o.data,'action':o.animation_data.action if o.animation_data else None,'loc':o.location.copy(),'rot':o.rotation_euler.copy(),'scale':o.scale.copy(),'hide':o.hide_render,'hide_viewport':o.hide_viewport,'parent':o.parent} for o in s.objects}
new_objects=[];new_modifiers=[];success=False
if 'responder' not in globals():
 def responder(data):print(json.dumps(data,ensure_ascii=False))

def get(name):
 ob=s.objects.get(name)
 if ob is None:raise RuntimeError('Falta objeto '+name)
 return ob

def action(ob):
 ob.animation_data_create();ob.animation_data.action=bpy.data.actions.new('AD_'+ob.name)

def key(ob,path,values,linear=False):
 for frame,value in values:
  setattr(ob,path,value);ob.keyframe_insert(data_path=path,frame=frame)
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   if fc.data_path==path:
    for k in fc.keyframe_points:
     k.interpolation='LINEAR' if linear else 'BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'

def vis(ob,start,end=1050):
 # Visibility changes are CONSTANT; no evaluated fractional booleans.
 for path in ['hide_render','hide_viewport']:
  if ob.animation_data and ob.animation_data.action:
   for fc in list(ob.animation_data.action.fcurves):
    if fc.data_path==path:ob.animation_data.action.fcurves.remove(fc)
  for frame,value in sorted(dict([(1,True),(max(1,start-1),True),(start,False),(end,False),(end+1,True)]).items()):
   setattr(ob,path,value);ob.keyframe_insert(data_path=path,frame=frame)
  for fc in ob.animation_data.action.fcurves:
   if fc.data_path==path:
    for k in fc.keyframe_points:k.interpolation='CONSTANT'

def off(ob):
 vis(ob,1100,1101)

def mesh_obj(name,verts,faces,material):
 assert not bpy.data.objects.get(name),name
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);new_objects.append(ob)
 if material:me.materials.append(material)
 return ob

def curve_obj(name,points,radius,material):
 assert not bpy.data.objects.get(name),name
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=3
 poly=data.splines.new('POLY');poly.points.add(len(points)-1)
 for p,co in zip(poly.points,points):p.co=(*co,1)
 ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);new_objects.append(ob);data.materials.append(material);return ob

try:
 if s.get('AD_ANIM_VERSION')==VERSION:
  responder({'already_applied':True,'version':VERSION});success=True
 else:
  w.scene=s
  required=['AP_CAMERA','AP_IMPLANT_AXIS','AP_Osteotomy_rig','AP_Anesthesia_rig','AP_Healing_cap','AP_Abutment','AP_Definitive_crown','CHICA_Rostro_completo_3D','AP_Encía_orgánica','AP_Maxilar_cortical','AP_Hueso_trabecular']
  for name in required:get(name)
  # Give changed objects new actions, preserving the old actions for rollback.
  for ob in list(s.objects):
   if ob.type!='LIGHT' and ob.name!='CAM_ROSTRO_PARA_MODELAR':action(ob)
  # Broad frontal key keeps enamel, roots and bone readable during the orbit.
  ld=bpy.data.lights.new('AD_LUZ_SUAVE_FRONTAL','AREA');ld.energy=300;ld.shape='DISK';ld.size=7;ld.color=(1,.92,.82)
  lo=bpy.data.objects.new('AD_LUZ_SUAVE_FRONTAL',ld);s.collection.objects.link(lo);new_objects.append(lo);lo.location=(0,-8,5)
  lo.rotation_euler=(Vector((0,0,1.2))-lo.location).to_track_quat('-Z','Y').to_euler()
  # Exactly four natural teeth in the explanatory section; keep posterior context only in the opening.
  for i,x in enumerate([-2.04,-1.02,1.02,2.04]):
   tooth=get('AP_Natural_tooth_'+str(i));tooth.data=tooth.data.copy()
   xs=[v.co.x for v in tooth.data.vertices];delta=x-(max(xs)+min(xs))/2
   for v in tooth.data.vertices:v.co.x+=delta
   tooth.data.update();vis(tooth,1)
   root=get('AP_Root_'+str(i));root.location=(x,-.28,1.72);vis(root,350)
  # Refined crowns: a convex labial face, narrower cervical neck, rounded incisal corners.
  def replace_crown(ob,center,width,lateral=False):
   oldmat=ob.data.materials[0];verts=[];faces=[];N=40
   levels=[(-1.08,.69,.45),(-1.055,.87,.57),(-1.00,.98,.67),(-.90,1,.80),(-.65,1.01,1),(-.30,.99,1.05),(.02,.86,.90),(.23,.64,.63),(.32,.45,.45)]
   for z,rx,ry in levels:
    for j in range(N):
     a=2*math.pi*j/N;xx=math.copysign(abs(math.cos(a))**.57,math.cos(a))*width*.5*rx
     yy=math.copysign(abs(math.sin(a))**.78,math.sin(a))*.29*ry
     zz=z+(.09*abs(xx)/(width*.5) if z<-.9 else 0)
     if lateral:zz=.94*zz+.03
     # Subtle longitudinal convexity; not a flat block face.
     yy-=.025*math.cos(xx/(width*.5)*math.pi)*math.exp(-((z+.35)/.65)**2)
     verts.append((center+xx,yy-.09,zz))
   for k in range(len(levels)-1):
    for j in range(N):a=k*N+j;b=k*N+(j+1)%N;faces.append((a,b,b+N,a+N))
   faces.extend([tuple(reversed(range(N))),tuple((len(levels)-1)*N+j for j in range(N))])
   me=bpy.data.meshes.new('AD_CORONA_ANATOMICA_'+ob.name);me.from_pydata(verts,[],faces);me.update();me.materials.append(oldmat);ob.data=me
   for p in me.polygons:p.use_smooth=True
  for i,x in enumerate([-2.04,-1.02,1.02,2.04]):
   ob=get('AP_Natural_tooth_'+str(i));replace_crown(ob,x,1.08 if i in [1,2] else 1.04,lateral=i in [0,3])
   # Tapered roots with an apical curve, separate from the crown.
   root=get('AP_Root_'+str(i));material=root.data.materials[0];verts=[];faces=[];N=32
   levels=[(.30,.155),(.48,.235),(.80,.25),(1.35,.225),(1.95,.17),(2.43,.11),(2.76,.055),(2.91,.012)]
   sign=-1 if x<0 else 1
   for z,r in levels:
    bend=sign*.09*((z-.3)/2.61)**2
    for j in range(N):a=j*2*math.pi/N;verts.append((x+bend+r*math.cos(a),-.20+.70*r*math.sin(a),z))
   for k in range(len(levels)-1):
    for j in range(N):a=k*N+j;b=k*N+(j+1)%N;faces.append((a,b,b+N,a+N))
   faces.extend([tuple(reversed(range(N))),tuple((len(levels)-1)*N+j for j in range(N))])
   me=bpy.data.meshes.new('AD_RAIZ_CONICA_'+str(i));me.from_pydata(verts,[],faces);me.update();me.materials.append(material);root.data=me;root.location=(0,0,0);root.scale=(1,1,1)
   for p in me.polygons:p.use_smooth=True
   ligpoints=[(x+sign*.09*((z-.3)/2.61)**2-r,-.205,z) for z,r in levels]+[(x+sign*.09*((z-.3)/2.61)**2+r,-.205,z) for z,r in reversed(levels)]
   ligament=curve_obj('AD_LIGAMENTO_'+str(i),ligpoints,.008,bpy.data.materials['AP_Cortical']);vis(ligament,350,999)
  replace_crown(get('AP_Definitive_crown'),0,1.05)
  # Real raised trabecular struts complement the volumetric maxilla and its 3D shader.
  import random
  rng=random.Random(915)
  network=bpy.data.curves.new('AD_TRABECULAS_3D','CURVE');network.dimensions='3D';network.bevel_depth=.010;network.bevel_resolution=2
  for iz in range(9):
   for ix in range(19):
    x=-2.65+ix*.294+(iz%2)*.075;z=.85+iz*.28
    if abs(x)<.36 or z>3.43-.075*x*x:continue
    rx=rng.uniform(.09,.14);rz=rng.uniform(.09,.15)
    poly=network.splines.new('POLY');poly.points.add(6);poly.use_cyclic_u=True
    for j,p in enumerate(poly.points):
     a=2*math.pi*j/7;p.co=(x+rx*math.cos(a),.025+.014*math.sin(a*2),z+rz*math.sin(a),1)
  net=bpy.data.objects.new('AD_TRABECULAS_3D',network);s.collection.objects.link(net);new_objects.append(net);network.materials.append(bpy.data.materials['AP_Cortical']);vis(net,350,999)

  for ob in list(s.objects):
   if ob.name.startswith('AP_Diente_distal'):vis(ob,1,349)
   if ob.name.startswith('AP_HOJA_'):off(ob)
  # One continuous moving geometric cut. The face remains in place and is wiped away.
  full=get('CHICA_Rostro_completo_3D');vis(full,1,415)
  for name in ['CHICA_Rostro_final_3D','CHICA_Rostro_corte_diagonal','CHICA_Contexto_final','CHICA_Borde_corte']:
   if s.objects.get(name):off(s.objects[name])
  context=get('CHICA_Contexto_cabello_y_cuello');vis(context,1,415)
  if s.objects.get('AP_Boca_interior'):vis(get('AP_Boca_interior'),1,415)
  bpy.ops.mesh.primitive_cube_add(size=1);cutter=bpy.context.object;cutter.name='AD_CORTADOR_TRANSICION';new_objects.append(cutter)
  cutter.scale=(40,50,80);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  angle=math.atan(.18);cutter.rotation_euler[1]=angle;cutter.display_type='WIRE';cutter.hide_render=True;cutter.hide_set(True)
  offsets=[(1,20),(349,20),(350,8),(360,2),(379,-.9),(396,-4.5),(415,-20),(980,-20),(998,20),(1050,20)]
  key(cutter,'location',[(f,(x+20/math.cos(angle),0,0)) for f,x in offsets])
  for ob in [full,context]+([get('AP_Boca_interior')] if s.objects.get('AP_Boca_interior') else []):
   m=ob.modifiers.new('AD_BARRIDO_DIAGONAL','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;new_modifiers.append((ob,m))
   # Cut the smooth surface at render resolution; work viewport remains low subdivision.
  line=curve_obj('AD_LINEA_CIAN_MOVIL',[(.18*z,-5,z) for z in [-16,18]],.014,bpy.data.materials['AP_Cyan_cutline'])
  vis(line,350,414);key(line,'location',[(f,(x,0,0)) for f,x in offsets])
  # Scoped cutaway gingiva: four teeth only, without extra empty distal gum lobes.
  gum=get('AP_Encía_orgánica');vis(gum,1,349)
  cutgum=gum.copy();cutgum.data=gum.data.copy();cutgum.name='AD_ENCIA_CUATRO_DIENTES';cutgum.animation_data_clear();s.collection.objects.link(cutgum);new_objects.append(cutgum);action(cutgum)
  bm=bmesh.new();bm.from_mesh(cutgum.data)
  for x,n in [(2.68,(1,0,0)),(-2.68,(-1,0,0))]:
   result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=Vector((x,0,0)),plane_no=Vector(n),clear_outer=True)
   edges=[e for e in result['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
   if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cutgum.data);bm.free();vis(cutgum,350)
  for name in ['AP_Maxilar_cortical','AP_Hueso_trabecular']:vis(get(name),350)
  # Fine warm cortical silhouette provides reference-style rim without changing material settings.
  rim=curve_obj('AD_BORDE_HUESO_CALIDO',[(-3,.07,.66),(-3,.07,2.50),(-2.91,.07,2.79),(-2.69,.07,3.01),(-2.28,.07,3.19),(-1.49,.07,3.46),(0,.07,3.60),(1.49,.07,3.46),(2.28,.07,3.19),(2.69,.07,3.01),(2.91,.07,2.79),(3,.07,2.50),(3,.07,.66)],.012,bpy.data.materials.get('DI_Warm_edge') or bpy.data.materials['AP_Cyan_cutline']);vis(rim,350)
  # Anesthesia starts with the spoken phrase, approaches gum, pauses, then withdraws.
  syringe=get('AP_Anesthesia_rig');syringe.rotation_euler=(0,-.55,-.30)
  key(syringe,'location',[(1,(-1.5,-1.15,-1)),(199,(-1.5,-1.15,-1)),(235,(-.52,-.75,.55)),(305,(-.52,-.75,.55)),(345,(-1.7,-1.3,-1.2))])
  for ob in s.objects:
   if ob.parent==syringe:vis(ob,200,347)
  plunger=get('AP_Plunger');key(plunger,'location',[(200,(0,0,-2.22)),(236,(0,0,-2.22)),(300,(0,0,-2.10)),(347,(0,0,-2.10))])
  # Preparation: drill enters upward. Bone plug recedes with the drill tip, showing the canal being made.
  drill=get('AP_Osteotomy_rig')
  key(drill,'location',[(1,(0,0,-2.6)),(420,(0,0,-2.6)),(445,(0,0,-1.92)),(528,(0,0,.38)),(541,(0,0,.38)),(564,(0,0,-3.7))])
  key(drill,'rotation_euler',[(420,(0,0,0)),(565,(0,0,32*math.pi))],linear=True)
  for ob in s.objects:
   if ob.parent==drill:vis(ob,420,565)
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.284,depth=1,location=(0,0,1.77));plug=bpy.context.object;plug.name='AD_HUESO_EN_PREPARACION';new_objects.append(plug);plug.data.materials.append(get('AP_Hueso_trabecular').data.materials[0]);action(plug);vis(plug,350,532)
  key(plug,'scale',[(350,(1,1,2.26)),(445,(1,1,2.26)),(530,(1,1,.025))])
  key(plug,'location',[(350,(0,0,1.77)),(445,(0,0,1.77)),(530,(0,0,2.8875))])
  # Implant: guide to axis, engage and rotate upward. Tip remains superior throughout.
  implant=get('AP_IMPLANT_AXIS')
  key(implant,'location',[(1,(0,0,-2.5)),(620,(0,0,-2.5)),(640,(0,0,-2.08)),(704,(0,0,0)),(1050,(0,0,0))])
  # Rotation and advance share proportional Bezier keys, coherent with screw pitch.
  key(implant,'rotation_euler',[(620,(0,0,0)),(640,(0,0,-2.5*math.pi)),(704,(0,0,-15*math.pi)),(1050,(0,0,-15*math.pi))])
  for ob in s.objects:
   if ob.parent==implant:vis(ob,620)
  cap=get('AP_Healing_cap');vis(cap,722,878)
  key(cap,'location',[(722,(0,0,-.28)),(739,(0,0,.39)),(861,(0,0,.39)),(878,(.7,0,-.7))])
  # Bone growth is anchored in existing bone, not scaled from the world origin.
  for i,ob in enumerate(sorted([o for o in s.objects if o.name.startswith('AP_Integration')],key=lambda x:x.name)):
   ob.data=ob.data.copy();anchor=Vector(ob.data.splines[0].points[0].co[:3])
   for spline in ob.data.splines:
    for point in spline.points:
     co=Vector(point.co[:3])-anchor;point.co=(*co,1)
   ob.location=anchor;vis(ob,742+i);key(ob,'scale',[(742+i,(.001,.001,.001)),(773+i,(1,1,1))])
  # Abutment and crown enter sequentially, following the same upper-maxilla axis.
  abut=get('AP_Abutment');vis(abut,880)
  key(abut,'location',[(1,(0,0,-1.1)),(880,(0,0,-1.1)),(914,(0,0,.26)),(1050,(0,0,.26))])
  crown=get('AP_Definitive_crown');vis(crown,923)
  key(crown,'location',[(1,(0,0,-1.65)),(923,(0,0,-1.65)),(977,(0,0,0)),(1050,(0,0,0))])
  # Camera: portrait into the actual gap, modest orbit around the exposed section, final gentle retreat.
  cam=get('AP_CAMERA');cam.data=cam.data.copy();cam.data.animation_data_clear();cam.data.type='ORTHO';cam.data.sensor_fit='VERTICAL';cam.data.dof.use_dof=False
  path=[(1,(-1.3,-32,4.5),(-1.3,0,4.5),25),(105,(-.8,-30,2.8),(-.8,0,2.8),18),(150,(-.25,-28,1.15),(-.25,0,1.15),11.2),(200,(-.45,-28,1.1),(-.2,0,1.1),11.0),(345,(-.3,-28,1.2),(-.1,0,1.2),11.2),(380,(0,-28,1.3),(0,0,1.3),11.6),(420,(.6,-28,2.4),(0,0,1.20),12.0),(528,(3.4,-28,2.9),(0,0,1.2),11.5),(620,(2.2,-28,2.3),(0,0,.4),13.8),(704,(-2.8,-28,3),(0,0,1.2),11.5),(740,(-2.4,-28,2.7),(0,0,1.2),11.3),(860,(2.2,-28,2.4),(0,0,1.2),11.3),(900,(1.1,-28,2.4),(0,0,.8),12.2),(960,(.9,-28,2.2),(0,0,.6),12),(979,(.8,-28,2.4),(0,0,.9),12),(1000,(-1,-30,3.5),(-1,0,3.5),22),(1050,(-1.3,-32,4.5),(-1.3,0,4.5),25)]
  for f,loc,target,scale in path:
   cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);cam.data.keyframe_insert(data_path='ortho_scale',frame=f)
  for ac in [cam.animation_data.action,cam.data.animation_data.action]:
   for fc in ac.fcurves:
    for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
  # Brief explanatory caption makes the integration interval explicit without altering the Fish recording.
  font=bpy.data.curves.new('AD_TIEMPO_CICATRIZACION','FONT');font.body='MESES DE CICATRIZACIÓN';font.align_x='CENTER';font.size=.18
  txt=bpy.data.objects.new('AD_TIEMPO_CICATRIZACION',font);s.collection.objects.link(txt);new_objects.append(txt);font.materials.append(bpy.data.materials.get('DI_Secondary') or bpy.data.materials['AP_Cyan_cutline']);txt.parent=cam;txt.location=(0,-3.8,-7);vis(txt,740,860)
  # Carlos's follow-up requests return to the face only for the final smile.
  def opening_and_final(ob,opening_end,final_start):
   for path in ['hide_render','hide_viewport']:
    for fc in list(ob.animation_data.action.fcurves):
     if fc.data_path==path:ob.animation_data.action.fcurves.remove(fc)
    for f,v in [(1,False),(opening_end,False),(opening_end+1,True),(final_start-1,True),(final_start,False),(1050,False)]:
     setattr(ob,path,v);ob.keyframe_insert(data_path=path,frame=f)
    for fc in ob.animation_data.action.fcurves:
     if fc.data_path==path:
      for k in fc.keyframe_points:k.interpolation='CONSTANT'
  for ob in [full,context]+([get('AP_Boca_interior')] if s.objects.get('AP_Boca_interior') else []):opening_and_final(ob,415,981)
  for ob in s.objects:
   if ob.name.startswith('AP_Diente_distal'):opening_and_final(ob,349,998)
  opening_and_final(gum,349,998)
  for ob in [cutgum,rim,get('AP_Maxilar_cortical'),get('AP_Hueso_trabecular')]+[get('AP_Root_'+str(i)) for i in range(4)]:vis(ob,350,997)
  for ob in s.objects:
   if ob.name.startswith('AP_Integration'):vis(ob,742+int(ob.name.split('_')[-1]),997)

  # Markers and sequencer sound are intentionally not rebuilt.
  s['AD_ANIM_VERSION']=VERSION
  s['AD_ANIM_NOTAS']='Cara y línea desaparecen en f416; solo la cara regresa en 981-998 para la sonrisa final. Cuatro dientes naturales/raíces; quinta pieza solo al colocar corona. Preparación 420-565; implante 620-704; integración 740-860; pilar 880-914; corona 923-977. Voz existente conservada.'
  success=True
  responder({'applied':True,'version':VERSION,'objects':len(s.objects),'new_objects':[o.name for o in new_objects],'voice':[(q.name,q.frame_final_start,q.frame_final_end) for q in s.sequence_editor.sequences_all if q.type=='SOUND']})
except Exception:
 # Roll back pointers/actions and poses without replacing the live scene.
 for ob,m in new_modifiers:
  if m.name in ob.modifiers:ob.modifiers.remove(m)
 for name,p in previous.items():
  ob=p['object'];ob.data=p['data'];ob.parent=p['parent'];ob.animation_data_create();ob.animation_data.action=p['action'];ob.location=p['loc'];ob.rotation_euler=p['rot'];ob.scale=p['scale']
 for ob in reversed(new_objects):
  if ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)
 responder({'error':traceback.format_exc()});raise
finally:
 w.scene=prior_scene;s.camera=prior_camera;s.frame_set(prior_frame)
 for p in previous.values():p['object'].hide_render=p['hide'];p['object'].hide_viewport=p['hide_viewport']
 s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.image_settings.file_format,s.render.filepath=prior_render
 s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma=prior_view
 s.world=prior_world
 for space,typ in prior_shading:space.shading.type=typ
