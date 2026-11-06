"""Obrero de Nexus en Modal: revisa cada 10 min la cola /obrero/cola/*.json del volumen nexus-workspace y ejecuta los trabajos de escenas
(Qwen-Image-Edit + MiniMax H3, app desplegada `productor-escenas`) aunque Claude esté desconectado. Si un trabajo falla, le pregunta a
Qwen3-VL-30B (app `qwen-productor`) qué hacer: reintentar o abandonar. Resultados en /obrero/salida/<id>/ y estado en /obrero/estado.json.

  modal deploy obrero_qwen_modal.py               # una vez (perfil charlyfavela2)
  modal run obrero_qwen_modal.py::encolar --archivo trabajo.json
  modal run obrero_qwen_modal.py::estado
Trabajo = {"id", "carpeta", "semilla", "tam": [704, 1280], "refs": {nombre: ruta_en_volumen}, "cuadros": {nombre: [[refs], prompt]},
           "tomas": [[nombre, cuadro, prompt, segundos, (cuadro_final), (voz)]], "voces": {nombre: ruta_en_volumen}, "listos": {nombre: ruta}}"""
import json
import time
import modal

RAIZ = "/vol/workspaces/Nexusv2.0launch18octubre"
OB = "/vol/obrero"
imagen = modal.Image.debian_slim(python_version="3.12").pip_install("modal")
imagen_armado = (modal.Image.debian_slim(python_version="3.12").apt_install("ffmpeg", "fonts-dejavu-core")
                 .pip_install("av", "imageio-ffmpeg", "pillow", "numpy", "requests"))
app = modal.App("obrero-nexus", image=imagen)
vol = modal.Volume.from_name("nexus-workspace")
MAX_INTENTOS = 3


def _ruta(p):
    return p if p.startswith("/") else f"{RAIZ}/{p}"


def _estado(mut=None):
    import os
    f = f"{OB}/estado.json"
    e = json.load(open(f)) if os.path.exists(f) else {}
    if mut:
        mut(e)
        os.makedirs(OB, exist_ok=True)
        json.dump(e, open(f, "w"), ensure_ascii=False, indent=1)
        vol.commit()
    return e


def _qwen_decide(trabajo_id, error):
    """Qwen3-VL lee el error y contesta {"accion": "reintentar"|"abandonar", "motivo": "..."}."""
    try:
        Productor = modal.Cls.from_name("qwen-productor", "Productor")
        prompt = ("Eres el supervisor de un obrero que genera escenas de video con IA en una GPU de Modal. El trabajo "
                  f"'{trabajo_id}' falló con este error:\n{error[-1800:]}\n\nResponde SOLO un JSON {{\"accion\": \"reintentar\" o \"abandonar\", "
                  "\"motivo\": \"una frase\"}}. Reintentar si parece temporal (tiempo agotado, 429/504, GPU no disponible, red). "
                  "Abandonar si es un error de datos o de código que se repetirá igual (archivo faltante, clave inválida, prompt rechazado).")
        txt = Productor().planear.remote([{"prompt": prompt, "imagenes": []}])[0]
        d = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
        return d.get("accion", "reintentar"), d.get("motivo", "")
    except Exception as e:  # sin Qwen, decisión por defecto
        return "reintentar", f"Qwen no respondió ({str(e)[:80]})"


@app.function(image=imagen_armado, volumes={"/vol": vol}, cpu=4, memory=8192, timeout=3600)
def armar(cmd: list, cwd: str, esperar: list):
    """Corre un armado (ffmpeg/PIL) sobre el workspace del volumen; `esperar` = archivos de salida que deben existir."""
    import os
    import subprocess
    vol.reload()
    os.makedirs("/workspaces", exist_ok=True)
    if not os.path.exists(RAIZ.replace("/vol", "")):
        os.symlink(RAIZ, RAIZ.replace("/vol", ""))
    r = subprocess.run(cmd, cwd=_ruta(cwd), capture_output=True, text=True)
    falta = [f for f in esperar if not os.path.exists(_ruta(f))]
    if r.returncode or falta:
        raise RuntimeError(f"armado falló ({r.returncode}) faltan {falta}\n{(r.stdout + r.stderr)[-1500:]}")
    vol.commit()
    return (r.stdout + r.stderr)[-500:]


@app.function(volumes={"/vol": vol}, schedule=modal.Period(minutes=10), timeout=3 * 3600, max_containers=1)
def revisar():
    import glob
    import os
    vol.reload()
    for f in sorted(glob.glob(f"{OB}/cola/*.json")):
        t = json.load(open(f))
        tid = t["id"]
        e = _estado()
        if e.get(tid, {}).get("estado") in ("listo", "abandonado"):
            continue
        n = e.get(tid, {}).get("intentos", 0)
        if n >= MAX_INTENTOS:
            _estado(lambda s: s[tid].update(estado="abandonado"))
            continue
        _estado(lambda s: s.setdefault(tid, {}).update(estado="corriendo", intentos=n + 1, inicio=time.strftime("%F %T")))
        try:
            if t.get("tipo") == "cmd":
                if t.get("despues_de") and _estado().get(t["despues_de"], {}).get("estado") != "listo":
                    _estado(lambda s: s[tid].update(estado="pendiente", intentos=n))
                    continue
                for copia in t.get("copiar", []):   # [origen_en_salida, destino] clips del obrero hacia la carpeta del armado
                    import shutil
                    os.makedirs(os.path.dirname(_ruta(copia[1])), exist_ok=True)
                    shutil.copy(_ruta(copia[0]), _ruta(copia[1]))
                out = armar.remote(t["cmd"], t["cwd"], t.get("esperar", []))
                _estado(lambda s: s[tid].update(estado="listo", fin=time.strftime("%F %T"), archivos=t.get("esperar", []), log=out))
                continue
            rd = lambda p: open(_ruta(p), "rb").read()
            refs = {k: rd(v) for k, v in t.get("refs", {}).items()}
            voces = {k: rd(v) for k, v in t.get("voces", {}).items()}
            listos = {k: rd(v) for k, v in t.get("listos", {}).items()}
            cuadros = {k: (v[0], v[1]) for k, v in t.get("cuadros", {}).items()}
            tomas = [tuple(x) for x in t.get("tomas", [])]
            escenas = modal.Function.from_name("productor-escenas", "escenas")
            res = escenas.remote(t["carpeta"], refs, cuadros, tomas, t.get("semilla", 12), listos, voces, tuple(t["tam"]) if t.get("tam") else None)
            sal = f"{OB}/salida/{tid}"
            os.makedirs(sal, exist_ok=True)
            for nombre, b in res.items():
                open(f"{sal}/{nombre}", "wb").write(b)
            _estado(lambda s: s[tid].update(estado="listo", fin=time.strftime("%F %T"), archivos=sorted(res)))
        except Exception as ex:
            accion, motivo = _qwen_decide(tid, repr(ex))
            nuevo = "abandonado" if accion == "abandonar" else "pendiente"
            _estado(lambda s: s[tid].update(estado=nuevo, error=repr(ex)[:500], qwen=f"{accion}: {motivo}"))


@app.local_entrypoint()
def encolar(archivo: str):
    t = json.load(open(archivo))
    with vol.batch_upload(force=True) as b:
        b.put_file(archivo, f"/obrero/cola/{t['id']}.json")
    print("encolado", t["id"])


@app.local_entrypoint()
def estado():
    import subprocess
    print(subprocess.run(["modal", "volume", "get", "nexus-workspace", "/obrero/estado.json", "-"], capture_output=True, text=True).stdout)
