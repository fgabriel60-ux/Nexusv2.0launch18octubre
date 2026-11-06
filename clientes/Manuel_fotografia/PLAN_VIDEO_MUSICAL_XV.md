# XV Manuel — plan como video musical (con la música de «GIO XV»)

Maqueta: `clientes/XV/final/XV_reel_v6_musica_referencia.mp4` = v6 (26 s) con la canción de la referencia desde el s 30.2 (la subida y el drop). Solo para ver el ritmo: esa canción es comercial, para pautar se usa una con licencia de ~120-125 BPM.

## La música manda
- ~123 BPM → 1 golpe = 0.49 s, 1 compás = 1.95 s.
- Estructura de la referencia: intro suave 0-36 s · DROP 1 36-50 s · respiro 50-61 s · DROP 2 62-86 s · cierre 86-95 s.
- La referencia corta: cada 2 compases (~4 s) en la intro, cada golpe (0.5 s) en los drops, planos de 2-4 s en el respiro. Tiene 82 cortes en 95 s.
- Lo que falla en nuestro v6: los cortes no caen en el golpe, todo va a la misma velocidad (no hay intro → drop → respiro) y faltan apertura, preparación y detalles. El cierre de 3 s con texto corta la música.
- v7 (siluetas, piso LED, láser) se ve como antro y no como su salón (cálido, con candiles). No casa con el material real.

## Guion de 30 s sobre la música (s 30 → 60 de la canción)
| Video | Música | Escena | Origen |
|---|---|---|---|
| 0-2 s | subida | Vista aérea nocturna del salón iluminado, acercándose | IA (Qwen + H3) desde foto del salón |
| 2-4 s | subida | Vestido verde colgado en ventana con luz cálida + tiara (macro) | IA desde foto del vestido |
| 4-6 s | pre-drop | Entrada a contraluz con humo en la puerta del salón, cámara lenta (silueta, sin cara) | IA |
| 6 s | **DROP** | Corte seco al giro del vestido verde en la pista | real |
| 6-14 s | drop, 1 corte por golpe | Pista, amigas, brazos arriba, confeti, robot LED, papá bailando | real (lo que ya hay en v6) |
| 14-20 s | respiro, planos de 2 s | Retrato con humo y contraluz; abrazo con mamá; detalle de manos y ramo | real + IA para el humo/contraluz |
| 20-27 s | drop 2 | Hora loca: CO2, robot LED, confeti, giro final en cámara lenta en el último golpe | real + IA (giro con confeti) |
| 27-30 s | cierre | Alejamiento del salón de noche → logo «Manuel Fotografía · Agenda tu fecha» SIN cortar la música | IA + texto |

## Escenas a generar en Modal (mejorando lo que tenemos)
Todas desde fotos reales de esta fiesta (salón, vestido verde, pista, robot) para que se vea el mismo evento; sin caras inventadas (siluetas, espalda, detalle).
1. Aérea nocturna del salón con luces cálidas, acercamiento lento.
2. Vestido verde colgado junto a la ventana, polvo en el aire, luz dorada.
3. Macro: tiara y collar con destellos.
4. Silueta a contraluz entrando por la puerta del salón con humo.
5. Giro del vestido verde en cámara lenta con confeti dorado sobre la pista real.
6. Retrato de espalda con humo y luz de escenario rosa/azul.
7. Robot LED entre CO2 sobre la pista real.
8. Alejamiento final del salón (para el logo).

## Edición
- Cortar al golpe (0.49 s) en los drops; en el respiro, 2 compases por plano.
- Color cálido de cine (magenta/azul de escenario), grano suave.
- Sin textos encima salvo el cierre.
- Sonidos reales (risas, gritos de la pista) por debajo de la música.
