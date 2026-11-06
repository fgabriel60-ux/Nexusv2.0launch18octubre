"""Voz clonada (Fish Audio) desde Modal, sin sacar la clave del contenedor.

La clave vive en el secreto de Modal `nexus-env` (variable FISH_API_KEY). Este módulo la usa DENTRO
de la función y solo devuelve el audio, así que la clave nunca pasa por el Codespace.

  GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run modelos_modal/voz_fish_modal.py::decir \
      --texto-archivo guion.txt --salida voz.wav --voz carlos

Voces (reference_id de Fish): carlos, jose, doctora, ruben, ivan.
"""
import pathlib
import modal

imagen = modal.Image.debian_slim(python_version="3.12").pip_install("requests")
app = modal.App("voz-fish", image=imagen)

VOCES = {
    "carlos": "1f679152b5d64c09a8e8eeecd3eb5424",
    "jose": "74cae190c2c84b0caaca073f42f5de54",
    "doctora": "1cbf187942e14e2789215b6374e8323c",
    "ruben": "22eb1ea2a6ce44c882d721aea1003766",
    "ivan": "2e7509fae4af43c0b4166202aeff3918",
}


@app.function(secrets=[modal.Secret.from_name("nexus-env")], timeout=900)
def hablar(texto: str, voz: str = "carlos", modelo: str = "s2-pro") -> bytes:
    import os
    import requests
    clave = os.environ.get("FISH_API_KEY")
    if not clave:
        raise RuntimeError("FISH_API_KEY no está en el secreto nexus-env")
    r = requests.post("https://api.fish.audio/v1/tts",
                      headers={"Authorization": f"Bearer {clave}", "model": modelo,
                               "content-type": "application/json"},
                      json={"text": texto, "format": "wav", "reference_id": VOCES.get(voz, voz)},
                      timeout=600)
    r.raise_for_status()
    return r.content


@app.local_entrypoint()
def tomas(texto_archivo: str = "", salida: str = "tomas", voz: str = "carlos", modelo: str = "s2-pro",
          n: int = 3):
    """Varias tomas por párrafo (la voz clonada a veces se come palabras; después se elige la buena).

      GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run modelos_modal/voz_fish_modal.py::tomas \
          --texto-archivo guion.txt --salida entregables/.../tomas --n 3
    """
    t = pathlib.Path(texto_archivo).read_text(encoding="utf-8")
    partes = [x.strip() for x in t.split("\n\n") if x.strip()]
    d = pathlib.Path(salida); d.mkdir(parents=True, exist_ok=True)
    trabajos = [(p, voz, modelo) for p in partes for _ in range(n)]
    audios = list(hablar.starmap(trabajos))
    k = 0
    for i, p in enumerate(partes):
        (d / f"p{i:02d}.txt").write_text(p, encoding="utf-8")
        for j in range(n):
            (d / f"p{i:02d}_t{j}.wav").write_bytes(audios[k]); k += 1
    print("tomas listas en", d, "·", len(partes), "párrafos x", n)


@app.local_entrypoint()
def decir(texto_archivo: str = "", texto: str = "", salida: str = "voz.wav", voz: str = "carlos",
          modelo: str = "s2-pro"):
    t = pathlib.Path(texto_archivo).read_text(encoding="utf-8") if texto_archivo else texto
    partes = [p.strip() for p in t.split("\n\n") if p.strip()]
    trozos = [hablar.remote(p, voz, modelo) for p in partes]
    out = pathlib.Path(salida)
    if len(trozos) == 1:
        out.write_bytes(trozos[0])
    else:
        d = out.parent / (out.stem + "_partes")
        d.mkdir(parents=True, exist_ok=True)
        for i, b in enumerate(trozos):
            (d / f"p{i:02d}.wav").write_bytes(b)
        print("partes en", d)
        out.write_bytes(trozos[0])
    print("listo", out, sum(len(b) for b in trozos), "bytes")
