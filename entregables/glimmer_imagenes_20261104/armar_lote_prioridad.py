"""Lote en el ORDEN que pidió Carlos (4 nov 2026, noche): dos ángulos, dos static ads y guion para que el cliente grabe.
El tatuador va primero y con tarea especial: analizar el video que mandó SIN subtítulos (17 s, 720x1280),
proponer subtítulos exactos y cómo llevarlo a 8 con lo que ya tenemos.
Salida: lote_prioridad.json"""
import json, pathlib, sys, time

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
DIG = RAIZ / "entregables/analisis_clientes_20261030/digest"
sys.path.insert(0, str(RAIZ / "herramientas"))

# (nombre, giro, chat id)  — en el orden exacto que pidió Carlos
ORDEN = [
    ("Adrián · tatuador (Cancún)", "Estudio de tatuajes en el Centro de Cancún", "250053667119335"),
    ("Mariano · Vizcaíno", "Casas en Vizcaíno Residencial / Catania, Rosarito", "27337584279694"),
    ("Rafael · autos BYD", "Asesor de venta de autos BYD", "225412869304444"),
    ("Giovanni Pulido", "Abogado de divorcios, Los Cabos", "147832891793521"),
    ("Fernando · Anegocios", "Puntos de venta y sistemas para negocios, CDMX", "263766994321528"),
    ("Rubén · Quiropraxia", "Alineación alfabiótica, Zinacantepec y Metepec", "25112875143230"),
    ("Ginecólogo (prospecto)", "Consultorio de ginecología", "52549679845607"),
    ("Oficinas amuebladas León (prospecto)", "Renta de oficinas amuebladas en León", "133921375272987"),
    ("Lisbeth · terrenos", "Terrenos en Tomatlán, Jalisco", "161641681395864"),
    ("Víctor · Servilin", "Limpieza de obra fina para constructoras y empresas", "244250780389552"),
    ("Rashel Carrasco (prospecto)", "Micropigmentación / Clou SPA, Mexicali", "233916904525900"),
    ("Jesús Puertas (prospecto)", "Carpintería: puertas y closets, Mazatlán", "77185511633028"),
    ("Ignacio Iglesia", "Venta de Chevrolet Colorado 2019", "71494512189562"),
    ("Jesús · cápsulas Rar~Amore", "Suplementos en cápsulas", "31606932787332"),
    ("Manuel · fotografía XV", "Hunab Ku, fotografía de XV años", "177558293323885"),
]

PLANTILLA = """Eres estratega de anuncios de Meta (Facebook/Instagram) para negocios en México. Da SOLO la respuesta final, en español claro para el dueño del negocio, sin mostrar tu razonamiento.

NEGOCIO: {nombre} · {giro}
OBJETIVO: mensajes baratos por WhatsApp de gente que SÍ compra. Los anuncios tienen que calificar 9 o 10 en la revisión de calidad de Meta (oferta, confianza, claridad, calidad visual, políticas, mensajes baratos, mensajes calificados).

DATOS REALES (conversación de WhatsApp; YO = el asesor de la agencia, EL = el cliente. Las notas de voz y las fotos no se ven). Usa SOLO estos datos: no inventes precios, tiempos, distancias, garantías ni resultados. Si falta un dato escribe [FALTA: ...] y di qué pedirle.
--- CONVERSACIÓN ---
{conv}
--- FIN ---

LO QUE PODEMOS PRODUCIR NOSOTROS: imágenes nuevas con Qwen-Image-Edit a partir de SUS fotos reales (encuadre, hora del día, fondo limpio, quitar textos), texto en capa exacta (titular, precio REAL si lo dio, botón de WhatsApp, logo), antes/después con sus fotos, collage de sus fotos, producto recortado sobre color, formatos 4:5 y 9:16.
NO podemos: inventar precios ni resultados, fotos de banco, promesas de salud, ni caras que no sean suyas.

ENTREGA EXACTAMENTE ESTE FORMATO:

1) DOS ÁNGULOS DE VENTA distintos (no la misma idea con otras palabras). Por cada uno:
- Nombre del ángulo
- A quién le habla y qué le duele
- La promesa concreta con el dato real que la sostiene
- Por qué baja el costo por mensaje en su giro
- Qué prueba real lo respalda (si no la tenemos: [FALTA: ...])

2) DOS ANUNCIOS DE IMAGEN (uno por ángulo). Por cada uno:
- Qué se ve y de dónde sale la foto (suya que ya tenemos / la que debe mandar / generada con Qwen a partir de cuál)
- Titular en pantalla: texto exacto, máximo 7 palabras
- Línea de apoyo: texto exacto
- Formato (4:5 o 9:16) y dónde va el botón
- Texto primario (máximo 3 renglones) y título del botón
- Calificación esperada (X/10) y qué le falta para 10

3) GUION PARA QUE ÉL LO GRABE CON SU CELULAR (20-30 s, el ángulo más fuerte):
- Frase por frase, palabra por palabra, como lo diría él
- Al lado de cada frase: qué debe estar grabando (dónde parado, qué enseña, qué se ve atrás)
- Cómo grabarlo: vertical, dónde poner el celular, luz, duración de cada toma
- Qué NO debe decir

4) QUÉ NOS TIENE QUE MANDAR ÉL para que esto califique 10.

5) SEGMENTACIÓN Y PRESUPUESTO: ciudad o radio, edad, intereses, presupuesto diario en pesos como rango (estimación).
"""

