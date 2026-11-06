
import bpy,json,sys,time,os
frames,folder,percent,samples=json.loads(sys.argv[sys.argv.index('--')+1])
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.render.use_sequencer=False;s.render.use_compositing=False
s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=percent
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.use_simplify=False;s.render.film_transparent=False
s.cycles.samples=samples;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.035
s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=4
s.cycles.device='CPU'
# Legacy SSS conversion is corrected explicitly in this render copy.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED' and 'Subsurface Weight' in n.inputs and n.inputs['Subsurface Weight'].default_value>.5:
   n.inputs['Subsurface Weight'].default_value=.035
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
os.makedirs(folder,exist_ok=True);times=[]
for f in frames:
 path=folder+'/frame_%04d.png'%f
 if os.path.exists(path):continue
 s.frame_set(f);s.render.filepath=path;t=time.monotonic();bpy.ops.render.render(write_still=True);times.append([f,time.monotonic()-t])
print('DENTAL_INFO '+json.dumps({'devices':['CPU local'],'times':times,'samples':samples,'percent':percent}))
