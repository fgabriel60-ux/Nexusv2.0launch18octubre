"""Glimmer (Muse-Glimmer-30B) como servicio web para chatear rápido desde el artifact.
Desplegar:  MODAL_PROFILE=carlosfavelajeje MODAL_IMAGE_BUILDER_VERSION=2025.06 modal deploy modelos_modal/glimmer_chat_web.py
La clave va en el secreto de Modal `glimmer-chat` (variable CLAVE). Se apaga solo tras 10 min sin uso."""
import base64, io, os
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "accelerate", "pillow", "sentencepiece", "protobuf", "fastapi[standard]")
          .pip_install("git+https://github.com/huggingface/transformers.git")
          .add_local_file(__file__.replace("glimmer_chat_web.py", "glimmer_chat.html"), "/app/chat.html"))
app = modal.App("glimmer-chat", image=imagen)
vol = modal.Volume.from_name("muse-glimmer-30b")


def _limpiar(texto: str) -> str:
    # Glimmer a veces escribe su razonamiento y luego «assistant to=user…»: nos quedamos con lo último.
    for marca in ("assistant to=user", "to=user"):
        if marca in texto:
            texto = texto.rsplit(marca, 1)[1]
            break
    return texto.strip()


@app.cls(gpu="A100-80GB", volumes={"/m": vol}, secrets=[modal.Secret.from_name("glimmer-chat")],
         scaledown_window=300, timeout=900, max_containers=1, min_containers=0)   # 3 nov: de 600 a 300 s; una A100 ociosa cuesta lo mismo que trabajando
class Glimmer:
    @modal.enter()
    def cargar(self):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor
        ruta = "/m/Muse-Glimmer-30B"
        self.proc = AutoProcessor.from_pretrained(ruta)
        self.modelo = AutoModelForImageTextToText.from_pretrained(ruta, torch_dtype=torch.bfloat16, device_map="cuda")

    @modal.asgi_app()
    def web(self):
        from fastapi import FastAPI, Header, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from PIL import Image

        api = FastAPI()
        api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

        @api.get("/")
        def pagina():
            from fastapi.responses import HTMLResponse
            return HTMLResponse(open("/app/chat.html", encoding="utf-8").read())

        @api.get("/estado")
        def estado():
            return {"ok": True}

        @api.post("/chat")
        def chat(cuerpo: dict, x_clave: str = Header(default="")):
            if x_clave != os.environ["CLAVE"]:
                raise HTTPException(401, "clave incorrecta")
            mensajes, imagenes = [], []
            for m in cuerpo.get("mensajes", [])[-12:]:
                contenido = []
                for f in m.get("fotos", []):
                    im = Image.open(io.BytesIO(base64.b64decode(f))).convert("RGB")
                    imagenes.append(im)
                    contenido.append({"type": "image", "image": im})
                contenido.append({"type": "text", "text": m["texto"]})
                mensajes.append({"role": "user" if m["rol"] == "user" else "assistant", "content": contenido})
            texto = self.proc.apply_chat_template(mensajes, add_generation_prompt=True, tokenize=False)
            if cuerpo.get("directo", True):
                texto += " to=user"  # salta el razonamiento interno (canal to=self) y contesta directo
            entrada = self.proc(text=texto, images=imagenes or None, return_tensors="pt").to("cuda")
            tokens = max(64, min(int(cuerpo.get("tokens", 1500)), 6000))
            salida = self.modelo.generate(**entrada, max_new_tokens=tokens, do_sample=False)
            crudo = self.proc.decode(salida[0][entrada["input_ids"].shape[1]:], skip_special_tokens=True)
            return {"respuesta": _limpiar(crudo), "crudo": crudo}

        return api
