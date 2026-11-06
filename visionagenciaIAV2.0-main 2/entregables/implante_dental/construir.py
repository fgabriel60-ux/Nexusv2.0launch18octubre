"""Construcción por exec en el puente. ASSETS se inyecta como base64 por enviar.py."""
import bpy, math, os, base64, random, json, traceback
from mathutils import Vector
from math import sin,cos,pi
original=bpy.context.window.scene
original_frame=original.frame_current
original_camera=original.camera
scene=None
out=os.path.expanduser('~/Desktop/IMPLANTE_DENTAL')
os.makedirs(out,exist_ok=True)
random.seed(14)
def mat(name,color,metal=0,rough=.3,noise=0):
 m=bpy.data.materials.new('DI_'+name);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if noise:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=38;n.inputs['Detail'].default_value=3
  b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=noise;b.inputs['Distance'].default_value=.045;m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m

def emission(name,color,strength=1):
 m=bpy.data.materials.new('DI_'+name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);e.inputs[1].default_value=strength;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m

def finish(ob,name,material):
 ob.name='DI_'+name
 if material:ob.data.materials.append(material)
 if ob.type=='MESH':
  for p in ob.data.polygons:p.use_smooth=True
 return ob

def sphere(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc);o=finish(bpy.context.object,name,material);o.scale=scale;return o

