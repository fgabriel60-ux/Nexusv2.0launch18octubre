"""Render del close-up del anilox de Marco en Modal (GPU T4, EEVEE Next de Blender 4.2), porque el Blender de la
Mac no estaba conectado. Carlos (19 sep): «dame render del anilox». Receta de
implante_dental/mejora_sticker/render_modal_eevee.py.
Uso:
  python3 -m modal run render_modal_anilox.py --mode upload
  python3 -m modal run render_modal_anilox.py --mode final --folder anilox_final
  (luego armar_video.sh)"""
import modal, json, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
BL_VER = '4.2.3'
imagen = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("wget", "xz-utils", "libegl1", "libgl1", "libxi6", "libxkbcommon0", "libxrender1",
                 "libsm6", "libxfixes3", "libxxf86vm1", "xvfb", "xauth")
    .run_commands(
        f"wget -q https://download.blender.org/release/Blender4.2/blender-{BL_VER}-linux-x64.tar.xz -O /tmp/b.tar.xz",
        "tar -xf /tmp/b.tar.xz -C /opt && rm /tmp/b.tar.xz",
        f"ln -s /opt/blender-{BL_VER}-linux-x64/blender /usr/local/bin/blender")
    .env({"NVIDIA_DRIVER_CAPABILITIES": "all"})
)
app = modal.App('anilox-marco-render', image=imagen)
volume = modal.Volume.from_name('anilox-marco-privado', create_if_missing=True)

CODE = r'''
import bpy, json, sys, time, os
frames, folder, percent, samples = json.loads(sys.argv[sys.argv.index('--') + 1])
s = bpy.data.scenes['ANILOX_MARCO_CLOSEUP']
s.render.engine = 'BLENDER_EEVEE_NEXT'
s.render.resolution_x = 1080; s.render.resolution_y = 1920; s.render.resolution_percentage = percent
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGB'
e = s.eevee
e.taa_render_samples = samples
for attr, val in (('use_shadows', True), ('use_raytracing', True), ('use_gtao', True)):
    if hasattr(e, attr):
        setattr(e, attr, val)
os.makedirs(folder, exist_ok=True); times = []
with bpy.context.temp_override(scene=s, view_layer=s.view_layers[0]):
    for f in frames:
        path = folder + '/frame_%04d.png' % f
        if os.path.exists(path): continue
        s.frame_set(f); s.render.filepath = path; t = time.monotonic()
        bpy.ops.render.render(write_still=True); times.append([f, round(time.monotonic() - t, 2)])
print('ANX_INFO ' + json.dumps({'n': len(times), 'seg_por_cuadro': round(sum(x[1] for x in times) / max(1, len(times)), 2)}))
'''


@app.function(gpu='T4', volumes={'/data': volume}, timeout=3600, memory=8192, cpu=2, max_containers=8)
def render(frames: list, folder: str, percent: int, samples: int):
    Path('/tmp/render_anx.py').write_text(CODE)
    p = subprocess.run(['blender', '-b', '/data/ANILOX_MARCO.blend', '--python-exit-code', '1', '-P', '/tmp/render_anx.py',
                        '--', json.dumps([frames, '/data/' + folder, percent, samples])], capture_output=True, text=True)
    volume.commit()
    info = next((json.loads(l[len('ANX_INFO '):]) for l in p.stdout.splitlines() if l.startswith('ANX_INFO ')), None)
    if p.returncode or not info:
        raise RuntimeError((p.stdout + p.stderr)[-6000:])
    return {'frames': [frames[0], frames[-1]], **info}


@app.local_entrypoint()
def main(mode: str = 'final', folder: str = 'anilox_final'):
    if mode == 'upload':
        with volume.batch_upload(force=True) as batch:
            batch.put_file(BASE / 'ANILOX_MARCO.blend', '/ANILOX_MARCO.blend')
        return
    if mode == 'preview':
        jobs = [[168, 330, 355, 394], [470, 590, 700]]; percent = 50; samples = 32
    else:
        jobs = [list(range(i, min(i + 72, 721))) for i in range(144, 721, 72)]; percent = 100; samples = 64
    for result in render.map(jobs, kwargs={'folder': folder, 'percent': percent, 'samples': samples}):
        print(json.dumps(result), flush=True)
    dest = BASE / folder; dest.mkdir(exist_ok=True)
    for entry in volume.iterdir('/' + folder):
        if not entry.path.endswith('.png'): continue
        out = dest / Path(entry.path).name
        if out.exists(): continue
        with out.open('wb') as f:
            for data in volume.read_file(entry.path): f.write(data)
    print('Bajados a', dest)
