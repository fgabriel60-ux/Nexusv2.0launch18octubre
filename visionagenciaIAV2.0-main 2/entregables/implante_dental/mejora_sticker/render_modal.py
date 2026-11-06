"""Private Modal GPU render; reuses the previously connected Blender image."""
import modal, importlib.util, json, subprocess, time
from pathlib import Path
BASE=Path(__file__).resolve().parent
BL_VER='4.2.3'
imagen = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("wget", "xz-utils", "libegl1", "libgl1", "libxi6", "libxkbcommon0", "libxrender1",
                 "libsm6", "libxfixes3", "libxxf86vm1", "xvfb", "xauth")
    .run_commands(
        f"wget -q https://download.blender.org/release/Blender4.2/blender-{BL_VER}-linux-x64.tar.xz -O /tmp/b.tar.xz",
        "tar -xf /tmp/b.tar.xz -C /opt && rm /tmp/b.tar.xz",
        f"ln -s /opt/blender-{BL_VER}-linux-x64/blender /usr/local/bin/blender")
    # pide al runtime de NVIDIA tambien las librerias de graficos (EGL), no solo las de computo
    .env({"NVIDIA_DRIVER_CAPABILITIES": "all"})
)
app=modal.App('dental-sticker-render',image=imagen)
volume=modal.Volume.from_name('dental-sticker-privado',create_if_missing=True)
CODE=r'''
import bpy,json,sys,time,os
frames,folder,percent,samples=json.loads(sys.argv[sys.argv.index('--')+1])
s=bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.render.use_sequencer=False;s.render.use_compositing=False
s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=percent
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.use_simplify=False;s.render.film_transparent=False
s.cycles.samples=samples;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.035
s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=4
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.refresh_devices()
assert any(d.type=='OPTIX' for d in prefs.devices),'No OPTIX GPU: abort instead of CPU fallback'
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU'
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
print('DENTAL_INFO '+json.dumps({'devices':[(d.name,d.type,d.use) for d in prefs.devices],'times':times,'samples':samples,'percent':percent}))
'''
@app.function(gpu='T4',volumes={'/data':volume},timeout=3600,memory=8192,cpu=2,max_containers=6)
def render(frames:list,folder:str,percent:int,samples:int):
 Path('/tmp/render_dental.py').write_text(CODE)
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
 p=subprocess.run(['blender','-b','/data/DENTAL_STICKER.blend','-t','2','--python-exit-code','1','-P','/tmp/render_dental.py','--',json.dumps([frames,'/data/'+folder,percent,samples])],capture_output=True,text=True)
 volume.commit()
 info=next((json.loads(l[len('DENTAL_INFO '):]) for l in p.stdout.splitlines() if l.startswith('DENTAL_INFO ')),None)
 if p.returncode or not info:raise RuntimeError((p.stdout+p.stderr)[-6000:])
 return {'gpu':gpu,**info}
@app.local_entrypoint()
def main(mode:str='preview',folder:str='preview_v1'):
 if mode=='upload':
  with volume.batch_upload(force=True) as batch:batch.put_file(BASE/'DENTAL_STICKER.blend','/DENTAL_STICKER.blend')
  return
 if mode=='preview':
  jobs=[[1],[265],[374],[740],[1050]];percent=50;samples=64
 elif mode=='final':
  jobs=[list(range(i,min(i+35,1051))) for i in range(1,1051,35)];percent=100;samples=64
 elif mode=='hero':
  jobs=[[740],[380],[265]];percent=100;samples=192
 else:raise ValueError(mode)
 reports=[]
 for result in render.map(jobs,kwargs={'folder':folder,'percent':percent,'samples':samples}):
  reports.append(result);print(json.dumps(result),flush=True)
  (BASE/(folder+'_gpu.json')).write_text(json.dumps(reports,indent=2))
 dest=BASE/folder;dest.mkdir(exist_ok=True)
 for entry in volume.iterdir('/'+folder):
  if not entry.path.endswith('.png'):continue
  out=dest/Path(entry.path).name
  if out.exists():continue
  with out.open('wb') as f:
   for data in volume.read_file(entry.path):f.write(data)
 print('Downloaded',dest)
