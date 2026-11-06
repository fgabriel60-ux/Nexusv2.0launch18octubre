Eres el ayudante de Claude en el workspace de Carlos. Lee AGENTS.md y entregables/ronda_8_9_20261031/plan.md. Haz la FASE A completa (A1 a A5), escribiendo los archivos en entregables/ronda_8_9_20261031/.

Reglas: NO escribas ni mandes nada a clientes ni prospectos. NO mandes nada a Carlos por WhatsApp (Claude lo hará). Solo lectura de WhatsApp (fetch-messages / download-media) y escribir archivos en esa carpeta. No borres nada. No lances GPU salvo la fila de Glimmer de A2.

A1: busca en clientes/<Cliente>/ (y entregables/) los .mp4 más recientes de cada cliente de la tabla del plan (incluye prospectos con video). Usa fecha de modificación y número de versión; descarta tmp/, cuadros, escenas sueltas. Cruza con las calificaciones de entregables/glimmer_evaluador/*/glimmer.log (lo que sigue a «assistant to=user»). Escribe inventario.md: cliente | ruta absoluta | versión | última calificación | fecha.

A2: con los videos de A1 arma entregables/glimmer_evaluador/anuncios_ronda1_20261031.json (campo "cliente" con datos reales del negocio, sácalos del tablero entregables/ruta_clientes_20261030/ruta.html y de /vol/claude-config/codex/contexto_carlos.md). Encólalo en entregables/fila/pendientes/20261031_0700_ronda1.sh con el formato de AGENTS.md y salida entregables/glimmer_evaluador/ronda1_20261031. Si son más de 8 videos, haz dos lotes (ronda1a, ronda1b).

A3: prospectos_referencias.md — tabla: prospecto | teléfono/chatId | giro | ¿mandó reel de Instagram? (link exacto) | ¿mandó fotos/audio? Separa «con referencia» y «sin referencia (Carlos les busca)». Revisa también los mensajes de los últimos 3 días en el chat de Carlos (44522318905388@lid, limit 150): ahí Carlos reenvía referencias.

A4: pedidos_clientes.md — por cliente, lo que falta pedirle (datos, fotos, audios, precios, WhatsApp de cierre) en un mensaje corto de WhatsApp listo para que Carlos lo apruebe.

A5: datos_encargo.md — busca en el chat de Carlos y en los chats de cada cliente (últimos 150 mensajes) y descarga a entregables/ronda_8_9_20261031/media/<cliente>/ la media relevante: lo nuevo que pidió Jesús Puertas; la referencia que Carlos le mandó a Ignacio (y fotos de su carro); referencias y nombres del prospecto de carros BYD; guion y audio de Fernando; planos y precios de Lisbeth; la v7 de Víctor y qué hay que corregirle; el audio/referencia de Guillermo para su video; el otro servicio de BD Pro; referencias de Israel, Mariano (Spiderman), Verónica, Tatuador (hard cut), Rachel, Blanca. Para cada uno: qué es, ruta descargada, mensaje original citado.

Al final escribe LISTO.md con un resumen de 10 líneas y cualquier cosa que no encontraste.
