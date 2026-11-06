"""Pasa cada anuncio de imagen por el portal de Glimmer rápido y guarda POR QUÉ FUNCIONA y su calificación.
  python3 entregables/anuncios_imagen_20261104/calificar_portal.py
Resultado: entregables/anuncios_imagen_20261104/calificaciones/<ANUNCIO>.md y RESUMEN.md"""
import base64, json, pathlib, time, urllib.request

AQUI = pathlib.Path(__file__).resolve().parent
URL = "https://charlyfavela666--glimmer-rapido-web.us-east.modal.run/calificar?k=i7_8usCbRdED_8lp"
SAL = AQUI / "calificaciones"; SAL.mkdir(exist_ok=True)

CONTEXTO = {
 "MARIANO": ("Mariano Herrera, asesor inmobiliario de Vizcaíno Residencial en Rosarito, Baja California. "
   "Vende las casas Bugambilia (desde 2.4 MDP), Benjamina (desde 2.8 MDP) y Salvia (desde 3.1 MDP, 4 recámaras), "
   "con acceso controlado, plaza comercial, pádel y área de juegos. Anuncio de imagen 4:5 para mensajes por WhatsApp."),
 "RAFAEL": ("Rafael, asesor de venta de autos BYD en México. Anuncio de imagen 4:5 para que le escriban por WhatsApp "
   "y agenden prueba de manejo. La foto es real de él y del BYD de la agencia."),
 "MANUEL": ("Manuel, fotografía y video de XV años (Hunab Ku). Las fotos son de un XV real que él cubrió. "
   "Anuncio de imagen 4:5 para que le escriban por WhatsApp y aparten fecha. WhatsApp 631 126 5175."),
}


def pide(ruta, contexto):
    b = base64.b64encode(ruta.read_bytes()).decode()
    cuerpo = {"fotos": ["data:image/jpeg;base64," + b], "contexto": contexto, "tokens": 900}
    req = urllib.request.Request(URL, data=json.dumps(cuerpo).encode(),
                                 headers={"content-type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=900).read())
    if not r.get("ok"):
        raise RuntimeError(r.get("error", "error"))
    return r["texto"]


def main():
    fs = sorted((AQUI / "anuncios").glob("*.jpg"))
    resumen = ["# Por qué funciona cada imagen · calificación de Glimmer (4 nov 2026)", ""]
    for f in fs:
        destino = SAL / (f.stem + ".md")
        if destino.exists():
            print("ya estaba", f.stem); continue
        cli = f.stem.split("_")[0]
        t0 = time.time()
        try:
            texto = pide(f, CONTEXTO.get(cli, ""))
        except Exception as e:
            print("falló", f.stem, e); continue
        destino.write_text(f"# {f.stem}\n\n{texto}\n")
        nota = next((l for l in texto.splitlines() if l.startswith("CALIFICACION")), "?")
        print(f"{f.stem}: {nota} ({time.time()-t0:.0f} s)", flush=True)
        resumen.append(f"- **{f.stem}** · {nota}")
    (AQUI / "RESUMEN_CALIFICACIONES.md").write_text("\n".join(resumen) + "\n")


if __name__ == "__main__":
    main()
