#!/usr/bin/env python3
"""Arma una hoja de personaje desde los VIDEOS REALES de un cliente.

Para qué: cuando se le pide a Codex «una imagen de esta persona», una sola foto no basta y la
cara termina pareciéndose a otro. Esta hoja junta varias tomas reales suyas —distintos ángulos,
luces y momentos— para dársela como referencia de identidad.

Cómo elige, sin detector de caras: este Codespace no puede correr mediapipe (le falta libEGL) y
el OpenCV instalado viene sin los clasificadores Haar. Así que se usa lo que sí hay: se sacan
cuadros cada medio segundo, se mide la nitidez con el laplaciano, y se eligen los más nítidos
separados entre sí en el tiempo, para que no salgan ocho veces el mismo gesto. Arriba van
recortes de la zona de la cara (en un video de celular la cara cae en el tercio superior
central) y abajo los cuadros completos, que muestran ropa y complexión.

Uso: python3 herramientas/character_sheet.py "clientes/X/**/*.mp4" salida.jpg "NOMBRE"
"""
import glob
import sys

import cv2
import numpy as np


def cuadros(rutas, cada=0.5, maximo=400):
    fuera = []
    for r in rutas:
        cap = cv2.VideoCapture(r)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        salto = max(1, int(fps * cada))
        i = 0
        while len(fuera) < maximo:
            ok, fr = cap.read()
            if not ok:
                break
            if i % salto == 0:
                g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
                al, an = g.shape
                zona = g[int(al * 0.10):int(al * 0.62), int(an * 0.18):int(an * 0.82)]
                nit = cv2.Laplacian(zona, cv2.CV_64F).var()
                # ¿hay una persona? Sin detector de caras (este equipo no puede con mediapipe ni
                # trae los Haar), se busca TONO DE PIEL en el centro del cuadro. Es lo que separa
                # una toma de la persona de una toma de dron, que por detalle sale más "nítida"
                # y se colaba siempre.
                c = fr[int(al * 0.10):int(al * 0.62), int(an * 0.18):int(an * 0.82)]
                ycc = cv2.cvtColor(c, cv2.COLOR_BGR2YCrCb)
                piel = cv2.inRange(ycc, (0, 133, 77), (255, 173, 127))
                prop = float(piel.mean()) / 255.0
                fuera.append({"fr": fr, "n": nit, "piel": prop, "video": r, "t": i / fps})
            i += 1
        cap.release()
    return fuera


def elegir(cands, n=8, separacion=1.5, min_piel=0.04):
    """Primero los cuadros donde se ve a la persona (tono de piel), y entre esos, los más nítidos.

    Si el video no tiene a nadie —pasó con los videos de producto de estos clientes— se cae a
    ordenar solo por nitidez, pero se avisa, porque entonces la hoja no sirve de referencia.
    """
    con_gente = [c for c in cands if c.get("piel", 0) >= min_piel]
    if con_gente:
        cands = con_gente
        print(f"  {len(con_gente)} cuadros con persona a cuadro")
    else:
        print("  AVISO: ningun cuadro parece tener a una persona; este video es de producto")
    cands.sort(key=lambda c: -(c["n"] * 0.5 + c.get("piel", 0) * 4000))
    sel = []
    for c in cands:
        if any(c["video"] == s["video"] and abs(c["t"] - s["t"]) < separacion for s in sel):
            continue
        sel.append(c)
        if len(sel) >= n:
            break
    return sel


def hoja(sel, salida, nombre, celda=300):
    cols = max(1, len(sel) // 2)
    lienzo = np.full((2 * celda + 96, cols * celda, 3), 20, np.uint8)
    cv2.putText(lienzo, f"HOJA DE PERSONAJE: {nombre}", (16, 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (240, 240, 240), 2)
    cv2.putText(lienzo, "arriba: rostro  ·  abajo: cuerpo y ropa  ·  cuadros reales de sus videos",
                (16, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (170, 170, 170), 1)
    for k, c in enumerate(sel[:cols * 2]):
        fr = c["fr"]
        al, an = fr.shape[:2]
        if k < cols:   # fila de arriba: acercamiento a la cara
            y0, y1 = int(al * 0.05), int(al * 0.52)
            x0, x1 = int(an * 0.16), int(an * 0.84)
            rec = fr[y0:y1, x0:x1]
        else:          # fila de abajo: el cuadro completo
            rec = fr
        lado = min(rec.shape[0], rec.shape[1])
        cy, cx = rec.shape[0] // 2, rec.shape[1] // 2
        rec = rec[max(0, cy - lado // 2):cy + lado // 2, max(0, cx - lado // 2):cx + lado // 2]
        rec = cv2.resize(rec, (celda, celda))
        f, col = divmod(k, cols)
        lienzo[96 + f * celda:96 + (f + 1) * celda, col * celda:(col + 1) * celda] = rec
    cv2.imwrite(salida, lienzo, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return salida


if __name__ == "__main__":
    patron, salida, nombre = sys.argv[1], sys.argv[2], sys.argv[3]
    rutas = sorted(glob.glob(patron, recursive=True))
    print(f"{len(rutas)} videos")
    c = cuadros(rutas)
    print(f"{len(c)} cuadros revisados")
    s = elegir(c, 8)
    print("elegidos:", [(x["video"].split("/")[-1][:20], round(x["t"], 1), int(x["n"])) for x in s])
    print("hoja:", hoja(s, salida, nombre))