TATUADOR = """Eres la IA de calidad y estrategia de anuncios de Meta para negocios en México. Da SOLO la respuesta final, en español claro para el dueño, sin mostrar tu razonamiento.

NEGOCIO: Adrián Santana · estudio de tatuajes en el Centro de Cancún, frente al Palacio Municipal.

LAS IMÁGENES son 10 cuadros, en orden, del VIDEO QUE ÉL MISMO GRABÓ con su celular y nos mandó hoy (17 segundos, vertical 720x1280, SIN subtítulos ni textos en pantalla).
LO QUE SE ESCUCHA (transcripción automática, algunas palabras pueden venir mal escritas):
{transcripcion}

DATOS REALES de su WhatsApp (YO = el asesor, EL = el cliente):
--- CONVERSACIÓN ---
{conv}
--- FIN ---

Usa SOLO estos datos. No inventes precios, promociones ni resultados: si falta algo escribe [FALTA: ...].
Lo que podemos hacer nosotros: subtítulos palabra por palabra en capa de texto, tarjetas de texto, recortar y reordenar tomas con ffmpeg, mejorar color y ritmo, imágenes nuevas con Qwen-Image-Edit a partir de sus fotos reales, música y efectos propios. NO podemos grabar de nuevo ni inventar datos.

ENTREGA EXACTAMENTE ESTE FORMATO:

1) CALIFICACIÓN DE SU VIDEO TAL COMO ESTÁ: X/10, y PROYECTADA: X/10 si le hacemos los cambios de abajo.

2) CÓMO LLEVARLO A 8 CON LO QUE YA TENEMOS (solo cortes, textos y audio; nada de volver a grabar):
- Orden exacto de las tomas con los segundos (qué dejar, qué quitar, qué poner primero)
- Qué arreglar en cada tramo y cuánto sube la nota

3) SUBTÍTULOS EXACTOS, con tiempos, palabra por palabra como se deben ver en pantalla (corrige lo que la transcripción trae mal, en español de México, sin inventar nada). Di también tamaño, posición y color para que se lean en celular.

4) DOS ÁNGULOS DE VENTA distintos para sus anuncios (nombre, a quién le habla, promesa con dato real, por qué baja el costo por mensaje, qué prueba falta).

5) DOS ANUNCIOS DE IMAGEN, uno por ángulo: qué se ve y de dónde sale la foto, titular (máximo 7 palabras), línea de apoyo, formato, texto primario, botón, calificación esperada.

6) GUION PARA QUE GRABE EL SIGUIENTE VIDEO (20-30 s): frase por frase con lo que debe estar grabando en cada una, cómo poner el celular y la luz, y qué NO decir.

7) QUÉ NOS TIENE QUE MANDAR ÉL.
"""


def conversacion(cid):
    for f in DIG.glob(f"*__{cid}.txt"):
        return f.read_text(encoding="utf-8", errors="replace")[-7000:]
    try:
        from wa import accion
        r = accion("fetch-messages", {"chatId": f"{cid}@lid", "limit": 80})
        ms = r["data"]["data"]
        lineas = []
        for it in ms:
            d = it["message"]["_data"]
            cuerpo = (d.get("body") or d.get("caption") or "").strip()
            if not cuerpo or len(cuerpo) > 1200:
                continue
            quien = "YO" if d["id"].get("fromMe") else "EL"
            lineas.append(f"{quien}: {cuerpo}")
        return "\n".join(lineas)[-7000:] or "(sin conversación)"
    except Exception as e:
        return f"(no se pudo leer la conversación: {e})"


def main():
    D = RAIZ / "clientes/Tatuador9983316522/del_cliente_1104"
    trans = (D / "transcripcion.txt").read_text(encoding="utf-8")
    trabajos = []
    for nombre, giro, cid in ORDEN:
        conv = conversacion(cid)
        if cid == "250053667119335":
            t = {"nombre": "TATUADOR_PRIORITARIO",
                 "prompt": TATUADOR.format(transcripcion=trans, conv=conv),
                 "fotos": [str(p) for p in sorted(D.glob("c*.jpg"))[:10]]}
        else:
            clave = nombre.split(" ·")[0].replace(" ", "_")
            t = {"nombre": clave, "prompt": PLANTILLA.format(nombre=nombre, giro=giro, conv=conv), "fotos": []}
        trabajos.append(t)
        time.sleep(0.2)
    (AQUI / "lote_prioridad.json").write_text(json.dumps(trabajos, ensure_ascii=False))
    print("trabajos:", len(trabajos))
    for t in trabajos:
        print(" -", t["nombre"], "fotos:", len(t["fotos"]), "conv:", "sin conversación" not in t["prompt"])


if __name__ == "__main__":
    main()
