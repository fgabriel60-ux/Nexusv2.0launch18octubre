"""Enlace público TEMPORAL con los videos de anuncio de Jesús · RIMO y sus miniaturas, para que Meta los descargue.
Uso: modal deploy servir_anuncios_modal.py  ·  apagar después: modal app stop rimo-anuncios"""
import pathlib
import modal

AQUI = pathlib.Path(__file__).resolve().parent
imagen = modal.Image.debian_slim().pip_install("fastapi[standard]")
for f in sorted(AQUI.glob("RIMO_*")):
    imagen = imagen.add_local_file(f, f"/anuncios/{f.name}")
app = modal.App("rimo-anuncios", image=imagen)


@app.function()
@modal.asgi_app()
def web():
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    api = FastAPI()
    api.mount("/a", StaticFiles(directory="/anuncios"), name="a")
    return api
