# Video de Alberto en Kling, 7 tramos de 5 s — reja de cuadros llave

35 s = 7 tramos de 5 s. Kling `image-to-video` va de `image` a `end_image`, así que
hacen falta **8 cuadros llave**, en los segundos 0, 5, 10, 15, 20, 25, 30 y 35.

Los marcadores de la voz (`voz_fish/tiempos.json`, 30 fps) NO caen en múltiplos de 5.
Esta es la asignación, con el desfase real de cada uno:

| s | cuadro Blender | imagen | de dónde sale | desfase |
|---|---|---|---|---|
| 0  | 1    | `01_rostro_hueco.png`      | ya existe (marcador ROSTRO, cuadro 1)      | **exacto** |
| 5  | 150  | `02_closeup_espacio.png`   | ya existe (CLOSEUP, cuadro 150)            | **exacto** |
| 10 | 300  | `R10_anestesia_sale.png`   | **NUEVO**                                   | el más cercano era 03 a 6.67 s → 3.3 s |
| 15 | 450  | `R15_fresa_dentro.png`     | **NUEVO**                                   | el más cercano era 05 a 14.0 s → 1.0 s |
| 20 | 600  | `06_implante_entra.png`    | ya existe (IMPLANTE, cuadro 620)           | 0.67 s |
| 25 | 750  | `07_integracion.png`       | ya existe (INTEGRACION, cuadro 740)        | 0.33 s |
| 30 | 900  | `09_corona_colocada.png`   | ya existe (~cuadro 950)                    | 1.7 s, pero la toma está detenida |
| 35 | 1050 | `10_sonrisa_feliz.png`     | ya existe (SONRISA + morph final)          | **exacto** |

## Por qué solo dos nuevos

- **10 s**: en 6.75 s entra la jeringa y en 12.09 s se despega el rostro. A los 10 s la
  jeringa ya salió y la cara sigue entera — no hay ningún cuadro de ese estado. Si se usa
  el 03 (jeringa puesta) el tramo 3 arranca 3 s atrasado; si se usa el 04 (rostro despegado)
  arranca 2 s adelantado y se pierde el despegue, que es el momento difícil.
- **15 s**: la fresa está en movimiento entre 14.09 y 20.75 s. Un segundo de desfase en una
  fresa que avanza sí se nota.
- **20, 25 y 30 s**: las tomas están prácticamente detenidas ahí (tornillo entrando,
  integración, corona puesta), así que medio segundo o segundo y medio no cambia el cuadro.

## Los 7 tramos

| # | de → a | qué pasa | beat de voz |
|---|---|---|---|
| 1 | 0 → 5 s   | rostro con el hueco, la cámara entra al macro | "¿Te falta un diente?…" |
| 2 | 5 → 10 s  | entra la jeringa, anestesia, se retira        | "Este es el espacio." / "Primero, anestesia local…" |
| 3 | 10 → 15 s | **el rostro se despega como sticker** y revela el maxilar; entra la fresa | "Ahora, veamos por dentro." |
| 4 | 15 → 20 s | la fresa termina el canal y se retira, el tornillo empieza a entrar | "El dentista prepara el hueso…" |
| 5 | 20 → 25 s | el tornillo de titanio se atornilla hasta el fondo; empieza la integración | "Coloca un tornillo de titanio…" |
| 6 | 25 → 30 s | el hueso crece alrededor, se pone el pilar y sube la corona | "Con los meses, el hueso crece…" |
| 7 | 30 → 35 s | corona puesta, la cámara se retira y la cara hace morph a la sonrisa feliz | "Encima va el pilar…" / "Y vuelves a sonreír." |

El tramo 3 es el mismo que ya probaste el 17 sep (`kling_por_pedazos_20260917`) y salió bien,
así que ese pedazo ya está validado.

## Costo

La prueba del 03→04 costó **$0.35 reales** (saldo 4.47 → 4.12). Siete tramos ≈ **$2.45**.
Los dos cuadros nuevos de GPT Image 2 son centavos. Saldo al 17 sep: **$18.12**.
