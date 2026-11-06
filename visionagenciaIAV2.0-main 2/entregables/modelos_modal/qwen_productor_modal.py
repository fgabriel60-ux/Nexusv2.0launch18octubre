"""Productor de videos: Qwen3-VL-30B-A3B en Modal mira las fotos y videos del prospecto y escribe el plan del video en JSON
(guion por frases, qué toma va en cada frase, textos en pantalla, tarjeta). Lo produce clientes/_productor/producir.py.
Una vez: modal deploy qwen_productor_modal.py  ·  prueba: modal run qwen_productor_modal.py --prompt "hola" """
import io
import modal

MODELO = "Qwen/Qwen3-VL-30B-A3B-Instruct"   # BF16: la versión FP8 exige núcleos DeepGEMM que fallan en Modal
imagen = (modal.Image.from_registry("nvidia/cuda:12.9.1-devel-ubuntu22.04", add_python="3.12")   # vLLM compila núcleos con nvcc
          .pip_install("vllm==0.30.0", "pillow")
          .env({"HF_HOME": "/m/hf", "VLLM_USE_DEEP_GEMM": "0"}))
app = modal.App("qwen-productor", image=imagen)
vol = modal.Volume.from_name("qwen3-vl-30b", create_if_missing=True)


@app.cls(gpu="H100", volumes={"/m": vol}, timeout=1800, scaledown_window=300)
class Productor:
    @modal.enter()
    def cargar(self):
        from huggingface_hub import snapshot_download
        from vllm import LLM
        ruta = snapshot_download(MODELO)
        vol.commit()
        self.llm = LLM(ruta, max_model_len=16384, limit_mm_per_prompt={"image": 24, "video": 0}, gpu_memory_utilization=0.9)

    @modal.method()
    def planear(self, trabajos: list) -> list:
        """trabajos: [{"prompt": str, "imagenes": [bytes jpg]}] → un texto (JSON) por trabajo, todos en un solo lote."""
        import base64
        from vllm import SamplingParams
        conversaciones = []
        for t in trabajos:
            contenido = [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b).decode()}} for b in t["imagenes"]]
            contenido.append({"type": "text", "text": t["prompt"]})
            conversaciones.append([{"role": "user", "content": contenido}])
        salidas = self.llm.chat(conversaciones, SamplingParams(temperature=0.4, top_p=0.9, max_tokens=3000))
        return [s.outputs[0].text for s in salidas]


@app.local_entrypoint()
def main(prompt: str):
    print(Productor().planear.remote([{"prompt": prompt, "imagenes": []}])[0])
