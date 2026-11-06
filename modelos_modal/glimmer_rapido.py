"""Glimmer RÁPIDO, desplegado y caliente, para calificar desde el tablero en segundos.

Por qué existe (4 nov 2026, pedido de Carlos): la fila de `glimmer_evaluador` tarda 6-10 min porque
carga los 30B cada vez. Aquí el modelo se queda cargado (`@modal.enter()`) y el contenedor sigue
caliente 4 min después de la última pregunta, así que la segunda calificación sale en segundos.
El tablero lo llama directo con `modal.Cls.from_name` (misma cuenta, sin claves).

  MODAL_PROFILE=charlyfavela666 MODAL_IMAGE_BUILDER_VERSION=2025.06 modal deploy modelos_modal/glimmer_rapido.py
  Apagar:  modal app stop glimmer-rapido
Ojo: una A100 ociosa cuesta igual que trabajando (~$4/h); por eso 4 min de ventana y no más.
"""
import io
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "accelerate", "pillow", "sentencepiece", "protobuf")
          .pip_install("git+https://github.com/huggingface/transformers.git"))
app = modal.App("glimmer-rapido", image=imagen)
# imagen ligera solo para la página web (sin torch): arranca en segundos
imagen_web = modal.Image.debian_slim(python_version="3.12").pip_install("fastapi[standard]")
vol = modal.Volume.from_name("muse-glimmer-30b")


PLAN = """Eres la IA de calidad de anuncios de Meta (Facebook/Instagram) para negocios en México.
Da SOLO la respuesta final, en español claro para el dueño del negocio, sin mostrar tu razonamiento.
Las imágenes son el anuncio que se quiere subir (o sus cuadros, en orden). No inventes precios, datos ni resultados:
si falta algo escribe [FALTA: ...].

NEGOCIO Y CONTEXTO: {contexto}

Responde EXACTAMENTE con este formato:

CALIFICACION: X/10
PROYECTADA: X/10
POR RUBRO (nota y una línea de por qué):
- Oferta:
- Confianza:
- Claridad del mensaje:
- Calidad visual:
- Políticas de Meta:
- Probabilidad de mensajes baratos:
- Probabilidad de mensajes calificados:
POR QUÉ FUNCIONA (lo que SÍ está jalando, 3 viñetas)
QUÉ LO FRENA (máximo 3 viñetas; cada una con el arreglo exacto y cuánto sube la nota)
PLAN PARA LLEGAR A 9-10 (pasos concretos, en orden, con lo que hacemos nosotros y lo que debe mandar el cliente)
CÓMO SE LO EXPLICO AL CLIENTE (4 a 6 renglones, tuteando de usted, para mandárselo tal cual por WhatsApp)
VEREDICTO: (subir ya / subir con cambios / no subir)"""


@app.cls(gpu="A100-80GB", volumes={"/m": vol}, timeout=1800, scaledown_window=240, max_containers=1,
         secrets=[modal.Secret.from_name("tablero-clave")])
class Rapido:
    @modal.enter()
    def cargar(self):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor
        ruta = "/m/Muse-Glimmer-30B"
        self.proc = AutoProcessor.from_pretrained(ruta)
        self.modelo = AutoModelForImageTextToText.from_pretrained(ruta, torch_dtype=torch.bfloat16, device_map="cuda")
        print("Glimmer rápido listo", flush=True)

    @modal.method()
    def calificar(self, prompt: str, fotos: list, tokens: int = 1200) -> str:
        """`fotos` son bytes de imagen. Devuelve solo la respuesta (canal directo, sin razonamiento)."""
        from PIL import Image
        ims = [Image.open(io.BytesIO(b)).convert("RGB") for b in fotos]
        contenido = [{"type": "image", "image": im} for im in ims]
        contenido.append({"type": "text", "text": prompt})
        texto = self.proc.apply_chat_template([{"role": "user", "content": contenido}],
                                              add_generation_prompt=True, tokenize=False) + " to=user"
        entrada = self.proc(text=texto, images=ims or None, return_tensors="pt").to("cuda")
        salida = self.modelo.generate(**entrada, max_new_tokens=tokens, do_sample=False)
        r = self.proc.decode(salida[0][entrada["input_ids"].shape[1]:], skip_special_tokens=True)
        for marca in ("assistant to=user", "to=user"):
            if marca in r:
                r = r.rsplit(marca, 1)[1]
                break
        return r.strip()


