"""Arma el lote para pedirle a Glimmer la ESTRATEGIA DE IMÁGENES (no video) de cada cliente y prospecto.
Carlos (4 nov 2026, idea de Sabri Suby): para Facebook Ads es más rápido y barato probar imágenes que videos.
Salida: lote_clientes.json y lote_prospectos.json (formato de glimmer_modal.py)."""
import json, pathlib, re, unicodedata

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DIG = RAIZ / "entregables/analisis_clientes_20261030/digest"
IDS = json.loads((RAIZ / "entregables/ronda_8_9_20261031/chat_ids.json").read_text())
DATOS = json.loads((AQUI / "datos.json").read_text())
# 4 nov 2026: chats que no estaban en chat_ids.json y sí tienen conversación guardada
IDS.update({"Jesus_RIMO": "71498354188521", "BDPro": "214649748369481", "Blanca": "99621917425766"})

GIRO = {'Guillermo':'Herrería y techos, Puebla','Fernando':'Anegocios, punto de venta, CDMX',
 'Jose':'Grupo JR, impermeabilización, Puebla','Alberto':'Veneers Dental (Dra. Ángeles), Nogales',
 'Victor':'Servilin, limpieza de obra para empresas','Giovanni':'Abogado de divorcios, Los Cabos',
 'Ivan':'Fumicam, fumigación','Ruben':'Alineación alfabiótica, Metepec','Lisbeth':'Terrenos en Tomatlán, Jalisco',
 'Tatuador':'Estudio de tatuajes, Cancún','Andres':'U Construcción, Cd. Juárez','Jesus_Puertas':'Carpintería, Mazatlán',
 'Israel':'SIRLed, pantallas LED','Mariano':'Casas Vizcaíno Residencial, Rosarito','Blanca':'Hablar Hablando, terapia de lenguaje',
 'Manuel':'Hunab Ku, fotografía de XV','BDPro':'Pistas de baile y audio para eventos, Monterrey',
 'Rachel':'Clou SPA, micropigmentación, Mexicali','Uriel':'Filtro de Liderazgo, consultoría',
 'Veronica':'Torre El Charro, Tampico','BYD_Rafael':'Rafael, asesor de autos BYD',
 'Jesus_RIMO':'RIMO, bolsas sublimadas','Cocinetas':'Cocinetas MTY, Monterrey','Villa_Bahia':'Villa Bahía, hospedaje',
 'Fumigador':'Fumigación','Generadores':'Venta de generadores','Caracol':'Caracol Península','Adrian':'Adrián'}

ALIAS = {'giovanni':'Giovanni','jesus-rimo':'Jesus_RIMO','victor-servilin':'Victor','ruben-quiropraxia':'Ruben',
 'fernando':'Fernando','mariano-vizcaino':'Mariano','guillermo-vicens':'Guillermo','tatuador':'Tatuador',
 'alberto-doctora-angeles':'Alberto','israel-sirled':'Israel','rafael':'BYD_Rafael','lisbeth':'Lisbeth',
 'andres':'Andres','ivan-fumicam':'Ivan','manuel-xv':'Manuel','uriel':'Uriel','jose-grupo-jr':'Jose',
 'cocinetas-mty':'Cocinetas','adrian':'Adrian','villa-bahia':'Villa_Bahia','rachel':'Rachel','bd-pro':'BDPro',
 'fumigador':'Fumigador','generadores':'Generadores','veronica':'Veronica','caracol-peninsula':'Caracol','blanca':'Blanca'}

