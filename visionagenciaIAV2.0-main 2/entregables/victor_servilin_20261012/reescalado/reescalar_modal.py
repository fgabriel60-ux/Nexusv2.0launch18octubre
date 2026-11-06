"""Reescala el video v4 de Servilin (540x960) a 1080x1920 con Real-ESRGAN x2 (spandrel) en Modal."""
import modal, sys, pathlib

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("wget", "ffmpeg")
    .pip_install("torch", "torchvision", "spandrel", "numpy", "av")
    .run_commands("wget -q -O /root/RealESRGAN_x2plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth")
)
app = modal.App("servilin-reescalado", image=imagen)


@app.function(gpu="L4", timeout=3600)
def reescalar(video: bytes) -> bytes:
    import subprocess, torch, numpy as np, av
    from spandrel import ModelLoader
    open("/root/in.mp4", "wb").write(video)
    modelo = ModelLoader().load_from_file("/root/RealESRGAN_x2plus.pth").cuda().eval().half()
    ent = av.open("/root/in.mp4")
    vs = ent.streams.video[0]
    fps = vs.average_rate
    w, h = vs.codec_context.width, vs.codec_context.height
    # tubería a ffmpeg: cuadros crudos -> H.264 1080p, audio original copiado
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w*2}x{h*2}", "-r", str(float(fps)), "-i", "-",
         "-i", "/root/in.mp4", "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "/root/out.mp4"],
        stdin=subprocess.PIPE)
    n = 0
    for fr in ent.decode(video=0):
        x = torch.from_numpy(fr.to_ndarray(format="rgb24")).permute(2, 0, 1)[None].cuda().half() / 255
        with torch.no_grad():
            y = modelo(x)
        ff.stdin.write((y.clamp(0, 1)[0].permute(1, 2, 0).float().cpu().numpy() * 255).round().astype(np.uint8).tobytes())
        n += 1
    ff.stdin.close(); ff.wait()
    print("cuadros:", n, "salida:", w * 2, "x", h * 2)
    return open("/root/out.mp4", "rb").read()


@app.local_entrypoint()
def main(origen: str, destino: str):
    pathlib.Path(destino).write_bytes(reescalar.remote(pathlib.Path(origen).read_bytes()))
    print("listo ->", destino)
