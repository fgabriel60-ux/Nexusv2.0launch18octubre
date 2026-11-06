"""Enlace público TEMPORAL solo con los videos de anuncio de Víctor (Servilin) y sus miniaturas, para que Meta los descargue.
Uso: modal deploy servir_anuncios_modal.py  ·  apagar después: modal app stop victor-anuncios"""
import pathlib
import modal

AQUI = pathlib.Path(__file__).resolve().parent
imagen = modal.Image.debian_slim().pip_install("fastapi[standard]")
for f in sorted(AQUI.glob("Servilin_*")):
    imagen = imagen.add_local_file(f, f"/anuncios/{f.name}")
app = modal.App("victor-anuncios", image=imagen)


@app.function()
@modal.asgi_app()
def web():
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    api = FastAPI()
    api.mount("/a", StaticFiles(directory="/anuncios"), name="a")
    return api
