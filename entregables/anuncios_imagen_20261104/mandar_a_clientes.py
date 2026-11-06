"""Manda a CADA CLIENTE sus propias imágenes con la calificación de Facebook y le pide aprobación
para aplicar las sugerencias (autorizado por Carlos el 5 nov 2026).
  python3 entregables/anuncios_imagen_20261104/mandar_a_clientes.py MARIANO
"""
import base64, pathlib, re, sys, time
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/herramientas")
from wa import accion

AQUI = pathlib.Path(__file__).resolve().parent
CLIENTES = {
    "MARIANO": ("27337584279694@lid", "Mariano"),
    "RAFAEL": ("225412869304444@lid", "Rafael"),
    "MANUEL": ("177558293323885@lid", "Manuel"),
}
TITULOS = {
    "MARIANO_A1_tres_casas": "Las 3 casas · Bugambilia, Benjamina y Salvia",
    "MARIANO_A2_recorrido": "«Te las muestro por dentro»",
    "MARIANO_B1_benjamina_precio": "Benjamina desde $2.8 MDP",
    "MARIANO_B2_cita": "«Pide tu cita y te abro la casa»",
    "RAFAEL_1A_prueba_manejo": "Prueba de manejo",
    "RAFAEL_1B_subete": "«Súbete y pruébalo»",
    "RAFAEL_2A_asesor": "«Te contesto yo, no un bot»",
    "RAFAEL_2B_whatsapp": "«Pregúntame por WhatsApp»",
    "MANUEL_A1_retrato": "Retrato de la quinceañera",
    "MANUEL_A2_collage": "La fiesta completa",
    "MANUEL_B1_agenda": "«Agenda tu fecha»",
    "MANUEL_B2_fecha": "«Apartamos tu fecha hoy»",
}


def bloque(texto, titulo, hasta):
    m = re.search(rf"{titulo}.*?\n(.*?)(?=\n(?:{hasta}))", texto, re.S)
    return [l.strip("-• ").strip() for l in m.group(1).strip().split("\n") if l.strip().startswith("-")] if m else []


def caption(nombre, texto, i, total):
    act = re.search(r"CALIFICACION:\s*([\d.]+)", texto)
    pro = re.search(r"PROYECTADA:\s*([\d.]+)", texto)
    l = [f"🖼️ *Anuncio {i} de {total} · {TITULOS.get(nombre, nombre)}*", ""]
    if act:
        l.append(f"📊 Calificación de Facebook hoy: *{act.group(1)}/10*" + (f" → con los ajustes: *{pro.group(1)}/10*" if pro else ""))
        l.append("")
    pq = bloque(texto, "POR QUÉ FUNCIONA", "QUÉ LO FRENA")
    if pq:
        l.append("✅ *Lo que ya jala*")
        l += [f"• {p}" for p in pq[:2]]
        l.append("")
    fr = bloque(texto, "QUÉ LO FRENA", "PLAN PARA")
    if fr:
        l.append("🔧 *Lo que le falta para subir*")
        l += [f"• {p}" for p in fr[:3]]
    return "\n".join(l)[:4000]


def main():
    cli = sys.argv[1].upper()
    chat, nombre = CLIENTES[cli]
    imgs = sorted((AQUI / "anuncios_v2").glob(f"{cli}_*.jpg"))
    listas = [p for p in imgs if (AQUI / "calificaciones_v2" / f"{p.stem}.md").exists()]
    intro = (f"{nombre}, le preparé *{len(listas)} anuncios de imagen* para su campaña 👇\n\n"
             "Son dos ideas distintas, con dos versiones cada una, y ya pasaron por la calificación de calidad "
             "de la IA de Facebook. Se los mando uno por uno con su nota y lo que le falta a cada uno.\n\n"
             "Le voy a ser franco de por qué le mando imágenes: en mi propia publicidad *una imagen me rindió "
             "mucho más que el video*. Y hay otra razón práctica: llevar un video a calificación 8 tarda mucho "
             "más (hay que corregir tomas, voz, ritmo y subtítulos), mientras que una imagen se corrige y se "
             "vuelve a calificar en minutos. Por eso me adelanté con estas, para que su publicidad salga antes. "
             "Su video también va avanzando en paralelo.")
    accion("send-message", {"chatId": chat, "message": intro}); time.sleep(2)
    for i, img in enumerate(listas, 1):
        cal = (AQUI / "calificaciones_v2" / f"{img.stem}.md").read_text()
        b = base64.b64encode(img.read_bytes()).decode()
        for k in range(4):
            r = accion("send-media", {"chatId": chat, "mediaBase64": b, "mediaName": img.name,
                                      "mediaCaption": caption(img.stem, cal, i, len(listas))})
            if r and r.get("data", {}).get("status") == "success":
                print("enviada", img.stem); break
            time.sleep(6 * (k + 1))
        time.sleep(3)
    cierre = ("¿Me da el visto bueno para *aplicar esos ajustes* y dejarlos listos para subir? 🙌\n\n"
              "Si quiere agregar o cambiar algo (un dato, una promoción, una foto suya que prefiera), dígamelo "
              "ahorita y lo meto en la misma vuelta.\n\n"
              "Recuerde el criterio: *no subimos nada abajo de 8 de 10*. Abajo de 8 se paga por vistas y no "
              "llegan mensajes. Con su aprobación los dejo en 8 o más y arrancamos.")
    accion("send-message", {"chatId": chat, "message": cierre})
    print("cierre enviado a", nombre)


if __name__ == "__main__":
    main()
