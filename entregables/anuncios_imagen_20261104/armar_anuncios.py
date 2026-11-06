"""Arma los anuncios de IMAGEN 4:5 (1080x1350) para Meta: foto + titular + línea de apoyo + botón de WhatsApp.

Pedido de Carlos (4 nov 2026): dos ángulos por cliente y DOS imágenes por ángulo.
El texto va SIEMPRE en capa aparte (nunca generado dentro de la imagen) y los datos son reales del cliente.
  python3 entregables/anuncios_imagen_20261104/armar_anuncios.py
"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

RAIZ = pathlib.Path("/workspaces/Nexusv2.0launch18octubre")
FUENTE = RAIZ / "visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf"
SALIDA = RAIZ / "entregables/anuncios_imagen_20261104/anuncios"
W, H = 1080, 1350


def fu(t, peso=900):
    f = ImageFont.truetype(str(FUENTE), t)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def _encaja(ruta, w=W, h=H):
    return ImageOps.fit(Image.open(ruta).convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.4))


def collage3(rutas):
    """Una foto grande arriba y dos abajo: sirve para enseñar 3 casas reales de un jalón."""
    lienzo = Image.new("RGB", (W, H), "white")
    g = _encaja(rutas[0], W, int(H * 0.62))
    lienzo.paste(g, (0, 0))
    y = int(H * 0.62) + 6
    for k, r in enumerate(rutas[1:3]):
        p = _encaja(r, (W - 6) // 2, H - y)
        lienzo.paste(p, (k * ((W - 6) // 2 + 6), y))
    return lienzo


def anuncio(base, titular, apoyo, boton="Enviar WhatsApp", pie="", etiqueta="", sombra=0.46,
            bullets=(), sello=""):
    """bullets: hasta 3 líneas cortas de valor (lo que Glimmer pidió para subir oferta).
    sello: nombre y puesto del asesor, para que se vea de quién es el anuncio (confianza)."""
    im = base.convert("RGB").copy()
    d = ImageDraw.Draw(im, "RGBA")
    # degradado inferior para que el texto se lea sobre cualquier foto
    alto = int(H * sombra)
    capa = Image.new("RGBA", (W, alto), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    for i in range(alto):
        dc.line([(0, i), (W, i)], fill=(8, 12, 18, int(252 * (i / alto) ** 1.35)))
    im.paste(capa, (0, H - alto), capa)

    if etiqueta:
        f = fu(34, 800)
        an = d.textlength(etiqueta, font=f) + 54
        d.rounded_rectangle((44, 44, 44 + an, 108), 32, fill=(255, 255, 255, 235))
        d.text((44 + an / 2, 76), etiqueta, font=f, fill=(18, 26, 38), anchor="mm")

    y = H - alto + 110
    f = fu(84, 900)
    lineas, linea = [], ""
    for p in titular.upper().split():
        if d.textlength((linea + " " + p).strip(), font=f) > W - 130:
            lineas.append(linea); linea = p
        else:
            linea = (linea + " " + p).strip()
    lineas.append(linea)
    for ln in lineas:
        d.text((64, y), ln, font=f, fill="white")
        y += 94
    if apoyo:
        fa = fu(40, 600)
        d.text((66, y + 12), apoyo, font=fa, fill=(236, 214, 150))
        y += 74
    if bullets:
        fbu = fu(31, 600)
        for b in list(bullets)[:3]:
            d.ellipse((66, y + 10, 84, y + 28), fill=(72, 200, 130, 255))
            d.text((98, y + 19), b, font=fbu, fill=(236, 236, 236), anchor="lm")
            y += 42
        y += 6
    if sello:
        fs = fu(27, 700)
        an = d.textlength(sello, font=fs) + 40
        d.rounded_rectangle((64, y, 64 + an, y + 46), 23, fill=(255, 255, 255, 36),
                            outline=(236, 214, 150, 170), width=2)
        d.text((84, y + 23), sello, font=fs, fill=(236, 214, 150), anchor="lm")
        y += 58
    # botón de WhatsApp
    fb = fu(40, 800)
    an = d.textlength(boton, font=fb) + 112
    y0 = max(y + 6, H - 180)
    d.rounded_rectangle((64, y0, 64 + an, y0 + 86), 43, fill=(37, 211, 102, 255))
    d.ellipse((92, y0 + 22, 134, y0 + 64), fill="white")
    d.text((154, y0 + 43), boton, font=fb, fill=(10, 40, 24), anchor="lm")
    return im


def logo(im, ruta, ancho=210):
    """Pega el logotipo real del cliente arriba a la derecha, con su transparencia."""
    lg = Image.open(ruta).convert("RGBA")
    lg = lg.resize((ancho, int(lg.height * ancho / lg.width)), Image.LANCZOS)
    im = im.convert("RGBA")
    im.alpha_composite(lg, (W - ancho - 48, 44))
    return im.convert("RGB")


def guardar(im, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    p = SALIDA / nombre
    im.save(p, quality=92)
    print("guardado", p)


def main():
    M = RAIZ / "clientes/Mariano/anuncios/refs"
    C = RAIZ / "entregables/anuncios_imagen_20261104/cuadros"

    # ---- MARIANO · Ángulo A: las 3 casas reales ----
    guardar(anuncio(collage3([M / "benjamina_fachada.jpg", M / "bugambilia_calle.jpg", M / "salvia_fachada.jpg"]),
                    "3 casas en Vizcaíno", "Bugambilia · Benjamina · Salvia",
                    pie="Rosarito, B.C. · Grupo Lagsa", etiqueta="ROSARITO, B.C.", sombra=0.42),
            "MARIANO_A1_tres_casas.jpg")
    if (C / "MAR_A2.png").exists():
        guardar(anuncio(_encaja(C / "MAR_A2.png"), "Te las muestro por dentro",
                        "Las 3 casas, en un solo recorrido", etiqueta="VIZCAÍNO RESIDENCIAL"),
                "MARIANO_A2_recorrido.jpg")

    # ---- MARIANO · Ángulo B: precio de entrada real ----
    guardar(anuncio(_encaja(M / "benjamina_fachada.jpg"), "Benjamina desde $2.8 MDP",
                    "Vizcaíno Residencial, Rosarito", pie="Precio que da el desarrollador · aplican restricciones",
                    etiqueta="MODELO BENJAMINA"),
            "MARIANO_B1_benjamina_precio.jpg")
    if (C / "MAR_B2.png").exists():
        guardar(anuncio(_encaja(C / "MAR_B2.png"), "Pide tu cita y te abro la casa",
                        "Benjamina desde $2.8 MDP", pie="Aplican restricciones", etiqueta="ROSARITO, B.C."),
                "MARIANO_B2_cita.jpg")

    # ---- RAFAEL · Ángulo 1: prueba de manejo ----
    manuel()

    for arch, tit, ap, nom in [
        ("RAF_1A.png", "Prueba de manejo", "Agenda la tuya por WhatsApp", "RAFAEL_1A_prueba_manejo.jpg"),
        ("RAF_1B.png", "Súbete y pruébalo", "Yo te acompaño en la prueba", "RAFAEL_1B_subete.jpg"),
        ("RAF_2A.png", "Te contesto yo, no un bot", "Rafael, asesor BYD", "RAFAEL_2A_asesor.jpg"),
        ("RAF_2B.png", "Pregúntame por WhatsApp", "Te paso versiones y disponibilidad", "RAFAEL_2B_whatsapp.jpg"),
    ]:
        if (C / arch).exists():
            guardar(anuncio(_encaja(C / arch), tit, ap, etiqueta="BYD"), nom)


def manuel():
    """Manuel · Hunab Ku, fotografía de XV. Fotos REALES de su trabajo (no generadas).
    Pendiente: que Manuel confirme que la familia autoriza usar estas fotos en anuncios."""
    F = RAIZ / "clientes/XV/frames_real"
    LG = RAIZ / "clientes/Manuel_fotografia/logo/logo_nuevo_sin_fondo.png"
    a1 = anuncio(_encaja(F / "base_7_retrato.png"), "Tu quinceañera, luz y sonrisa",
                 "Fotografía y video de XV", etiqueta="HUNAB KU")
    guardar(logo(a1, LG), "MANUEL_A1_retrato.jpg")
    a2 = anuncio(collage3([F / "base_1_heroe.png", F / "base_4_amigas.png", F / "base_6_familia.png"]),
                 "Así se ve tu XV con nosotros", "Tu fiesta completa, no solo el vals",
                 etiqueta="HUNAB KU", sombra=0.42)
    guardar(logo(a2, LG), "MANUEL_A2_collage.jpg")
    b1 = anuncio(_encaja(F / "base_3_xv.png"), "Agenda tu fecha por WhatsApp",
                 "Las fechas buenas se apartan antes", etiqueta="HUNAB KU")
    guardar(logo(b1, LG), "MANUEL_B1_agenda.jpg")
    b2 = anuncio(_encaja(F / "base_8_detalle.png"), "Apartamos tu fecha hoy",
                 "Escríbenos y te decimos si está libre",
                 pie="Hunab Ku Fotografía · WhatsApp 631 126 5175", etiqueta="HUNAB KU")
    guardar(logo(b2, LG), "MANUEL_B2_fecha.jpg")


def v2():
    """Segunda versión (5 nov 2026): aplica lo que pidió Glimmer sobre las v1 —
    precios y amenidades reales, sello del asesor, llamado concreto y el texto fuera de la cara.
    Las imágenes base de las personas ahora salen de Codex (regla de Carlos del 4 nov)."""
    global SALIDA
    SALIDA = RAIZ / "entregables/anuncios_imagen_20261104/anuncios_v2"
    M = RAIZ / "clientes/Mariano/anuncios/refs"
    C = RAIZ / "entregables/anuncios_imagen_20261104/codex"
    F = RAIZ / "clientes/XV/frames_real"
    LG = RAIZ / "clientes/Manuel_fotografia/logo/logo_nuevo_sin_fondo.png"
    PRECIOS = ("Bugambilia desde $2.4 MDP", "Benjamina desde $2.8 MDP", "Salvia desde $3.1 MDP · 4 rec")
    AMEN = ("Acceso controlado", "Plaza comercial y pádel", "Área de juegos")
    SELLO_M = "Mariano Herrera · Asesor · Vizcaíno Residencial"

    guardar(anuncio(collage3([M / "benjamina_fachada.jpg", M / "bugambilia_calle.jpg", M / "salvia_fachada.jpg"]),
                    "3 casas en Vizcaíno", "Rosarito, B.C.", boton="Quiero el recorrido",
                    etiqueta="VIZCAÍNO RESIDENCIAL", sombra=0.52, bullets=PRECIOS, sello=SELLO_M,
                    pie="Precios del desarrollador · aplican restricciones"),
            "MARIANO_A1_tres_casas.jpg")
    guardar(anuncio(_encaja(C / "MAR_A2_codex.png"), "Te las muestro por dentro", "Las 3 casas en un recorrido",
                    boton="Quiero el recorrido", etiqueta="VIZCAÍNO RESIDENCIAL", sombra=0.5,
                    bullets=PRECIOS, sello=SELLO_M, pie="Aplican restricciones"),
            "MARIANO_A2_recorrido.jpg")
    guardar(anuncio(_encaja(M / "benjamina_fachada.jpg"), "Benjamina desde $2.8 MDP", "Vizcaíno Residencial, Rosarito",
                    boton="Recorrido y precios", etiqueta="MODELO BENJAMINA", sombra=0.5,
                    bullets=AMEN, sello=SELLO_M, pie="Precio del desarrollador · aplican restricciones"),
            "MARIANO_B1_benjamina_precio.jpg")
    guardar(anuncio(_encaja(C / "MAR_B2_codex.png"), "Pide tu cita y te abro la casa", "Benjamina desde $2.8 MDP",
                    boton="Recorrido y precios", etiqueta="ROSARITO, B.C.", sombra=0.5,
                    bullets=AMEN, sello=SELLO_M, pie="Aplican restricciones"),
            "MARIANO_B2_cita.jpg")

    SELLO_R = "Rafael · Asesor BYD"
    for arch, tit, ap, bot, nom in [
        ("RAF_1A_codex.png", "Prueba de manejo", "Agenda la tuya por WhatsApp", "Agendar prueba", "RAFAEL_1A_prueba_manejo.jpg"),
        ("RAF_1B_codex.png", "Súbete y pruébalo", "Yo te acompaño en la prueba", "Agendar prueba", "RAFAEL_1B_subete.jpg"),
        ("RAF_2A_codex.png", "Te contesto yo, no un bot", "Dudas, versiones y disponibilidad", "Escribirle a Rafael", "RAFAEL_2A_asesor.jpg"),
        ("RAF_2B_codex.png", "Pregúntame por WhatsApp", "Te paso versiones y disponibilidad", "Escribirle a Rafael", "RAFAEL_2B_whatsapp.jpg"),
    ]:
        guardar(anuncio(_encaja(C / arch), tit, ap, boton=bot, etiqueta="BYD", sombra=0.48,
                        bullets=("Te atiendo yo, no un bot", "Te digo versiones y disponibilidad"),
                        sello=SELLO_R),
                nom)

    SELLO_X = "Hunab Ku · Fotografía de XV"
    BUL_X = ("Fotografía y video", "Cubrimos toda la fiesta", "WhatsApp 631 126 5175")
    for arch, tit, ap, nom, col in [
        ("base_7_retrato.png", "Tu quinceañera, luz y sonrisa", "Recuerdo que dura", "MANUEL_A1_retrato.jpg", False),
        (None, "Así se ve tu XV con nosotros", "Tu fiesta completa, no solo el vals", "MANUEL_A2_collage.jpg", True),
        ("base_3_xv.png", "Agenda tu fecha por WhatsApp", "Las fechas buenas se apartan antes", "MANUEL_B1_agenda.jpg", False),
        ("base_8_detalle.png", "Apartamos tu fecha hoy", "Te decimos si está libre", "MANUEL_B2_fecha.jpg", False),
    ]:
        base = (collage3([F / "base_1_heroe.png", F / "base_4_amigas.png", F / "base_6_familia.png"])
                if col else _encaja(F / arch))
        im = anuncio(base, tit, ap, boton="Apartar fecha", etiqueta="HUNAB KU", sombra=0.52,
                     bullets=BUL_X, sello=SELLO_X)
        guardar(logo(im, LG), nom)


if __name__ == "__main__":
    import sys
    if "--v2" in sys.argv:
        v2()
    else:
        main()
