"""Mide cuánto dura cada cierre candidato con la voz elegida (Narrador v2), para ver cuál cabe.

Carlos (17 sep): «haz el cierre con llamada a la acción con esa voz y que diga Veneers Dental».
El hueco real es del segundo 30 al 35: 5 s para la corona + el cierre.
También prueba dos escrituras de la marca, porque el TTS puede leer "Veneers" a la inglesa
o a la española y no lo puedo juzgar de oído.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voz_adictiva import habla, env, dura, VOCES

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "_cierres"); os.makedirs(TMP, exist_ok=True)
REF = VOCES["narrador"][0]

CANDIDATOS = {
    "corona_corta":   "Encima va tu corona nueva.",
    "corona_larga":   "Encima, una corona igual a tus dientes.",
    "A_sonrisa_marca":    "Y vuelves a sonreír. Veneers Dental.",
    "B_agenda":           "Agenda tu valoración en Veneers Dental.",
    "C_sonrisa_agenda":   "Y vuelves a sonreír. Agenda tu cita en Veneers Dental.",
    "D_solo_marca":       "Veneers Dental.",
    "E_pregunta":         "Vuelve a sonreír. Pregunta en Veneers Dental.",
    # misma frase, marca escrita a la española, para comparar cómo la lee
    "A_fonetico":         "Y vuelves a sonreír. Viníers Dental.",
    "B_fonetico":         "Agenda tu valoración en Viníers Dental.",
}

if __name__ == "__main__":
    llave = env("FISH_API_KEY")
    for clave, texto in CANDIDATOS.items():
        mp3 = os.path.join(TMP, clave + ".mp3")
        if not os.path.exists(mp3):
            habla(texto, mp3, llave, REF, 0.98)
        print("%-18s %5.2f s   %s" % (clave, dura(mp3), texto))
