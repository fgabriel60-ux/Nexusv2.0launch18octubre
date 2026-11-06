"""Une el video final de la fiesta (video_grupo_edit_diente.mp4, con su audio) con los tres clips de Kling:
cara → close-up del hueco → pantalla dividida → solo dientes y encía. Cortes directos: cada clip empieza en el
último cuadro del anterior. Salida 1080×1920 a 24 fps y versión ligera para WhatsApp, más hoja de revisión.
Uso: python3 montar_transicion.py"""
import os, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
FINAL = ("/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/"
         "clientes/Vision Agencia/veneers_dental/video_grupo_edit_diente.mp4")
CLIPS = [os.path.join(AQUI, n) for n in ("CLIP1_CARA_A_CLOSEUP.mp4", "CLIP2_CLOSEUP_A_PANTALLA_DIVIDIDA.mp4",
                                         "CLIP3_PANTALLA_DIVIDIDA_A_SOLO_DIENTES.mp4")]
SALIDA = os.path.join(AQUI, "IMPLANTE_TRANSICION_KLING_1080.mp4")
WHATSAPP = os.path.join(AQUI, "IMPLANTE_TRANSICION_KLING_WHATSAPP.mp4")


def dur(r):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", r]).decode())


norm = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=24,setsar=1,format=yuv420p"
entradas = [FINAL] + CLIPS
filtro = "".join("[%d:v]%s,setpts=PTS-STARTPTS[v%d];" % (i, norm, i) for i in range(len(entradas)))
filtro += "".join("[v%d]" % i for i in range(len(entradas))) + "concat=n=%d:v=1:a=0[v];" % len(entradas)
total = sum(dur(e) for e in entradas)
filtro += "[0:a]aresample=48000,apad,atrim=0:%.3f[a]" % total
subprocess.run(["ffmpeg", "-v", "error", "-y", *sum((["-i", e] for e in entradas), []), "-filter_complex", filtro,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac",
                "-b:a", "192k", "-movflags", "+faststart", SALIDA], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SALIDA, "-vf", "scale=720:1280", "-c:v", "libx264", "-crf", "25",
                "-preset", "slow", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", WHATSAPP], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % max(0, dur(FINAL) - 1.5), "-i", SALIDA, "-vf",
                "fps=2,scale=180:320,tile=11x3", "-frames:v", "1", os.path.join(AQUI, "REVISION_TRANSICION.jpg")], check=True)
print("listo", SALIDA, "duración %.2f s" % dur(SALIDA))
