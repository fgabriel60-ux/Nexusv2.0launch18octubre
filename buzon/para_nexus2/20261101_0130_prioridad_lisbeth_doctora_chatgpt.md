# Encargo prioritario para ChatGPT (Modal) · Lisbeth y doctora · 1 nov 2026

Carlos pidió que lo hagas tú, en orden, para subir a campaña rápido. Cola nueva: `entregables/cola_prioridad/` (ver su LEEME.md).

## 1. Lisbeth (prioridad alta): de 6/10 a 8
- Base: `clientes/Lisbeth/video/v9/armar_lisbeth_v9.py` y `clientes/Lisbeth/video/Lisbeth_v9_terreno_real.mp4`.
- Cambios que pidió Carlos: quitar el aéreo de 0 a 4.5 s (abrir directo con el terreno); cierre con voz Fish: «Si buscas terreno desde 300 m² en Tomatlán, escríbeme por WhatsApp» y ese texto también en capa; recortar a 35 s o menos.
- Voz: Fish, cliente de Lisbeth (ver `clientes/Lisbeth/whatsapp` y memoria de voces). Genera 4 tomas, elige la que Whisper medium transcriba igual.
- Entrega: `clientes/Lisbeth/video/v10/Lisbeth_v10.mp4` (H.264 Main 720p, <16 MB). No borres v9; versiona.
- Dato que falta: plano y precios (no aparecieron en la ronda). Usa solo lo que está en su chat; si no hay precio, no lo pongas en el video.
- Calificación Glimmer: separa actual y proyectada, sin inventar.

## 2. Doctora Ángeles (Veneers Dental, Alberto): de 6.5 a más
- Última versión: `clientes/Alberto/video/Veneers_Dra_Angeles_implantes_estilo_ref_v6c.mp4` (6.5, «pendiente mejorar»).
- Motivo de la calificación: `clientes/Alberto/glimmer_101010_20261027/glimmer.log` (lee lo que la frustra).
- Precios reales (30 oct, `clientes/Alberto/precios_20261030.txt`): brackets $3,000; tomografía $1,500; placas acrílicas $5,000; carillas de zirconia $7,000. Úsalos tal cual, no inventes otros.
- Armador: `clientes/Alberto/video/armar_implantes_ref.py --version v7 --tomas v6` (revisa antes el parámetro `--tomas`).
- Entrega: v7 en la misma carpeta, con Glimmer actual y proyectada.

## Reglas
- Nada a clientes: todo va a Carlos (`44522318905388@lid`). Alberto y Lisbeth no reciben nada sin que Carlos lo pida en ese mensaje.
- GPU: antes de lanzar, manda a Carlos la estimación (tiempo y costo). Lo de ffmpeg y voz Fish no pide permiso.
- Anota «Lisbeth/Alberto · nexus2 · hora» en `buzon/tomados.md` antes de tomar cada uno.
- Al terminar: rutas de los videos, calificaciones actual/proyectada y qué falta. En español.
