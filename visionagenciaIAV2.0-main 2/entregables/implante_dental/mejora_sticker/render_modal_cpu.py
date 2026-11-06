"""Render en Modal SIN GPU (Carlos 15 sep: «intenta sin gpu en modal»): Modal pide tarjeta para T4, no para CPU.
Eevee no corre sin GPU, así que es Cycles CPU con OpenImageDenoise. render_modal.py (Cycles GPU, de Astra) no se toca.
Uso:
  python3 -m modal run render_modal_cpu.py --mode upload
  python3 -m modal run render_modal_cpu.py --mode preview --folder cpu_preview     (mide el tiempo por cuadro)
  python3 -m modal run render_modal_cpu.py --mode final --folder cpu_final
  python3 montar_video.py cpu_final"""
import modal, json, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
BL_VER = '4.2.3'
imagen = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("wget", "xz-utils", "libegl1", "libgl1", "libxi6", "libxkbcommon0", "libxrender1",
                 "libsm6", "libxfixes3", "libxxf86vm1")
    .run_commands(
        f"wget -q https://download.blender.org/release/Blender4.2/blender-{BL_VER}-linux-x64.tar.xz -O /tmp/b.tar.xz",
        "tar -xf /tmp/b.tar.xz -C /opt && rm /tmp/b.tar.xz",
        f"ln -s /opt/blender-{BL_VER}-linux-x64/blender /usr/local/bin/blender")
)
app = modal.App('dental-cpu-render', image=imagen)
volume = modal.Volume.from_name('dental-cpu-privado', create_if_missing=True)
CPUS = 8

CODE = r'''
import bpy, json, sys, time, os
frames, folder, percent, samples = json.loads(sys.argv[sys.argv.index('--') + 1])
s = bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']; bpy.context.window.scene = s
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'
s.render.use_sequencer = False; s.render.use_compositing = False
s.render.resolution_x = 1080; s.render.resolution_y = 1920; s.render.resolution_percentage = percent
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGB'
s.render.use_simplify = False; s.render.film_transparent = False
s.cycles.samples = samples; s.cycles.use_denoising = True; s.cycles.denoiser = 'OPENIMAGEDENOISE'
s.cycles.use_adaptive_sampling = True; s.cycles.adaptive_threshold = .05
s.cycles.max_bounces = 4; s.cycles.diffuse_bounces = 2; s.cycles.glossy_bounces = 2; s.cycles.transmission_bounces = 4
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED' and 'Subsurface Weight' in n.inputs and n.inputs['Subsurface Weight'].default_value > .5:
            n.inputs['Subsurface Weight'].default_value = .035
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = 0
os.makedirs(folder, exist_ok=True); times = []
for f in frames:
    path = folder + '/frame_%04d.png' % f
    if os.path.exists(path): continue
    s.frame_set(f); s.render.filepath = path; t = time.monotonic()
    bpy.ops.render.render(write_still=True); times.append([f, round(time.monotonic() - t, 1)])
print('DENTAL_INFO ' + json.dumps({'times': times, 'samples': samples, 'percent': percent}))
'''


@app.function(volumes={'/data': volume}, timeout=6 * 3600, memory=8192, cpu=CPUS, max_containers=20)
def render(frames: list, folder: str, percent: int, samples: int):
    Path('/tmp/render_cpu.py').write_text(CODE)
    p = subprocess.run(['blender', '-b', '/data/DENTAL_STICKER.blend', '-t', str(CPUS), '--python-exit-code', '1',
                        '-P', '/tmp/render_cpu.py', '--', json.dumps([frames, '/data/' + folder, percent, samples])],
                       capture_output=True, text=True)
    volume.commit()
    info = next((json.loads(l[len('DENTAL_INFO '):]) for l in p.stdout.splitlines() if l.startswith('DENTAL_INFO ')), None)
    if p.returncode or not info:
        raise RuntimeError((p.stdout + p.stderr)[-6000:])
    return info


@app.local_entrypoint()
def main(mode: str = 'preview', folder: str = 'cpu_preview'):
    if mode == 'upload':
        with volume.batch_upload(force=True) as batch:
            batch.put_file(BASE / 'DENTAL_STICKER.blend', '/DENTAL_STICKER.blend')
        return
    if mode == 'preview':
        jobs = [[1], [265], [374], [740], [950], [1050]]; percent = 50; samples = 32
    elif mode == 'final':
        jobs = [list(range(i, min(i + 30, 1051))) for i in range(1, 1051, 30)]; percent = 100; samples = 32
    else:
        raise ValueError(mode)
    reports = []
    for result in render.map(jobs, kwargs={'folder': folder, 'percent': percent, 'samples': samples}, return_exceptions=True):
        reports.append(result if isinstance(result, dict) else {'error': str(result)[-400:]})
        print(json.dumps(reports[-1]), flush=True)
        (BASE / (folder + '_cpu.json')).write_text(json.dumps(reports, indent=2))
    dest = BASE / folder; dest.mkdir(exist_ok=True)
    for entry in volume.iterdir('/' + folder):
        if not entry.path.endswith('.png'): continue
        out = dest / Path(entry.path).name
        if out.exists(): continue
        with out.open('wb') as f:
            for data in volume.read_file(entry.path): f.write(data)
    print('Downloaded', dest)
