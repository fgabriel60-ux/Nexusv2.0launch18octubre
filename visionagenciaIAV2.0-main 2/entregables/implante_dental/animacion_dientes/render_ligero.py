import bpy,os,json,time
from pathlib import Path
base=Path('/workspaces/visionagenciaIAV2.0/entregables/implante_dental')
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.cycles.max_bounces=4;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.12
s.render.resolution_percentage=25;s.render.image_settings.file_format='PNG';s.render.use_sequencer=False
# Blender 4 converts legacy SSS to weight 1 with scaled radius; reduce preview variance.
for name,weight in [('AP_Enamel',.035),('AP_Gingiva',.08),('AP_Root',.03),('AP_Piel_fotografica_con_poroso',.06)]:
 m=bpy.data.materials.get(name)
 if m and m.use_nodes:
  for node in m.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED' and 'Subsurface Weight' in node.inputs: node.inputs['Subsurface Weight'].default_value=weight
frames=[int(f) for f in os.environ.get('DENTAL_FRAMES','360,620').split(',')]
assert len(frames)<=5
for f in frames:
 s.frame_set(f);s.render.filepath=str(base/'capturas_animacion'/('FASE_%04d.png'%f));t=time.time();bpy.ops.render.render(write_still=True);print('FRAME_DONE',f,round(time.time()-t,2),flush=True)
