"""Ensambla el video final desde los clips H3: tramos con velocidad (cámara lenta), crossfades cortos, rótulos de fase, SFX sintéticos y pad suave.
Uso: python3 armar.py plan_vN.json   -> pajaro_realista_vN.mp4 (H.264 Main, 720x1280, <16 MB)
plan: {"salida": "pajaro_realista_v1.mp4", "xfade": 0.25,
       "tramos": [{"clip": "K1", "ini": 0, "fin": 5.0, "vel": 1.0, "rotulo": "Lanzamiento"}...],
       "sfx": [[seg, "whoosh"|"clic"|"aleteo", {kw}], ...]}"""
import json, pathlib, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

AQUI = pathlib.Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 24
sys.path.insert(0, str(AQUI))
import sfx  # noqa: E402


def leer_cuadros(ruta):
    p = subprocess.run([FF, "-v", "error", "-i", str(ruta), "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)


def retimar(fr, ini, fin, vel, reversa=False):
    a, b = int(round(ini * FPS)), min(len(fr), int(round(fin * FPS)))
    seg = fr[a:b][::-1] if reversa else fr[a:b]
    n = max(2, int(round(len(seg) / vel)))
    pos = np.linspace(0, len(seg) - 1, n)
    out = np.empty((n, H, W, 3), np.uint8)
    for k, p in enumerate(pos):         # mezcla lineal entre cuadros vecinos (cámara lenta suave)
        i = int(p); f = p - i; j = min(i + 1, len(seg) - 1)
        out[k] = seg[i] if f < 1e-3 else (seg[i] * (1 - f) + seg[j] * f).astype(np.uint8)
    return out


def rotulo(texto):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=f)
    w, h = x1 - x0, y1 - y0; x, y = (W - w) // 2, 120
    d.rounded_rectangle((x - 24, y - 16, x + w + 24, y + h + 26), 18, fill=(0, 0, 0, 120))
    d.text((x - x0, y - y0 + 4), texto, font=f, fill=(255, 236, 200, 255))
    a = np.array(img).astype(np.float32)
    return a[..., :3], a[..., 3:] / 255.0


def main(plan_path):
    plan = json.loads((AQUI / plan_path).read_text())
    xf = int(round(plan.get("xfade", 0.25) * FPS))
    cache, video, marcas = {}, None, []
    for t in plan["tramos"]:
        if t["clip"] not in cache:
            cache[t["clip"]] = leer_cuadros(AQUI / "clips" / f"{t['clip']}.mp4")
        seg = retimar(cache[t["clip"]], t.get("ini", 0), t.get("fin", 99), t.get("vel", 1.0), t.get("reversa", False))
        if t.get("rotulo"):
            rgb, al = rotulo(t["rotulo"])
            n = min(len(seg), int(1.6 * FPS))
            for k in range(n):
                fade = min(1, k / 5, (n - k) / 5)
                seg[k] = (seg[k] * (1 - al * fade) + rgb * al * fade).astype(np.uint8)
        if video is None:
            marcas.append(0.0); video = seg
        else:
            x = xf if t.get("xfade", True) else 0
            if x:
                w = np.linspace(0, 1, x)[:, None, None, None]
                mezcla = (video[-x:] * (1 - w) + seg[:x] * w).astype(np.uint8)
                video = np.concatenate([video[:-x], mezcla, seg[x:]])
                marcas.append((len(video) - len(seg)) / FPS)
            else:
                marcas.append(len(video) / FPS); video = np.concatenate([video, seg])
    dur = len(video) / FPS
    print("duración", round(dur, 2), "s · inicios de tramo", [round(m, 2) for m in marcas])
    eventos = [(s if not isinstance(s, str) else marcas[int(s.split("+")[0][1:])] + float(s.split("+")[1]), tipo, kw) for s, tipo, kw in plan["sfx"]]
    audio = sfx.pista(eventos, dur, plan.get("musica", True))
    wav = AQUI / "clips" / "_audio.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sfx.SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    salida = AQUI / plan["salida"]
    p = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
                          "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-pix_fmt", "yuv420p", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M",
                          "-preset", "slow", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", str(salida)], stdin=subprocess.PIPE)
    p.stdin.write(video.tobytes()); p.stdin.close(); p.wait()
    print("guardado", salida, round(salida.stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main(sys.argv[1])
