"""Dental polish and baked page curl. Blender 3.3/4.x; no handlers or external dependencies.
PHOTO_PATH must name the transferred portrait. Run on an isolated copy first.
"""
import bpy, math, traceback
from mathutils import Vector
VERSION='STICKER_20260915_v3'
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];w=bpy.context.window
oldscene=w.scene;frame=s.frame_current;camera=s.camera
settings={k:getattr(s.render,k) for k in ('resolution_x','resolution_y','resolution_percentage','filepath','engine','use_sequencer')}
fmt=s.render.image_settings.file_format
view={k:getattr(s.view_settings,k) for k in ('view_transform','look','exposure','gamma')}
world=s.world;world_state=(world.use_nodes,tuple(world.color)) if world else None
shading={p.identifier:getattr(s.display.shading,p.identifier) for p in s.display.shading.bl_rna.properties if not p.is_readonly and p.type in ('BOOLEAN','INT','FLOAT','ENUM','STRING')}
spaces=[(a.spaces.active,a.spaces.active.shading.type) for a in bpy.context.screen.areas if a.type=='VIEW_3D']
before={o:(o.data,o.animation_data.action if o.animation_data else None,o.location.copy(),o.scale.copy(),o.hide_render,o.hide_viewport) for o in s.objects}
mods=[];created=[];success=False
if 'responder' not in globals():
 def responder(x):print(x)
def key(ob,path,values):
 for f,v in values:
  setattr(ob,path,v);ob.keyframe_insert(data_path=path,frame=f)
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   if fc.data_path==path:
    for k in fc.keyframe_points:
     k.interpolation='CONSTANT' if path.startswith('hide_') else 'LINEAR'
def visible(ob,a,b):
 if ob.animation_data and ob.animation_data.action:
  for fc in list(ob.animation_data.action.fcurves):
   if fc.data_path in ('hide_render','hide_viewport'):ob.animation_data.action.fcurves.remove(fc)
 for path in ('hide_render','hide_viewport'):
  key(ob,path,[(1,True),(a-1,True),(a,False),(b,False),(b+1,True)])
def copydata(ob):
 ob.data=ob.data.copy()
 if ob.animation_data and ob.animation_data.action:ob.animation_data.action=ob.animation_data.action.copy()