# ---- Página y API (4 nov 2026, pedido de Carlos) -------------------------
# Carlos quería «Glimmer súper rápido en una URL de Modal que nos dé plan de calidad»:
# se sube la imagen del anuncio (o varias) y contesta calificación por rubro, por qué
# funciona, qué lo frena, el plan para llegar a 9-10 y el texto para explicárselo al cliente.
# La clave es la misma del tablero (secreto `tablero-clave`), para no crear otra.
# La página corre en CPU: abre al instante y la A100 solo se prende al calificar.
@app.function(image=imagen_web, secrets=[modal.Secret.from_name("tablero-clave")], timeout=1800)
@modal.asgi_app()
def web():
    import base64 as b64
    import os
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse

    CLAVE = os.environ.get("TABLERO_CLAVE", "")
    api = FastAPI()

    def _guard(req, x_clave):
        if CLAVE and (req.query_params.get("k") or x_clave) != CLAVE:
            raise HTTPException(401, "clave incorrecta")

    @api.get("/", response_class=HTMLResponse)
    def pagina(req: Request):
        _guard(req, "")
        return HTMLResponse(PAGINA)

    @api.get("/estado")
    def estado():
        return {"ok": True}

    @api.post("/calificar")
    async def calificar(req: Request, x_clave: str = Header(default="")):
        _guard(req, x_clave)
        c = await req.json()
        fotos = [b64.b64decode(f.split(",")[-1]) for f in (c.get("fotos") or [])][:10]
        if not fotos:
            return JSONResponse({"ok": False, "error": "manda al menos una imagen"}, 400)
        prompt = PLAN.format(contexto=(c.get("contexto") or "[FALTA: datos del negocio]")[:1500])
        return JSONResponse({"ok": True, "texto": Rapido().calificar.remote(prompt, fotos, int(c.get("tokens", 1100)))})

    return api


PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Glimmer rápido</title><style>
:root{--bg:#faf9f7;--panel:#fff;--fg:#1a1a1a;--mut:#6b6b6b;--lin:#e2ddd5;--ok:#1f7a4d}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#17181a;--panel:#1f2023;--fg:#ececec;--mut:#9a9a9a;--lin:#32343a;--ok:#4ec98a;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
.w{max-width:760px;margin:0 auto;padding:22px 16px 48px}
h1{font-size:20px;margin:0 0 4px}p.s{color:var(--mut);font-size:13.5px;margin:0 0 18px}
.p{background:var(--panel);border:1px solid var(--lin);border-radius:12px;padding:15px;margin-bottom:14px}
textarea,input[type=file]{font:inherit;width:100%;border:1px solid var(--lin);border-radius:9px;background:var(--bg);color:var(--fg);padding:9px 11px}
textarea{min-height:76px;resize:vertical}
button{font:inherit;font-weight:600;padding:9px 16px;border-radius:9px;border:1px solid var(--ok);background:transparent;color:var(--ok);cursor:pointer;margin-top:10px}
button:disabled{opacity:.5;cursor:default}
pre{white-space:pre-wrap;font:13.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;background:color-mix(in srgb,var(--fg) 6%,transparent);border-radius:9px;padding:12px;overflow-wrap:anywhere}
.min{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}.min img{height:74px;border-radius:7px}
</style></head><body><div class="w">
<h1>Glimmer rápido</h1>
<p class="s">Sube la imagen del anuncio (o varios cuadros de un video) y te dice en qué califica, por qué funciona, qué lo frena y el plan para llegar a 9-10. La primera consulta tarda ~2 min porque carga el modelo; las siguientes salen en segundos.</p>
<div class="p">
  <label>Imágenes del anuncio</label>
  <input id="fs" type="file" accept="image/*" multiple>
  <div class="min" id="min"></div>
</div>
<div class="p">
  <label>De qué negocio es y qué vende (datos reales)</label>
  <textarea id="ctx" placeholder="Ej.: Villa en renta en San Carlos, Sonora. Vendemos videos y estrategia por $500 al mes, la pauta va aparte. El anuncio busca mensajes por WhatsApp de dueños de villas."></textarea>
  <button id="go" type="button">Calificar</button>
</div>
<div class="p"><pre id="out">Aquí sale el plan de calidad.</pre></div>
</div><script>
(function(){
var K=new URLSearchParams(location.search).get('k')||'';
var fotos=[];
document.getElementById('fs').onchange=function(e){
  fotos=[];var m=document.getElementById('min');m.textContent='';
  Array.prototype.slice.call(e.target.files).slice(0,10).forEach(function(f){
    var r=new FileReader();
    r.onload=function(){fotos.push(r.result);var i=new Image();i.src=r.result;m.appendChild(i);};
    r.readAsDataURL(f);});
};
document.getElementById('go').onclick=function(){
  var b=this,o=document.getElementById('out');
  if(!fotos.length){o.textContent='Primero sube una imagen.';return;}
  b.disabled=true;o.textContent='Glimmer está viendo el anuncio…';
  fetch('/calificar?k='+encodeURIComponent(K),{method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({fotos:fotos,contexto:document.getElementById('ctx').value})})
   .then(function(r){return r.json();})
   .then(function(j){o.textContent=j.ok?j.texto:('No se pudo: '+(j.error||'error'));b.disabled=false;})
   .catch(function(e){o.textContent='No se pudo: '+e.message;b.disabled=false;});
};
})();
</script></body></html>"""
