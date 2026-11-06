"""Glimmer: semana de publicaciones orgánicas para Anegocios (Fernando hace 3 por semana)."""
import json
from pathlib import Path
AQUI = Path(__file__).resolve().parent
prompt = """Eres estratega de contenido orgánico de Facebook e Instagram para negocios en México. Da SOLO la respuesta final, en español, sin mostrar tu razonamiento.

CLIENTE: Fernando, dueño de ANEGOCIOS (punto de venta en la nube; facebook.com/anegociosmx). Hoy hace 3 publicaciones orgánicas por semana él mismo y pidió «¿qué propones?».
Oferta real: $3,500 MXN más impuestos = 1 año de software + impresora térmica + lector de códigos de barras + instalación en tu negocio + capacitación personal + soporte. «Primero lo tienes funcionando, después pagas.» Requisito: que el negocio ya tenga computadora. Instalación solo en CDMX y Área Metropolitana (dice su flyer).
Funciones reales: ventas y cobros al momento, inventario actualizado, cortes de caja claros, catálogo digital, app Android para rutas de venta, reportes, consulta desde el celular, cuenta demostrativa y demo por videollamada. Caso real que cuenta: una señora con nevería que no sabía controlar inventario porque cada bola lleva distintos gramos; él le explicó que se controla por vasos y gramos y se lo mostró funcionando en la computadora.
Cliente ideal: tiendas, misceláneas, abarrotes, neverías, papelerías, negocios que llevan ventas en libreta o Excel, y negocios con rutas de venta.
Imagen adjunta: su material real (fotos de Fernando en distintos lugares, la impresora térmica HOIN con ticket, el lector de códigos, rollos de papel, pantalla del sistema, sus flyers con logo Anegocios en azul).
Videos que ya tiene: v6 (capacitación con su voz, gancho de la nevería) y viene una v7 «Los 4 pasos para controlar tu negocio sin libreta».

TAREA: arma la SEMANA DE CONTENIDO (lunes, miércoles y viernes = 3 publicaciones de feed, más 2 historias de apoyo martes y jueves), pensada para que el contenido orgánico genere confianza y mensajes por WhatsApp (no solo likes). Mezcla: educar (un consejo útil que el dueño de tienda aplica hoy), prueba/confianza (Fernando real, instalación, el kit) y oferta clara.
Para CADA publicación entrega:
1) Día y objetivo.
2) Formato (imagen única 4:5, carrusel de N láminas, o reel corto) y por qué.
3) Texto EXACTO de cada imagen/lámina (titular corto ≤ 7 palabras + línea secundaria ≤ 12 palabras), indicando qué foto real de su material va de fondo o qué elemento (impresora, lector, pantalla del sistema, foto de Fernando).
4) Copy completo del post (caption) listo para pegar, natural, con 1 pregunta que invite a comentar o escribir, y CTA a WhatsApp. 3-5 hashtags locales útiles.
5) Mejor hora para publicar.
Para las 2 historias: texto exacto y el sticker/encuesta a usar.
Al final: 3 reglas para responder comentarios y mensajes que conviertan, y qué NO publicar (sin inventar precios, clientes, cifras ni testimonios).
Califica honestamente la semana (1-10) en confianza, claridad de oferta y probabilidad de mensajes."""
(AQUI / 'prompt.txt').write_text(prompt)
(AQUI / 'lote.json').write_text(json.dumps([{'nombre': 'semana_anegocios', 'prompt': prompt, 'fotos': [str(AQUI / 'material.jpg')]}], ensure_ascii=False))
