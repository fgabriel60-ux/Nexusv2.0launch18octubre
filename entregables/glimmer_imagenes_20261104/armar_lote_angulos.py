"""Segunda ronda (pedido de Carlos, 4 nov 2026 por la tarde): por cada cliente y prospecto,
DOS ÁNGULOS de venta, DOS anuncios de imagen (static ads) y un GUION para que el cliente lo grabe él mismo.
Reusa el armado de datos de armar_lote.py y solo cambia la plantilla."""
import importlib.util, json, pathlib, re, unicodedata

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("base", AQUI / "armar_lote.py")
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)

PLANTILLA = """Eres estratega de anuncios de Meta (Facebook/Instagram) para negocios en México. Da SOLO la respuesta final, en español claro para el dueño del negocio, sin mostrar tu razonamiento.

NEGOCIO: {nombre} · {giro}
OBJETIVO: que le lleguen mensajes BARATOS de gente que SÍ compra, por WhatsApp. Queremos anuncios que la IA de calidad de Meta califique 9 o 10 en: oferta, confianza, claridad, calidad visual, políticas, probabilidad de mensajes baratos y probabilidad de mensajes calificados.

DATOS REALES (conversación de WhatsApp; YO = el asesor de la agencia, EL = el cliente. Las notas de voz y las fotos no se ven). Usa SOLO estos datos: no inventes precios, tiempos, distancias, garantías ni resultados. Si falta un dato, escribe [FALTA: ...] y di qué pedirle.
--- CONVERSACIÓN ---
{conv}
--- FIN DE LA CONVERSACIÓN ---
{extra}
LO QUE PODEMOS PRODUCIR NOSOTROS: imágenes nuevas con Qwen-Image-Edit a partir de SUS fotos reales (encuadre, hora del día, fondo limpio, quitar textos), composición con texto en capa exacta (titular, precio REAL si él lo dio, botón de WhatsApp, su logo), antes/después con sus fotos, collage de 3-4 fotos suyas, producto recortado sobre color. Formatos 4:5 y 9:16.
NO podemos: inventar precios ni resultados, usar fotos de banco, prometer salud, ni caras que no sean suyas.

ENTREGA EXACTAMENTE ESTE FORMATO:

1) DOS ÁNGULOS DE VENTA (distintos entre sí, no la misma idea con otras palabras). Por cada uno:
- Nombre del ángulo
- A quién le habla (quién es esa persona y qué le duele)
- La promesa concreta, con el dato real que la sostiene
- Por qué baja el costo por mensaje en su giro
- Qué prueba real lo respalda (y si no la tenemos: [FALTA: ...])

2) DOS ANUNCIOS DE IMAGEN (uno por ángulo). Por cada uno:
- Qué se ve: la foto exacta y de dónde sale (foto suya que ya tenemos / la que debe mandar / generada con Qwen a partir de cuál)
- Titular en pantalla: texto exacto, máximo 7 palabras
- Línea de apoyo: texto exacto
- Formato (4:5 o 9:16) y dónde va el botón
- Texto primario del anuncio (máximo 3 renglones) y título del botón
- Calificación esperada (X/10) y qué le falta para llegar a 10

3) GUION PARA QUE ÉL LO GRABE CON SU CELULAR (20-30 segundos, el ángulo más fuerte). Dámelo así:
- Frase por frase, palabra por palabra, como lo tiene que decir (lenguaje de él, no publicitario)
- Al lado de cada frase: qué debe estar grabando en ese momento (dónde parado, qué enseña, qué se ve atrás)
- Cómo grabarlo: vertical, dónde poner el celular, luz, cuánto dura cada toma
- Qué NO debe decir (por políticas de Meta o porque espanta al comprador)

4) QUÉ NOS TIENE QUE MANDAR ÉL para que esto califique 10 (lista corta y concreta).

5) SEGMENTACIÓN Y PRESUPUESTO: ciudad o radio, edad, intereses y presupuesto diario en pesos como rango (márcalo como estimación).
"""


def main():
    datos = json.loads((AQUI / "datos.json").read_text())
    clientes, prospectos = [], []
    for r in datos:
        nombre = r.get("cliente")
        if not nombre:
            continue
        clave = base.ALIAS.get(r.get("slug", ""), "")
        conv = base.digest(clave) if clave else ""
        extra = ""
        if not conv:
            conv = "(no hay conversación guardada de este negocio)"
            notas = [v.get("nota", "") for v in r.get("versiones", []) if v.get("nota")]
            if notas:
                extra = "\nLO QUE SABEMOS POR SUS VIDEOS YA CALIFICADOS:\n" + "\n".join(f"- {n}" for n in notas[:3]) + "\n"
        t = {"nombre": re.sub(r"[^A-Za-z0-9_]+", "_", unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()),
             "prompt": PLANTILLA.format(nombre=nombre, giro=base.GIRO.get(clave, r.get("tipo", "")), conv=conv, extra=extra),
             "fotos": []}
        (clientes if r.get("tipo") == "Cliente" else prospectos).append(t)
    (AQUI / "lote2_clientes.json").write_text(json.dumps(clientes, ensure_ascii=False))
    (AQUI / "lote2_prospectos.json").write_text(json.dumps(prospectos, ensure_ascii=False))
    print("clientes:", len(clientes), "prospectos:", len(prospectos))


if __name__ == "__main__":
    main()
