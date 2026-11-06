"""Giovanni Pulido · video v3 (30 oct): Carlos pidió que se parezca a él. En la v2 Qwen inventó la cara (barba de candado en una toma, otra piel en otra).
Ahora Qwen SOLO cambia el fondo de su foto real (misma cara, bigote sin barba, misma pose); mismas voces y tomas que la v2.
Uso: GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/Giovanni/video_v3_20261030/giovanni_v3_modal.py"""
import pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
BASE = ("Edita esta foto SIN cambiar a la persona: conserva EXACTAMENTE la misma cara, los mismos rasgos, el mismo tono de piel, el mismo bigote canoso SIN barba en la barbilla, "
        "el mismo cabello canoso corto, el mismo traje azul marino, la misma corbata, la misma pose con los brazos cruzados y el mismo encuadre. "
        "Quita todo el texto, letras y el fondo rojo. Cambia SOLO el fondo: ")
FIN = " Foto realista vertical 9:16, nítida, luz natural cálida que coincide con el fondo, sin texto, sin letras, sin logotipos."
CUADROS = {
    "GA": (["cara"], BASE + "su despacho de abogado moderno con libreros de madera detrás." + FIN),
    "GB": (["cara"], BASE + "un ventanal con vista a la bahía de Cabo San Lucas, el Arco y el mar azul." + FIN),
    "GC": (["cara"], BASE + "una oficina luminosa con un escritorio de madera, una laptop y carpetas de documentos detrás de él." + FIN),
}
TOMA = ("Vertical realistic talking-head shot: the man speaks directly to the camera in Spanish with natural lip movement exactly matching the speech, small natural head movements, "
        "arms stay crossed, very slow gentle push-in. Keep exactly the same face, mustache without beard, suit and background. No text.")
TOMAS = [("G1", "GA", TOMA, 9.2, None, "G1"), ("G2a", "GB", TOMA, 8.92, None, "G2a"), ("G2b", "GC", TOMA, 7.34, None, "G2b")]


@app.local_entrypoint()
def main(semilla: int = 12):
    refs = {"cara": (RAIZ / "clientes/lote_30oct/refs/giovanni_cara.png").read_bytes()}
    voces = {k: (RAIZ / f"clientes/lote_30oct/voz/{k}.wav").read_bytes() for k in ("G1", "G2a", "G2b")}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    for n, v in escenas.remote("giovanni_v3_20261030", refs, CUADROS, TOMAS, semilla, None, voces, (704, 1280)).items():
        (out / n).write_bytes(v); print("guardado", n)