def cube(name,loc,scale,material,bevel=.1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=finish(bpy.context.object,name,material);o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Rounded edges','BEVEL');b.width=bevel;b.segments=4
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def cyl(name,r,depth,loc,material,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=r,radius2=r if r2 is None else r2,depth=depth,location=loc);o=finish(bpy.context.object,name,material)
 b=o.modifiers.new('Machined edges','BEVEL');b.width=.018;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o

def line(name,pts,r,material):
 c=bpy.data.curves.new('DI_'+name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new('DI_'+name,c);scene.collection.objects.link(o);o.data.materials.append(material);return o

def empty(name,loc=(0,0,0)):
 o=bpy.data.objects.new('DI_'+name,None);scene.collection.objects.link(o);o.location=loc;return o

def key(o,prop,values):
 for f,v in values:setattr(o,prop,v);o.keyframe_insert(data_path=prop,frame=f)

def visible(o,start=1,end=1050):
 for f,v in [(1,True),(max(1,start-1),True),(start,False),(end,False),(end+1,True)]:
  o.hide_render=v;o.hide_viewport=v;o.keyframe_insert(data_path='hide_render',frame=f);o.keyframe_insert(data_path='hide_viewport',frame=f)

def tooth(name,x,y,material):
 # Upper incisor, incisal edge below and root above. Ring profile gives a rounded rectangular crown.
 levels=[(-1.03,.22,.13),(-.99,.37,.19),(-.87,.41,.235),(-.35,.40,.28),(.07,.32,.23),(.30,.20,.16)]
 vs=[];fs=[];N=48
 for z,rx,ry in levels:
  for j in range(N):
   a=2*pi*j/N;xx=math.copysign(abs(cos(a))**.55,cos(a))*rx;yy=math.copysign(abs(sin(a))**.7,sin(a))*ry
   vs.append((x+xx,y+yy,z))
 for i in range(len(levels)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;fs.append((a,b,b+N,a+N))
 fs.append(tuple(reversed(range(N))));fs.append(tuple((len(levels)-1)*N+j for j in range(N)))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('DI_'+name,me);scene.collection.objects.link(o);finish(o,name,material)
 sub=o.modifiers.new('Enamel surface','SUBSURF');sub.levels=2;return o

def cut(o,cutter):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Anatomical section','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name)

def text(name,body,x,y,size,material,start,end):
 c=bpy.data.curves.new('DI_'+name,'FONT');c.body=body;c.size=size;c.align_x='LEFT';c.space_line=1.1;c.extrude=0
 o=bpy.data.objects.new('DI_'+name,c);scene.collection.objects.link(o);o.data.materials.append(material);o.parent=cam;o.location=(x,y,-4);visible(o,start,end);return o

try:
 scene=bpy.data.scenes.new('IMPLANTE_DENTAL_CINEMA');bpy.context.window.scene=scene
 scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32;scene.eevee.use_gtao=True;scene.eevee.gtao_distance=3;scene.eevee.gtao_factor=1.15;scene.eevee.use_soft_shadows=True;scene.eevee.use_bloom=True;scene.eevee.bloom_intensity=.07
 scene.render.resolution_x=1080;scene.render.resolution_y=1920;scene.render.resolution_percentage=100;scene.render.fps=30;scene.frame_start=1;scene.frame_end=1050
 scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
 scene.world=bpy.data.worlds.new('DI_Night');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.015,.03,.035,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 enamel=mat('Enamel',(.83,.77,.61),0,.22,.06);enamel.node_tree.nodes['Principled BSDF'].inputs['Subsurface'].default_value=.09
 gum=mat('Gingiva',(.46,.085,.07),0,.32,.18);gum.node_tree.nodes['Principled BSDF'].inputs['Subsurface'].default_value=.12
 bone=mat('Trabecular',(.62,.49,.32),0,.64,.5)
 n=bone.node_tree.nodes;ln=bone.node_tree.links;p=n.get('Principled BSDF');v=n.new('ShaderNodeTexVoronoi');v.inputs['Scale'].default_value=24;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.12;r.color_ramp.elements[0].color=(.11,.07,.035,1);r.color_ramp.elements[1].position=.42;r.color_ramp.elements[1].color=(.78,.67,.47,1);ln.new(v.outputs['Distance'],r.inputs[0]);ln.new(r.outputs[0],p.inputs['Base Color'])
 cortical=mat('Cortical',(.85,.75,.55),0,.5,.16);rootmat=mat('Root',(.63,.48,.28),0,.42,.1)
 metal=mat('Titanium',(.45,.55,.59),.92,.26,.09);darkmetal=mat('Titanium_shadow',(.09,.13,.15),.9,.3)
 cyan=emission('Cyan_edge',(.05,.65,.74),2);warm=emission('Warm_edge',(1,.27,.075),1.2);white=emission('Typography',(.93,.94,.89));dim=emission('Secondary',(.41,.69,.72))
 black=mat('Backdrop',(.004,.013,.018),0,.9)
 # Genuine open section of the upper maxillary segment. Rounded boundaries, central canal.
 slab=cube('Maxilla_cortical',(0,.63,2.1),(5.8,1.6,3.15),cortical,.32)
 inner=cube('Maxilla_section',(0,.045,2.10),(5.47,.07,2.81),bone,.24)
 channel=cyl('Canal_cutter',.29,3.3,(0,0,1.75),None)
 for o in [slab,inner]:cut(o,channel)
 bpy.data.objects.remove(channel,do_unlink=True)
 # Remove anterior half so channel and screw remain readable from the front.
 cutter=cube('Cutaway_tool',(0,-1,2),(6.5,2.16,4.5),None,0)
 cut(slab,cutter);bpy.data.objects.remove(cutter,do_unlink=True)
 gumob=cube('Gingival_margin',(0,.45,.39),(5.85,1.55,.65),gum,.25)
 channel=cyl('Gum_access',.3,1.2,(0,0,.35),None);cut(gumob,channel);bpy.data.objects.remove(channel,do_unlink=True)
 for i,x in enumerate([-2.12,-1.12,1.02,2.04]):
  tooth('Natural_tooth_%s'%i,x,-.11+.05*abs(x),enamel)
  root=sphere('Root_%s'%i,(x,-.28,1.72),(.20,.13,1.16),rootmat)
  visible(root,300,934)
 for o in [slab,inner]:visible(o,290,934)
 # Edge highlight traces the section; modest emission like reference sheet.
 edge=line('Section_outline',[(-2.85,-.28,.63),(-2.85,-.28,3.40),(-2.58,-.28,3.65),(2.58,-.28,3.65),(2.85,-.28,3.40),(2.85,-.28,.63)],.014,cyan);visible(edge,290,934)
 for x in [-2.12,-1.12,1.02,2.04]:
  o=sphere('Gum_papilla',(x+.4,-.25,.22),(.18,.20,.26),gum)
 # Threaded implant, anatomically points upward into upper jaw.
 rig=empty('IMPLANT_AXIS');body=cyl('Implant_body',.215,2.16,(0,0,1.63),metal,r2=.14);body.parent=rig
 pts=[]
 for j in range(1000):
  t=j/999;z=.57+2.1*t;rr=.235-.07*t;a=2*pi*13*t;pts.append((rr*cos(a),rr*sin(a),z))
 thread=line('Machined_helical_thread',pts,.045,metal);thread.parent=rig
 collar=cyl('Implant_collar',.25,.19,(0,0,.52),metal);collar.parent=rig
 socket=cyl('Connector_socket',.11,.015,(0,0,.417),darkmetal);socket.parent=rig
 for o in [body,thread,collar,socket]:visible(o,481,934)
 key(rig,'location',[(481,(0,0,-3.3)),(506,(0,0,-2.5)),(620,(0,0,0)),(1050,(0,0,0))]);key(rig,'rotation_euler',[(481,(0,0,0)),(620,(0,0,-26*pi))])
 healing=cyl('Healing_cap',.23,.18,(0,0,.39),metal);visible(healing,631,762)
 abut=cyl('Abutment',.18,.51,(0,0,.26),metal,r2=.12);visible(abut,765,1050);key(abut,'location',[(765,(0,0,-1.25)),(801,(0,0,.26))])
 crown=tooth('Definitive_crown',0,0,enamel);visible(crown,804,1050);key(crown,'location',[(804,(0,0,-1.5)),(879,(0,0,0))])
 # Integration shown by fine trabecular links growing toward the thread, not a magical solid fill.
 for i in range(55):
  z=random.uniform(.72,2.70);sgn=random.choice([-1,1]);x=sgn*random.uniform(.28,.55)
  o=line('Integration_%02d'%i,[(x,-.13,z),(sgn*.215,-.09,z+.035)],.012,cortical);visible(o,655+i,934)
  key(o,'scale',[(650+i,(.01,.01,.01)),(700+i,(1,1,1))])
 # Anesthesia prop: barrel and fine needle, anchored beside gum.
 syringe=empty('Anesthesia_rig',(-.52,-.75,.55));syringe.rotation_euler=(0,-.55,-.30)
 for ob in [cyl('Needle',.014,.95,(0,0,-.48),metal),cyl('Needle_hub',.055,.20,(0,0,-1.05),metal),cyl('Syringe_barrel',.095,.90,(0,0,-1.60),metal),cyl('Syringe_inset',.097,.52,(0,0,-1.55),dim),cyl('Plunger',.035,.40,(0,0,-2.22),metal)]:
  ob.parent=syringe;visible(ob,151,268)
 key(syringe,'location',[(151,(-1.2,-1.1,-.45)),(188,(-.52,-.75,.55)),(235,(-.52,-.75,.55)),(268,(-1.2,-1.1,-.45))])
 # Tool approaches from below along upper maxilla axis, with restrained metal flutes.
 drill=empty('Osteotomy_rig');shaft=cyl('Drill_shaft',.075,2.5,(0,0,1.1),metal,r2=.045);shaft.parent=drill
 handle=cyl('Handpiece',.22,1.15,(0,0,-.65),metal);handle.parent=drill
 for k in range(2):
  pts=[(.082*cos(t*.09+k*pi),.082*sin(t*.09+k*pi),.1+t*.018) for t in range(125)];o=line('Drill_flute',pts,.012,darkmetal);o.parent=drill;visible(o,361,480)
 for o in [shaft,handle]:visible(o,361,480)
 key(drill,'location',[(361,(0,0,-2.5)),(390,(0,0,-1.5)),(448,(0,0,.10)),(480,(0,0,-3.8))]);key(drill,'rotation_euler',[(361,(0,0,0)),(480,(0,0,30*pi))])
 # Cinematic camera: mild arcs, no spin, lens fixed for readable screen typography.
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='DI_CAMERA';cam.data.lens=48;cam.data.sensor_fit='HORIZONTAL';scene.camera=cam
 path=[(1,(.1,-18,3.7),(0,0,1.2)),(90,(.1,-15,2.8),(0,0,.7)),(150,(-.7,-13.9,2.3),(0,0,.65)),(270,(-1.2,-13.2,2.4),(0,0,.8)),(360,(1,-14.5,3.5),(0,0,1.35)),(480,(1.45,-14,3.2),(0,0,1.35)),(620,(-1.35,-13.9,3.5),(0,0,1.35)),(750,(-.8,-13.5,3.3),(0,0,1.35)),(840,(1,-14,2.7),(0,0,1.1)),(934,(.15,-15.1,3),(0,0,1.2)),(1050,(0,-18,3.7),(0,0,1.2))]
 for f,loc,target in path:
  cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
 # Image cards in camera space preserve the woman's actual identity; macro is visibly a diagram.
 def card(keyname,name,start,end,zoomkeys):
  payload=ASSETS[keyname];path=os.path.join(out,name+'.jpg');open(path,'wb').write(base64.b64decode(payload));im=bpy.data.images.load(path,check_existing=False);im.pack()
  m=bpy.data.materials.new('DI_'+name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();tx=n.new('ShaderNodeTexImage');tx.image=im;e=n.new('ShaderNodeEmission');output=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(tx.outputs['Color'],e.inputs[0]);m.node_tree.links.new(e.outputs[0],output.inputs[0])
  bpy.ops.mesh.primitive_plane_add(size=2);o=finish(bpy.context.object,name,m);o.parent=cam;o.location=(0,0,-5);ratio=im.size[0]/im.size[1];h=6.6667;w=h*ratio;o.scale=(w/2,h/2,1)
  for f,zoom,dx,dy in zoomkeys:
   o.scale=(w/2*zoom,h/2*zoom,1);o.location=(dx,dy,-5);o.keyframe_insert(data_path='scale',frame=f);o.keyframe_insert(data_path='location',frame=f)
  visible(o,start,end);return o
 card('before','Portrait_before',1,108,[(1,1,0,0),(70,1.10,-.015,.08),(108,3.8,-.65,1.70)])
 card('after','Portrait_after',935,1050,[(935,2.1,-2.0,2.0),(995,1.05,-.65,0),(1050,1.05,-.65,0)])
 # Header, stage index, subtitle: all remain in the safe region of a vertical reel.
 text('Brand','ANATOMÍA / IMPLANTE',-1.27,2.10,.075,dim,1,1050)
 stages=[(1,108,'LO QUE SE VE','Un diente que falta.'),(109,150,'MIRA MÁS CERCA','El proceso, por dentro.'),(151,270,'01 / ANESTESIA LOCAL','Se anestesia la zona.'),(271,360,'BAJO LA ENCÍA','Un corte para entenderlo.'),(361,480,'02 / PREPARACIÓN','Se prepara el alojamiento.'),(481,630,'03 / IMPLANTE','Titanio dentro del hueso.'),(631,762,'04 / INTEGRACIÓN','Meses de cicatrización.'),(763,900,'05 / PILAR + CORONA','La conexión. El nuevo diente.'),(901,934,'LO QUE NO SE VE','La base de la nueva sonrisa.'),(935,1050,'VUELVE LA SONRISA','Así se recupera un diente.')]
 for i,(a,b,title,subtitle) in enumerate(stages):
  text('Title_%d'%i,title,-1.27,1.88,.108,white,a,b);text('Subtitle_%d'%i,subtitle,-1.27,-1.92,.09,white,a,b)
 text('Disclaimer','Visualización simplificada · cada caso es distinto',-1.27,-2.13,.050,dim,109,934)
 # Thin timeline progress in camera plane.
 progress=line('Progress',[(0,0,0),(2.54,0,0)],.006,cyan);progress.parent=cam;progress.location=(-1.27,-2.27,-4);key(progress,'scale',[(1,(.005,1,1)),(1050,(1,1,1))])
 # Dark studio and broad light sources.
 for name,loc,energy,color,size,target in [('Key',(-4,-7,7),950,(1,.71,.47),6,(0,0,1)),('Teal',(4,2,5),1200,(.14,.77,1),5,(0,0,1)),('Fill',(2,-4,0),350,(.63,.84,1),4,(0,0,1)),('Top',(-1,2,7),800,(1,.46,.2),3,(0,0,1))]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='DI_'+name;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 # Smooth animation, linear rotation for mechanical action.
 for ob in scene.objects:
  if ob.animation_data and ob.animation_data.action:
   for fc in ob.animation_data.action.fcurves:
    for k in fc.keyframe_points:
     if fc.data_path.startswith('hide_'):k.interpolation='CONSTANT'
     elif fc.data_path=='rotation_euler' and ob in [rig,drill]:k.interpolation='LINEAR'
     else:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
 for a,b,title,subtitle in stages:scene.timeline_markers.new(title,frame=a)
 scene['README']='35 s / 30 fps. Upper maxillary educational cutaway. Reference portraits packed. Not a clinical planning model. Select DI_CAMERA; numpad 0; play.'
 scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(out,'frames','DI_')
 scene.frame_set(570)
 # Write dental scene and dependencies only, leaving the existing file and scene untouched.
 dest=os.path.join(out,'IMPLANTE_DENTAL_CINEMA.blend');bpy.data.libraries.write(dest,{scene},fake_user=True,compress=True)
 responder({'ok':True,'scene':scene.name,'objects':len(scene.objects),'blend':dest,'frames':1050})
except Exception:
 responder({'ok':False,'error':traceback.format_exc()})
 raise
finally:
 bpy.context.window.scene=original
 original.camera=original_camera
 if original.frame_current!=original_frame:original.frame_set(original_frame)