PLANTILLA = """Eres estratega de anuncios de Meta (Facebook/Instagram) para negocios en México. Da SOLO la respuesta final, en español claro, sin mostrar tu razonamiento.

NEGOCIO: {nombre} · {giro}
OBJETIVO: campaña de MENSAJES a WhatsApp con ANUNCIOS DE IMAGEN (no video). Cada imagen tiene que sacar 9 o 10 en la calificación de calidad de Meta, que mide: oferta, confianza, claridad del mensaje, calidad visual, cumplimiento de políticas, probabilidad de mensajes baratos y probabilidad de mensajes calificados.

DATOS REALES (conversación de WhatsApp; YO = el asesor de la agencia, EL = el cliente. Las notas de voz y las fotos no se ven). Usa SOLO estos datos: no inventes precios, tiempos, distancias, garantías ni resultados. Si falta un dato, escribe [FALTA: ...] y di exactamente qué pedirle.
--- CONVERSACIÓN ---
{conv}
--- FIN DE LA CONVERSACIÓN ---
{extra}
LO QUE SÍ PODEMOS PRODUCIR NOSOTROS (propón solo esto):
- Imágenes nuevas con Qwen-Image-Edit a partir de SUS fotos reales: cambiar encuadre, hora del día, limpiar o cambiar fondo, quitar textos, juntar producto y persona.
- Composición con texto en capa exacta: titular, línea de apoyo, precio REAL si él lo dio, botón de WhatsApp, su logo.
- Antes/después con sus fotos, collage de 3-4 fotos suyas, producto recortado sobre fondo de color.
- Formatos 4:5 y 9:16 para Feed, Reels y Stories.
NO podemos: inventar precios o resultados, usar fotos de banco o de otro negocio, prometer salud, ni usar caras que no sean suyas.

ENTREGA EXACTAMENTE ESTE FORMATO:

1) LAS 5 IMÁGENES, en el orden en que las subiría (la 1 es la primera que se prueba). Para cada una:
- Nombre corto
- Qué se ve: la foto exacta que se usa y de dónde sale (foto suya que ya tenemos / foto que debe mandar / generada con Qwen a partir de cuál)
- Titular en pantalla: texto exacto, máximo 7 palabras
- Línea de apoyo: texto exacto
- Formato (4:5 o 9:16) y dónde va el botón
- Texto primario del anuncio (máximo 3 renglones) y título del botón
- Cómo sube cada rubro: oferta / confianza / claridad / calidad visual / políticas / mensajes baratos / mensajes calificados (una frase por rubro)

2) CALIFICACIÓN ESPERADA de cada una (X/10) y qué le falta a la más baja para llegar a 9.

3) QUÉ NOS TIENE QUE MANDAR ÉL para que la número 1 califique 10 (lista corta y concreta: fotos exactas, precio, zona, prueba).

4) SEGMENTACIÓN Y PRESUPUESTO: ciudad o radio, edad, intereses, y presupuesto diario en pesos como rango (márcalo como estimación).

5) LO QUE NO SE PUEDE DECIR en su giro por políticas de Meta.
"""


def digest(clave):
    cid = IDS.get(clave)
    if not cid:
        return ""
    for f in DIG.glob(f"*__{cid}.txt"):
        t = f.read_text(encoding="utf-8", errors="replace")
        return t[-7000:]
    return ""


def main():
    clientes, prospectos = [], []
    for r in DATOS:
        nombre = r.get("cliente")
        if not nombre:
            continue
        clave = ALIAS.get(r.get("slug", ""), "")
        conv = digest(clave) if clave else ""
        extra = ""
        if not conv:
            conv = "(no hay conversación guardada de este negocio)"
            notas = [v.get("nota", "") for v in r.get("versiones", []) if v.get("nota")]
            if notas:
                extra = "\nLO QUE SABEMOS POR SUS VIDEOS YA CALIFICADOS:\n" + "\n".join(f"- {n}" for n in notas[:3]) + "\n"
        t = {"nombre": re.sub(r"[^A-Za-z0-9_]+", "_", unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()),
             "prompt": PLANTILLA.format(nombre=nombre, giro=GIRO.get(clave, r.get("tipo", "")), conv=conv, extra=extra),
             "fotos": []}
        (clientes if r.get("tipo") == "Cliente" else prospectos).append(t)
    (AQUI / "lote_clientes.json").write_text(json.dumps(clientes, ensure_ascii=False))
    (AQUI / "lote_prospectos.json").write_text(json.dumps(prospectos, ensure_ascii=False))
    print("clientes:", len(clientes), "prospectos:", len(prospectos))
    print("con conversación:", sum(1 for t in clientes + prospectos if "no hay conversación" not in t["prompt"]))


if __name__ == "__main__":
    main()
