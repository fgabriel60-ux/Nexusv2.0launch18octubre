"""Run locally with FACE_DATA and PHOTO_PATH; inject data + packed image for remote exec."""
import bpy,bmesh,math,os,json,traceback
from mathutils import Vector
old=bpy.context.window.scene;scene=None
try:
 source=bpy.data.scenes['IMPLANTE_DENTAL_CINEMA']
 scene=bpy.data.scenes.new('CHICA_IMPLANTE_ESTILO_APROBADO');bpy.context.window.scene=scene
 copies={};materials={}
 for ob in source.objects:
  if ob.type=='FONT' or ob.name.startswith(('DI_Portrait','DI_Progress')):continue
  copy=ob.copy()
  if ob.data:copy.data=ob.data.copy()
  copy.name='AP_'+ob.name.removeprefix('DI_');scene.collection.objects.link(copy);copies[ob.name]=copy
  if copy.animation_data and copy.animation_data.action:copy.animation_data.action=copy.animation_data.action.copy()
  if copy.type in ['MESH','CURVE']:
   for i,m in enumerate(copy.data.materials):
    if m:
     if m.name not in materials:materials[m.name]=m.copy();materials[m.name].name='AP_'+m.name.removeprefix('DI_')
     copy.data.materials[i]=materials[m.name]
 for name,ob in copies.items():
  original=source.objects.get(name)
  if original.parent:ob.parent=copies.get(original.parent.name)
 scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1080;scene.render.resolution_y=1920;scene.render.resolution_percentage=100;scene.render.fps=30;scene.frame_start=1;scene.frame_end=1050
 scene.eevee.taa_render_samples=24;scene.eevee.use_gtao=True;scene.eevee.gtao_distance=2;scene.eevee.gtao_factor=1.15;scene.eevee.use_bloom=True;scene.eevee.bloom_intensity=.045
 scene.world=source.world.copy();scene.world.name='AP_Dark_teal_studio'
 scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=-.25
 scene.render.use_simplify=True;scene.render.simplify_subdivision=0;scene.render.simplify_subdivision_render=2;scene.sync_mode='FRAME_DROP'
 def mesh(name,data,material):
  me=bpy.data.meshes.new(name);me.from_pydata(data['vertices'],[],data['faces']);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o)
  uv=me.uv_layers.new(name='Photo_projection')
  for p in me.polygons:
   p.use_smooth=True
   for li in p.loop_indices:uv.data[li].uv=data['uv'][me.loops[li].vertex_index]
  o.data.materials.append(material);return o
 def vis(o,start,end):
  for f,v in [(1,True),(max(1,start-1),True),(start,False),(end,False),(end+1,True)]:
   o.hide_render=v;o.hide_viewport=v;o.keyframe_insert(data_path='hide_render',frame=f);o.keyframe_insert(data_path='hide_viewport',frame=f)
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='CONSTANT'
 def emit(name,col,strength):
  m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);e.inputs[1].default_value=strength;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);m.diffuse_color=(*col,1);return m
 def line(name,points,r,material):
  c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;p=c.splines.new('POLY');p.points.add(len(points)-1)
  for v,co in zip(p.points,points):v.co=(*co,1)
  ob=bpy.data.objects.new(name,c);scene.collection.objects.link(ob);c.materials.append(material);return ob
 # The photographed face is used as a projected color texture on an actual landmark-fitted mesh.
 image=bpy.data.images.load(PHOTO_PATH,check_existing=False);image.name='CHICA_PIEL_FOTOGRAFICA';image.pack()
 skin=bpy.data.materials.new('AP_Piel_fotografica_con_poroso');skin.use_nodes=True;skin.diffuse_color=(.50,.24,.14,1)
 n=skin.node_tree.nodes;n.clear();links=skin.node_tree.links
 tx=n.new('ShaderNodeTexImage');tx.image=image;tx.name='TEXTURA_FOTO_APROBADA';tx.extension='EXTEND'
 p=n.new('ShaderNodeBsdfPrincipled');links.new(tx.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.5
 sub=p.inputs.get('Subsurface Weight') or p.inputs.get('Subsurface')
 if sub:sub.default_value=.05
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=180;noise.inputs['Detail'].default_value=2
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.012;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])
 em=n.new('ShaderNodeEmission');links.new(tx.outputs[0],em.inputs[0]);em.inputs[1].default_value=.9
 mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.60;links.new(p.outputs[0],mix.inputs[1]);links.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');links.new(mix.outputs[0],out.inputs['Surface']);n.active=tx
 full=mesh('CHICA_Rostro_completo_3D',FACE_DATA,skin);full['source']='Landmark fit to supplied portrait; photographed light remains in texture. Limited orbit recommended.'
 for ob in [full]:
  sub=ob.modifiers.new('Facial_smoothing','SUBSURF');sub.levels=1;sub.render_levels=2
 vis(full,1,289)
 finalface=full.copy();finalface.data=full.data;finalface.name='CHICA_Rostro_final_3D';scene.collection.objects.link(finalface);finalface.animation_data_clear();vis(finalface,935,1050)
 cutface=mesh('CHICA_Rostro_corte_diagonal',FACE_DATA,skin)
 # Bisect real geometry: x - .32*z = -.35. Open region reveals the anatomy behind the face.
 bm=bmesh.new();bm.from_mesh(cutface.data)
 ret=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=Vector((-1.2,0,0)),plane_no=Vector((1,0,-.18)),clear_outer=True,clear_inner=False)
 cutpoints=[tuple(v.co) for v in bm.verts if abs(v.co.x-.18*v.co.z+1.2)<.001]
 bm.to_mesh(cutface.data);bm.free();cutface.data.update();vis(cutface,290,934)
 sub=cutface.modifiers.new('Facial_smoothing','SUBSURF');sub.levels=1;sub.render_levels=2
 # Keep the border line subtle. Vertices follow facial depth rather than a flat screen stripe.
 cyan=emit('AP_Cyan_cutline',(.035,.50,.63),1.8)
 ordered=sorted(cutpoints,key=lambda x:x[2]);edge=line('CHICA_Borde_corte',[(x,y-.025,z) for x,y,z in ordered],.014,cyan);vis(edge,290,934)
 context=mesh('CHICA_Contexto_cabello_y_cuello',FACE_DATA['context'],skin);context['note']='Photographic surrounding context; separate from facial geometry.'
 vis(context,1,289)
 context2=context.copy();context2.name='CHICA_Contexto_final';scene.collection.objects.link(context2);context2.animation_data_clear();vis(context2,935,1050)
 # Curved open maxilla replaces rectangular cross-section slab with a tapered anatomical segment.
 # Sculpt existing rounded slab vertices into a gentler taper; no destructive edits to source scene.
 for name in ['DI_Maxilla_cortical','DI_Maxilla_section']:
  ob=copies.get(name)
  if ob:
   for v in ob.data.vertices:
    # Mesh is centered at z=2.1: narrow slightly at the root apex and curve the superior edge.
    z=v.co.z+ob.location.z
    v.co.x*=1-.09*max(0,min(1,(z-1)/2.7))
   ob.data.update()
 # Photographic enamel tone, muted gingiva, finely textured ivory bone and titanium.
 for name,m in materials.items():
  p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
  if not p:continue
  if 'Enamel' in name:p.inputs['Base Color'].default_value=(.88,.80,.65,1);p.inputs['Roughness'].default_value=.20
  if 'Gingiva' in name:p.inputs['Base Color'].default_value=(.52,.13,.11,1);p.inputs['Roughness'].default_value=.36
  if 'Cortical' in name:p.inputs['Base Color'].default_value=(.82,.74,.57,1)
  if 'Trabecular' in name:
   for node in m.node_tree.nodes:
    if node.type=='VALTORGB':node.color_ramp.elements[0].color=(.25,.18,.105,1);node.color_ramp.elements[1].color=(.86,.76,.56,1)
  m.diffuse_color=p.inputs['Base Color'].default_value[:]
 # Fill the additional visible teeth of her smile, keeping the gap at x=0.
 # Existing four anterior crowns remain; distal teeth taper behind the lip opening.
 template=copies['DI_Natural_tooth_3']
 for i,(x,y,sc) in enumerate([(2.82,.30,.68),(3.37,.55,.53),(-2.91,.55,.55)]):
  ob=template.copy();ob.data=template.data.copy();ob.name='AP_Diente_distal_%d'%i;scene.collection.objects.link(ob)
  # Template vertices already encode x=2.04.
  for v in ob.data.vertices:v.co.x=(v.co.x-2.04)*sc+x;v.co.y=(v.co.y-.212)*sc+y;v.co.z=v.co.z*sc+.2
 # Remove the old rectangular edge glow; retain only the diagonal facial section.
 outline=copies.get('DI_Section_outline')
 if outline:bpy.data.objects.remove(outline,do_unlink=True)
 cam=copies['DI_CAMERA'];scene.camera=cam;cam.animation_data_clear();cam.data.type='ORTHO';cam.data.sensor_fit='VERTICAL';cam.data.lens=70
 path=[(1,(-1.3,-32,4.5),(-1.3,0,4.5),25),(70,(-1,-30,3.8),(-1,0,3.8),22),(150,(-.25,-28,1.2),(-.25,0,1.2),11.5),(270,(-.45,-28,1.05),(-.2,0,1.05),11.5),(360,(.15,-28,1.25),(.15,0,1.25),11.5),(480,(.65,-28,1.15),(.2,0,1.15),11.5),(630,(-.45,-28,1.3),(.1,0,1.3),11.5),(750,(0,-28,1.3),(.1,0,1.3),11.5),(900,(.5,-28,1.1),(.1,0,1.1),11.5),(934,(0,-28,1.2),(0,0,1.2),11.5),(1050,(-1.3,-32,4.5),(-1.3,0,4.5),25)]
 for f,loc,target,scale in path:
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);cam.data.keyframe_insert(data_path='ortho_scale',frame=f)
 for action in [cam.animation_data.action,cam.data.animation_data.action]:
  for fc in action.fcurves:
   for k in fc.keyframe_points:k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
 # Softer studio energy: preserve ivory instead of clipping to cyan/white.
 for name,factor in [('DI_Key',.30),('DI_Fill',.08),('DI_Teal',.15),('DI_Top',.22)]:
  if name in copies:copies[name].data.energy*=factor
 # Replace the straight gum bar and spherical papillae with a continuous scalloped gingiva.
 for ob in list(scene.objects):
  if ob.name.startswith('AP_Gum_papilla') or ob.name=='AP_Gingival_margin':bpy.data.objects.remove(ob,do_unlink=True)
 vs=[];fs=[];NX=120;NR=16
 centers=[-2.9,-2.12,-1.12,0,1.02,2.04,2.82,3.37]
 for i in range(NX+1):
  x=-3.35+6.95*i/NX;d=min(abs(x-c) for c in centers);margin=.10+.28*max(0,math.cos(min(d,.5)*math.pi))**2
  centerz=(1.03+margin)/2;rz=(1.03-margin)/2
  for j in range(NR):
   a=j*2*math.pi/NR;vs.append((x,.18+.035*x*x+.58*math.sin(a),centerz+rz*math.cos(a)))
 for i in range(NX):
  for j in range(NR):a=i*NR+j;b=i*NR+(j+1)%NR;fs.append((a,b,b+NR,a+NR))
 fs.extend([tuple(reversed(range(NR))),tuple(NX*NR+j for j in range(NR))])
 me=bpy.data.meshes.new('AP_Encía_orgánica');me.from_pydata(vs,[],fs);me.update();go=bpy.data.objects.new('AP_Encía_orgánica',me);scene.collection.objects.link(go);me.materials.append(materials['DI_Gingiva'])
 for p in me.polygons:p.use_smooth=True
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.30,depth=1.8,location=(0,0,.6));tool=bpy.context.object
 bpy.context.view_layer.objects.active=go;m=go.modifiers.new('Acceso_implante','BOOLEAN');m.operation='DIFFERENCE';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True)
 # Rounded maxillary outline and open implant canal, built as closed volumes.
 outline_pts=[(-3.05,.63),(-3.05,2.5),(-2.96,2.8),(-2.72,3.03),(-2.3,3.21),(-1.5,3.48),(0,3.62),(1.5,3.48),(2.3,3.21),(2.72,3.03),(2.96,2.8),(3.05,2.5),(3.05,.63)]
 def volume(name,outline,yfront,yback,material):
  verts=[(x,y,z) for y in [yfront,yback] for x,z in outline];N=len(outline);faces=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(material)
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.29,depth=3.3,location=(0,0,1.75));tool=bpy.context.object
  bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Canal','BOOLEAN');m.operation='DIFFERENCE';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True)
  bevel=ob.modifiers.new('Bordes_anatómicos','BEVEL');bevel.width=.055;bevel.segments=3;ob.modifiers.new('Normales','WEIGHTED_NORMAL');vis(ob,290,934);return ob
 for name in ['DI_Maxilla_cortical','DI_Maxilla_section']:
  if name in copies:bpy.data.objects.remove(copies[name],do_unlink=True)
 volume('AP_Maxilar_cortical',outline_pts,.10,1.20,materials['DI_Cortical'])
 small=[(x*.947,(z-2.1)*.92+2.1) for x,z in outline_pts]
 volume('AP_Hueso_trabecular',small,.055,.11,materials['DI_Trabecular'])
 # Small variations prevent a uniform row of rectangular crowns.
 for name in ['DI_Natural_tooth_0','DI_Natural_tooth_2','DI_Natural_tooth_3']:
  ob=copies.get(name)
  if ob:
   center=sum(v.co.x for v in ob.data.vertices)/len(ob.data.vertices)
   for v in ob.data.vertices:
    v.co.x=center+(v.co.x-center)*(.88 if name.endswith('2') else .95)
    if v.co.z<-.8:v.co.z+=.10*abs(v.co.x-center)/.4
   ob.data.update()

 # Editor camera for a close-up of the entire textured face, no effect on animation.
 dc=cam.data.copy();dc.animation_data_clear();dc.ortho_scale=17
 overview=bpy.data.objects.new('CAM_ROSTRO_PARA_MODELAR',dc);scene.collection.objects.link(overview);overview.location=(-1.3,-30,4.8);overview.rotation_euler=(math.pi/2,0,0)
 for frame,label in [(1,'ROSTRO'),(150,'CLOSEUP'),(200,'ANESTESIA'),(360,'CORTE'),(420,'PREPARACION'),(620,'IMPLANTE'),(740,'INTEGRACION'),(865,'CORONA'),(1000,'SONRISA')]:scene.timeline_markers.new(label,frame=frame)
 scene['README']='Modelo de rostro para close-up, ajustado a la fotografía aprobada. Textura fotográfica UV empaquetada, boca abierta, malla de corte diagonal y anatomía separada. Giros pequeños: no es un escaneo de cabeza de 360 grados. Frame 200 rostro/anestesia; 620 corte/implante; 900 corona.'
 scene.frame_set(620)
 if LOCAL:
  bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND,check_existing=False)
 else:
  bpy.data.libraries.write(OUT_BLEND,{scene},fake_user=True,compress=True)
 result={'scene':scene.name,'objects':len(scene.objects),'face_vertices':len(full.data.vertices),'face_triangles':len(full.data.polygons),'blend':OUT_BLEND}
 if not LOCAL:responder(result)
 else:print('BUILT',json.dumps(result))
except Exception:
 if not LOCAL:responder({'error':traceback.format_exc()})
 raise
finally:
 if not LOCAL:bpy.context.window.scene=old
