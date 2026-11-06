"""Corre un trabajo de escenas descrito en JSON (Qwen-Image-Edit + MiniMax H3, una GPU) y guarda lo que sale en su carpeta de salida.
spec = {"carpeta", "salida", "semilla", "tam": [704, 1280] | null, "refs": {nombre: ruta}, "listos": {nombre: ruta},
        "cuadros": {nombre: [[refs], prompt]}, "tomas": [[nombre, cuadro, prompt, segundos, cuadro_final|null, voz|null]], "voces": {nombre: ruta}}
Uso: SPEC=ruta/spec.json GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/_productor/correr_spec.py"""
import json, os, pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

RAIZ = pathlib.Path("/workspaces/Nexusv2.0launch18octubre")
leer = lambda p: (pathlib.Path(p) if p.startswith("/") else RAIZ / p).read_bytes()


@app.local_entrypoint()
def main(spec: str = ""):
    s = json.load(open(spec or os.environ["SPEC"]))
    out = pathlib.Path(s["salida"]) if s["salida"].startswith("/") else RAIZ / s["salida"]; out.mkdir(parents=True, exist_ok=True)
    res = escenas.remote(s["carpeta"], {k: leer(v) for k, v in s.get("refs", {}).items()}, s.get("cuadros", {}),
                         [tuple(t) for t in s["tomas"]], s.get("semilla", 21), {k: leer(v) for k, v in s.get("listos", {}).items()} or None,
                         {k: leer(v) for k, v in s.get("voces", {}).items()} or None, tuple(s["tam"]) if s.get("tam") else None)
    for n, v in res.items():
        (out / n).write_bytes(v); print("guardado", n, flush=True)
