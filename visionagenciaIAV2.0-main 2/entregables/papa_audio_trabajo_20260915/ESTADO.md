# Pedidos de papá (Gabriel) — 15 y 16 septiembre 2026

## 1. Audio del cliente: mueble color madera (15 sep)

Papá reenvió un audio de 21 s de quien pide el trabajo. Transcrito con faster-whisper en `transcripcion.txt`:

> «…dile que me gusta un diseño como de madera, que sean de color madera… con una cajonera y un comedorcito ahí o algo
> así… cuando la tenga te mando una foto para ver el diseño… dile que la haga color madera.»

Justo después mandó el número de **Marco Antonio Ortiz: 631 123 1961**, probablemente el cliente.

Se hicieron dos propuestas con GPT Image 2 y se le mandaron a él y a Carlos:

- `PROPUESTA_1_cocina_cajonera_comedorcito.png`: cocina color madera con columna de cajones y comedorcito integrado.
- `PROPUESTA_2_cajonera_y_comedor.png`: cajonera de 5 cajones y comedor de 4 sillas, mismo tono.

Script: `diseno_madera.py`. **Falta** la foto del diseño que el cliente iba a mandar; con ella se puede ajustar.

## 2. Charros revolucionarios (16 sep)

Papá mandó una foto suya con el joven y pidió: «Sácala vestidos de charros revolucionarios ☺️».

Se editó la foto con GPT Image 2 cuidando que siguieran siendo ellos: mismas caras, misma pose, misma diferencia de
estatura y mismo encuadre; solo cambia la ropa. Dos versiones, mandadas a él y a Carlos:

- `CHARROS_v1_gala.png`: charros de gala, sombrero bordado, moño rojo y botonadura plateada, en la misma sala.
- `CHARROS_v2_revolucionarios.png`: revolucionarios de 1910, bandoleras cruzadas, paliacate y luz sepia.

Script: `charros_revolucionarios.py`. Foto original: `FOTO_PAPA_CHARROS.jpg`. Recibos en `recibo_charros.json`.
