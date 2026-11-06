"""Giovanni Pulido · video v2 (30 oct): 3 tomas realistas con su voz clonada y sincronía de labios (guion de Glimmer: sin promesas de plazo, precio desde $20,000 con alcance).
Voces: clientes/lote_30oct/voz (G1, G2a, G2b). Uso: python3 gasto_modal.py run clientes/Giovanni/video_v2_20261030/giovanni_modal.py"""
import pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
BASE = ("Foto realista vertical 9:16, nítida, luz natural cálida, sin texto, sin letras, sin logotipos. El MISMO hombre de la imagen (misma cara, bigote, cabello canoso corto, "
        "traje azul marino y corbata azul con puntitos). ")
CUADROS = {
    "GA": (["cara"], BASE + "Sentado en su despacho de abogado moderno con libreros de madera y luz cálida, mirando a cámara con expresión segura y amable, plano medio de pecho hacia arriba."),
    "GB": (["cara"], BASE + "De pie junto a un ventanal con vista a la bahía de Cabo San Lucas y el mar azul, mirando a cámara con expresión segura y amable, plano medio de pecho hacia arriba."),
    "GC": (["cara"], BASE + "Sentado ante un escritorio con una laptop abierta y una carpeta de documentos, sonriendo ligeramente a cámara, plano medio de pecho hacia arriba."),
}
TOMA = ("Vertical realistic talking-head shot: the man speaks directly to the camera in Spanish with natural lip movement exactly matching the speech, small natural head movements, "
        "calm hand gestures, very slow gentle push-in. Keep the same face, suit and background exactly. No text.")
TOMAS = [("G1", "GA", TOMA, 9.2, None, "G1"), ("G2a", "GB", TOMA, 8.92, None, "G2a"), ("G2b", "GC", TOMA, 7.34, None, "G2b")]


@app.local_entrypoint()
def main(semilla: int = 12):
    refs = {"cara": (RAIZ / "clientes/lote_30oct/refs/giovanni_cara.png").read_bytes()}
    voces = {k: (RAIZ / f"clientes/lote_30oct/voz/{k}.wav").read_bytes() for k in ("G1", "G2a", "G2b")}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    for n, v in escenas.remote("giovanni_v2_20261030", refs, CUADROS, TOMAS, semilla, None, voces, (704, 1280)).items():
        (out / n).write_bytes(v); print("guardado", n)