def mat(name,color,rough=.25,metal=0,sss=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 sub=p.inputs.get('Subsurface Weight') or p.inputs.get('Subsurface')
 if sub is not None:sub.default_value=sss
 p.inputs['Subsurface Radius'].default_value=(.7,.3,.15)
 return m
def assign(ob,m):
 copydata(ob);ob.data.materials.clear();ob.data.materials.append(m)
def cylinder(name,radius,depth,z,parent,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth)
 o=bpy.context.object;o.name=name;created.append(o);o.parent=parent;o.location=(0,0,z);o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 m=o.modifiers.new('Bordes pulidos','BEVEL');m.width=.015;m.segments=3
 visible(o,200,347);return o
def curl_point(p,edge,radius=.85):
 # A half-cylinder smoothly lifts the right edge, then folds the detached sheet back.
 d=p.x-edge
 if d<=0:return p.copy()
 a=min(math.pi,d/radius)
 q=p.copy();q.x=edge+radius*math.sin(a)-max(0,d-math.pi*radius)
 q.y=p.y-radius*(1-math.cos(a))
 return q
try:
 if s.get('STICKER_VERSION')==VERSION:
  success=True;responder({'already_applied':True})
 else:
  assert s.get('AD_ANIM_VERSION')=='DIENTES_20260915_v3'
  w.scene=s;s.frame_set(1)
  # Isolated mathematical fold test: intact left side, lifted right edge, finite coordinates.
  assert (curl_point(Vector((-1,0,0)),0)-Vector((-1,0,0))).length==0
  assert curl_point(Vector((1,0,0)),0).y<-.4
  enamel=mat('ST_Esmalte_marfil',(.92,.86,.73),.13,sss=.035)
  ep=enamel.node_tree.nodes.get('Principled BSDF');nt=enamel.node_tree
  noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=145;noise.inputs['Detail'].default_value=2
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.065;bump.inputs['Distance'].default_value=.003
  nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],ep.inputs['Normal'])
  gum=mat('ST_Encia_rosa_humeda',(.58,.15,.19),.29,sss=.07)
  gp=gum.node_tree.nodes.get('Principled BSDF');coat=gp.inputs.get('Coat Weight') or gp.inputs.get('Clearcoat')
  if coat is not None:coat.default_value=.28
  rootmat=mat('ST_Raiz_marfil',(.78,.65,.45),.34,sss=.025)
  titanium=mat('ST_Titanio_satinado',(.65,.70,.74),.23,1)
  dark=mat('ST_Titanio_oscuro',(.13,.18,.20),.28,.9)
  for ob in list(s.objects):
   if ob.name.startswith(('AP_Natural_tooth','AP_Diente_distal')) or ob.name=='AP_Definitive_crown':assign(ob,enamel)
   if ob.name in ('AP_Encía_orgánica','AD_ENCIA_CUATRO_DIENTES'):assign(ob,gum)
   if ob.name.startswith('AP_Root_'):
    assign(ob,rootmat);cx=[-2.04,-1.02,1.02,2.04][int(ob.name[-1])]
    for v in ob.data.vertices:v.co.x=cx+(v.co.x-cx)*1.27
   if ob.type in ('MESH','CURVE') and ob.data and any(m and m.name in ('AP_Titanium','AP_Titanium_shadow') for m in ob.data.materials):
    assign(ob,dark if 'flute' in ob.name.lower() else titanium)
  # Replace regular hexagon overlay by continuous irregular cellular bone relief.
  net=s.objects.get('AD_TRABECULAS_3D')
  if net:
   if net.animation_data:net.animation_data.action=net.animation_data.action.copy()
   visible(net,1100,1101)
  bone=mat('ST_Hueso_poroso',(.8,.68,.46),.52)
  nt=bone.node_tree;p=nt.nodes.get('Principled BSDF');coords=nt.nodes.new('ShaderNodeTexCoord')
  vor=nt.nodes.new('ShaderNodeTexVoronoi');vor.feature='F1';vor.inputs['Scale'].default_value=6.5;nt.links.new(coords.outputs['Object'],vor.inputs['Vector'])
  ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.24,.14,.065,1);ramp.color_ramp.elements[1].position=.48;ramp.color_ramp.elements[1].color=(.83,.70,.49,1)
  nt.links.new(vor.outputs['Distance'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
  bump=nt.nodes.new('ShaderNodeBump');bump.invert=False;bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.055;nt.links.new(vor.outputs['Distance'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
  assign(s.objects['AP_Hueso_trabecular'],bone)
  assign(s.objects['AD_HUESO_EN_PREPARACION'],bone)
  # Needle is longer and wider while preserving the animated tip's world position.
  needle=s.objects['AP_Needle'];copydata(needle)
  for v in needle.data.vertices:
   v.co.x*=1.65;v.co.y*=1.65;v.co.z=.475+(v.co.z-.475)*1.65
  for m in needle.modifiers:
   if m.type=='BEVEL':mods.append((m,'width',m.width));m.width=.004
  extra=.95*.65
  for name in ('AP_Needle_hub','AP_Syringe_barrel','AP_Syringe_inset','AP_Plunger'):
   ob=s.objects[name];copydata(ob)
   for v in ob.data.vertices:v.co.x*=1.6;v.co.y*=1.6;v.co.z-=extra
  rig=s.objects['AP_Anesthesia_rig']
  cylinder('ST_Apoyo_dedos',.28,.08,-2.04-extra,rig,titanium)
  cylinder('ST_Apoyo_pulgar',.15,.07,-2.42-extra,rig,titanium)
  for i in range(7):cylinder('ST_Graduacion_%02d'%i,.158,.012,-1.28-extra-i*.085,rig,dark)
  # Needle tip bevel is visible at render size; drill has a readable metal chuck.
  drill=s.objects['AP_Osteotomy_rig']
  chuck=cylinder('ST_Mandril_fresa',.19,.6,-.42,drill,titanium);visible(chuck,420,565)
  for i in range(5):
   o=cylinder('ST_Anillo_mandril_%02d'%i,.20,.025,-.64+i*.10,drill,dark);visible(o,420,565)
  # New photo material shared by face and context keeps the seam visually consistent.
  skin=s.objects['CHICA_Rostro_completo_3D'].data.materials[0].copy();skin.name='ST_Piel_mejorada'
  photo=bpy.data.images.load(PHOTO_PATH,check_existing=False);photo.name='ST_CHICA_MEJORADA';photo.pack()
  for n in skin.node_tree.nodes:
   if n.type=='TEX_IMAGE':n.image=photo
   if n.type=='MIX_SHADER':n.inputs[0].default_value=.90
   if n.type=='BUMP':n.inputs['Strength'].default_value=.025
   if n.type=='BSDF_PRINCIPLED':
    sub=n.inputs.get('Subsurface Weight') or n.inputs.get('Subsurface')
    if sub is not None:sub.default_value=.02
  backing=mat('ST_Reverso_sticker',(.72,.81,.80),.48)
  # A continuous UV sheet avoids seams between the landmark face and the hair context.
  # The opening uses the photograph; the complete dental model is revealed by the curl.
  for name in ['CHICA_Contexto_cabello_y_cuello','AP_Boca_interior']:
   ob=s.objects[name];copydata(ob);visible(ob,1100,1101)
  ob=s.objects['CHICA_Rostro_completo_3D'];copydata(ob)
  for m in ob.modifiers:
   mods.extend([(m,'show_viewport',m.show_viewport),(m,'show_render',m.show_render)]);m.show_viewport=False;m.show_render=False
  nx,nz=100,176;vertices=[];faces=[]
  for j in range(nz+1):
   v=j/nz
   for i in range(nx+1):
    u=i/nx;vertices.append(((u*941-550)*.017,-4.5,(947-(1-v)*1672)*.017))
  for j in range(nz):
   for i in range(nx):
    a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
  mesh=bpy.data.meshes.new('ST_Lamina_fotografica_continua');mesh.from_pydata(vertices,[],faces);mesh.update();uv=mesh.uv_layers.new(name='Photo_projection')
  for poly in mesh.polygons:
   poly.use_smooth=True
   for li in poly.loop_indices:
    idx=mesh.loops[li].vertex_index;uv.data[li].uv=(idx%(nx+1)/nx,idx//(nx+1)/nz)
  ob.data=mesh;mesh.materials.append(skin);mesh.materials.append(backing)
  # Switch to the separately generated restored smile at the final return.
  nt=skin.node_tree;tx=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
  finalphoto=bpy.data.images.load(FINAL_PHOTO_PATH,check_existing=False);finalphoto.name='ST_SONRISA_FINAL';finalphoto.pack()
  tx2=nt.nodes.new('ShaderNodeTexImage');tx2.image=finalphoto
  mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX'
  destinations=[l.to_socket for l in tx.outputs['Color'].links]
  nt.links.new(tx.outputs['Color'],mix.inputs[1]);nt.links.new(tx2.outputs['Color'],mix.inputs[2])
  for dest in destinations:nt.links.new(mix.outputs[0],dest)
  emission=nt.nodes.new('ShaderNodeEmission');emission.inputs[1].default_value=1.0
  nt.links.new(mix.outputs[0],emission.inputs[0]);out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');nt.links.new(emission.outputs[0],out.inputs['Surface'])
  for f,v in [(1,0),(980,0),(998,1),(1050,1)]:mix.inputs[0].default_value=v;mix.inputs[0].keyframe_insert(data_path='default_value',frame=f)
  sol=ob.modifiers.new('ST_Espesor_sticker','SOLIDIFY');sol.thickness=.015;sol.offset=0;sol.material_offset=1;sol.material_offset_rim=1
  ob.shape_key_add(name='Basis');worldpts=[v.co.copy() for v in mesh.vertices]
  for f in range(350,416,3):
   t=(f-350)/63;ease=t*t*(3-2*t);edge=8-23*ease
   sk=ob.shape_key_add(name='ST_Despegue_%03d'%f)
   for vert,co in zip(sk.data,worldpts):vert.co=curl_point(co,edge,1.0)
   for kf,value in [(1,0),(f-3,0),(f,1),(f+3,1 if f==413 else 0),(417,0),(980,0)]:sk.value=value;sk.keyframe_insert(data_path='value',frame=kf)
  for fc in mesh.shape_keys.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
  for path in ('hide_render','hide_viewport'):
   for fc in list(ob.animation_data.action.fcurves):
    if fc.data_path==path:ob.animation_data.action.fcurves.remove(fc)
   key(ob,path,[(1,False),(415,False),(416,True),(997,True),(998,False),(1050,False)])
  # Place the needle in front of the photographic sheet, preserving its gum target in X/Z.
  rig.animation_data.action=rig.animation_data.action.copy()
  for fc in rig.animation_data.action.fcurves:
   if fc.data_path=='location' and fc.array_index==1:
    for k in fc.keyframe_points:k.co.y-=4.6;k.handle_left.y-=4.6;k.handle_right.y-=4.6
  for o in s.objects:
   if o.name.startswith('AP_Natural_tooth_') or o.name=='AP_Definitive_crown':
    if o.name.startswith('AP_Natural'):visible(o,350,997)
  for name in ['AP_Encía_orgánica']:
   o=s.objects[name];o.animation_data.action=o.animation_data.action.copy();visible(o,1100,1101)
  for o in s.objects:
   if o.name.startswith('AP_Diente_distal'):
    o.animation_data.action=o.animation_data.action.copy();visible(o,1100,1101)
  cam=s.objects['AP_CAMERA'];copydata(cam)
  if cam.data.animation_data and cam.data.animation_data.action:
   cam.data.animation_data.action=cam.data.animation_data.action.copy()
   for fc in cam.data.animation_data.action.fcurves:
    if fc.data_path=='ortho_scale':
     for k in fc.keyframe_points:
      if k.co.y>23:k.co.y=23;k.handle_left.y=23;k.handle_right.y=23
  # Narrow studio reflections describe convex enamel and polished instruments.
  for i,loc in enumerate([(-3,-5,1.0),(3,-4,2.8)]):
   ld=bpy.data.lights.new('ST_Reflejo_esmalte_%d'%i,'AREA');ld.energy=180;ld.shape='RECTANGLE';ld.size=.8;ld.size_y=4;ld.color=(1,.92,.8)
   lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);created.append(lo);lo.location=loc;lo.rotation_euler=(Vector((0,0,.2))-lo.location).to_track_quat('-Z','Y').to_euler()
  line=s.objects['AD_LINEA_CIAN_MOVIL'];line.animation_data.action=line.animation_data.action.copy();visible(line,1100,1101)
  # Root ligaments adapt to thicker roots; no extra dental pieces.
  for i in range(4):
   ob=s.objects.get('AD_LIGAMENTO_'+str(i))
   if ob:
    copydata(ob);cx=[-2.04,-1.02,1.02,2.04][i]
    for sp in ob.data.splines:
     for p in sp.points:p.co.x=cx+(p.co.x-cx)*1.27
  for name,color,power in [('AP_Key',(1,.88,.73),420),('AP_Fill',(.72,.86,1),95),('AD_LUZ_SUAVE_FRONTAL',(1,.95,.87),360)]:
   o=s.objects[name];copydata(o);o.data.color=color;o.data.energy=power
  s['STICKER_VERSION']=VERSION;success=True
  responder({'applied':True,'version':VERSION,'needle_length_factor':1.65,'curl_frames':[350,415],'photo_packed':bool(photo.packed_file)})
except Exception:
 for m,attr,value in reversed(mods):setattr(m,attr,value)
 for o,(data,action,loc,scale,hr,hv) in before.items():
  o.data=data;o.animation_data_create();o.animation_data.action=action;o.location=loc;o.scale=scale
  for m in list(o.modifiers):
   if m.name.startswith('ST_'):o.modifiers.remove(m)
 for ob in reversed(created):bpy.data.objects.remove(ob,do_unlink=True)
 responder({'error':traceback.format_exc()});raise
finally:
 w.scene=oldscene;s.camera=camera;s.frame_set(frame)
 for o,state in before.items():o.hide_render=state[-2];o.hide_viewport=state[-1]
 for k,v in settings.items():setattr(s.render,k,v)
 s.render.image_settings.file_format=fmt
 for k,v in view.items():setattr(s.view_settings,k,v)
 s.world=world
 if world:world.use_nodes,world.color=world_state
 for k,v in shading.items():
  if v!='':setattr(s.display.shading,k,v)
 for space,typ in spaces:space.shading.type=typ
