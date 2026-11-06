# Revisión del repo higgsfield-genjutsu-unlimited (17 sep 2026)

Repo: https://github.com/SabauAlexandru-py/higgsfield-genjutsu-unlimited
Clonado y leído completo (README, docs/PRD.md, backend/creator.py, backend/temp_mail.py,
backend/proxy_manager.py). Esto es lo que hace, palabra por palabra de su propio README.

## Qué hace realmente

> "Unlimited free Higgsfield Genjutsu videos by **auto-creating a fresh verified account
> for every generation** (each new account gets 1 free credit)."

El flujo del backend, por cada video que pides:

1. `temp_mail.py` abre un buzón desechable en 1secmail.
2. `creator.py` levanta un Chromium con **undetected-playwright** (navegador parchado para
   que higgsfield.ai no detecte que es un robot).
3. Se registra en higgsfield.ai con ese correo, espera el correo de verificación, abre la
   liga y verifica la cuenta.
4. Entra a Genjutsu, sube la referencia, escribe el prompt, genera y descarga el mp4.
5. `proxy_manager.py` rota proxies SOCKS5 para que no se vea que todo sale de la misma IP.

O sea: no es un cliente de la API de Higgsfield ni un truco de precios. Es **crear cuentas
falsas en serie, con evasión de detección y rotación de IP, para no pagar los créditos**.

## Por qué no lo voy a montar

Eso es fraude de servicio contra Higgsfield: suplantación de usuarios, evasión de los
controles de acceso de un tercero y uso de infraestructura ajena sin pagar. No lo instalo
ni lo despliego, y tampoco te lo dejo armado para correrlo.

Aparte del punto legal, hay riesgo directo para el negocio: si Higgsfield liga esas altas
a tu IP, tu tarjeta o tu cuenta real, te tumban la cuenta buena — con la que ya tienes
trabajo de Catania y del implante adentro.

## Lo que SÍ resuelve el video de Alberto

Ya tienes probado en el repo qué reemplaza a Genjutsu — ver
`entregables/implante_dental/genjutsu_20260915/ALTERNATIVAS_A_GENJUTSU.md`, con las tres
pruebas corridas con el tramo A real, no con ejemplos:

| Opción | Costo real medido | Tiempo | ¿Hace el corte anatómico + sticker? |
|---|---|---|---|
| `minimax-h3/video-edit` | ~$2.85 / 15 s | 21 min | **Sí** — el único que lo logró |
| `ltx-2-19b/control` (depth) | $0.54 / 18 s | 2.5 min | No (solo acepta 1 referencia) |
| `lucy-restyle` | $0.01 | 100 seg | No, y además rompe el tiempo |

**MiniMax es el reemplazo real de Genjutsu.** Los 35 s del implante salen en 3 pedazos.
Costo estimado a precio real medido: **$8 a $9 dólares**, no los $0.75 del precio de lista
(WaveSpeed cobra 11x lista en ese modelo — está documentado en el mismo archivo).

Pendientes conocidos antes de lanzarlo:
- Reforzar el negativo para la sangre que escurrió en el tramo final de la prueba.
- Saldo de WaveSpeed: estaba en $4.47 tras la prueba LTX. **No alcanza para los 3 pedazos.**

## Las tres salidas que sí hay

1. **Genjutsu con tu cuenta.** Es lento, pero es el que da la calidad que aprobaste. Si el
   problema es solo la espera, se manda el tramo y se recoge después.
2. **MiniMax en WaveSpeed, 3 pedazos.** Hay que recargar saldo primero (~$10 para tener
   colchón). Es la ruta ya probada.
3. **Seguir con Kling por pedazos**, que es en lo que ibas el 17 sep
   (`kling_por_pedazos_20260917/PRUEBA_KLING_03_A_04.mp4`).

Dime cuál y lo dejo corriendo.
