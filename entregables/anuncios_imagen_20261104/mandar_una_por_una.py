"""Manda a Carlos cada anuncio POR SEPARADO con su calificación y las sugerencias para subirla
(pedido del 5 nov 2026). Lee las imágenes de anuncios_v2/ y su calificación de calificaciones_v2/.
  python3 entregables/anuncios_imagen_20261104/mandar_una_por_una.py [NOMBRE_PARCIAL]
"""
import base64, os, pathlib, re, sys, time
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/herramientas")
from wa import accion

AQUI = pathlib.Path(__file__).resolve().parent
CARLOS = "44522318905388@lid"
TITULOS = {
    "MARIANO_A1_tres_casas": "MARIANO · Ángulo A1 · las 3 casas reales",
    "MARIANO_A2_recorrido": "MARIANO · Ángulo A2 · «te las muestro por dentro»",
    "MARIANO_B1_benjamina_precio": "MARIANO · Ángulo B1 · Benjamina desde $2.8 MDP",
    "MARIANO_B2_cita": "MARIANO · Ángulo B2 · «pide tu cita»",
    "RAFAEL_1A_prueba_manejo": "RAFAEL · Ángulo 1A · prueba de manejo",
    "RAFAEL_1B_subete": "RAFAEL · Ángulo 1B · «súbete y pruébalo»",
    "RAFAEL_2A_asesor": "RAFAEL · Ángulo 2A · «te contesto yo, no un bot»",
    "RAFAEL_2B_whatsapp": "RAFAEL · Ángulo 2B · «pregúntame por WhatsApp»",
    "MANUEL_A1_retrato": "MANUEL · Ángulo A1 · retrato de la quinceañera",
    "MANUEL_A2_collage": "MANUEL · Ángulo A2 · la fiesta completa",
    "MANUEL_B1_agenda": "MANUEL · Ángulo B1 · «agenda tu fecha»",
    "MANUEL_B2_fecha": "MANUEL · Ángulo B2 · «apartamos tu fecha»",
}


def bloque(texto, titulo, hasta):
    m = re.search(rf"{titulo}.*?\n(.*?)(?=\n(?:{hasta}))", texto, re.S)
    if not m:
        return []
    return [l.strip("-• ").strip() for l in m.group(1).strip().split("\n") if l.strip().startswith("-")]


def mensaje(nombre, texto):
    act = re.search(r"CALIFICACION:\s*([\d.]+)", texto)
    pro = re.search(r"PROYECTADA:\s*([\d.]+)", texto)
    porque = bloque(texto, "POR QUÉ FUNCIONA", "QUÉ LO FRENA")
    frena = bloque(texto, "QUÉ LO FRENA", "PLAN PARA")
    l = [f"📊 *{TITULOS.get(nombre, nombre)}*", ""]
    if act:
        l.append(f"*Calificación de Facebook hoy: {act.group(1)}/10*" + (f" → con los cambios: *{pro.group(1)}/10*" if pro else ""))
        l.append("")
    if porque:
        l.append("✅ *Por qué funciona*")
        l += [f"• {p}" for p in porque[:3]]
        l.append("")
    if frena:
        l.append("🔧 *Qué lo frena y cómo sube*")
        l += [f"• {p}" for p in frena[:3]]
    return "\n".join(l)[:4000]


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    for img in sorted((AQUI / "anuncios_v2").glob("*.jpg")):
        if filtro and filtro not in img.stem:
            continue
        cal = AQUI / "calificaciones_v2" / f"{img.stem}.md"
        if not cal.exists():
            print("sin calificación todavía:", img.stem); continue
        cap = mensaje(img.stem, cal.read_text())
        b = base64.b64encode(img.read_bytes()).decode()
        for i in range(4):
            r = accion("send-media", {"chatId": CARLOS, "mediaBase64": b,
                                      "mediaName": img.name, "mediaCaption": cap})
            if r and r.get("data", {}).get("status") == "success":
                print("enviada", img.stem); break
            time.sleep(6 * (i + 1))
        else:
            print("FALLÓ", img.stem)
        time.sleep(3)


if __name__ == "__main__":
    main()
