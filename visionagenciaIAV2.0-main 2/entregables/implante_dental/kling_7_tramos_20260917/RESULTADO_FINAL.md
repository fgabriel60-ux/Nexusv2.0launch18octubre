# Video del implante de Alberto — resultado del 17 sep 2026

`IMPLANTE_ALBERTO_FINAL_35s.mp4` · 1080×1920 · 30 fps · 35.000 s exactos
Versión ligera para WhatsApp: `IMPLANTE_ALBERTO_FINAL_35s_WHATSAPP.mp4` (720×1280, 8.3 MB)

Voz: `voz_adictiva_20260917/FINAL_AGENDA_35s.mp3` (Narrador v2, cierre "Agenda tu valoración
en Veneers Dental").

## De dónde salió cada tramo

Ningún modelo sirvió para todo. Cada tramo quedó con el que resolvió *su* problema.

| tramo | s | modelo | costo | qué pasa |
|---|---|---|---|---|
| 1 | 0–5   | Kling 2.6 pro, cuadros llave | $0.35 | rostro con el hueco, la cámara entra al macro |
| 2 | 5–10  | Kling 2.6 pro, cuadros llave | $0.35 | la jeringa entra, anestesia y se retira |
| 3 | 10–15 | **Seedance 2.0 fast 1080p**  | $2.50 | el rostro se despega como calcomanía y entra la fresa |
| 4 | 15–20 | Kling 2.6 pro, cuadros llave | $0.35 | la fresa termina el canal y sube el tornillo |
| 5 | 20–25 | **Kling o3 pro + video Blender** | $0.84 | el tornillo se atornilla hasta el fondo e integra |
| 6 | 25–30 | Kling 2.6 pro, cuadros llave | $0.35 | el hueso integra y la corona sube y se asienta |
| 7 | 30–35 | **Seedance 2.0 fast 480p**   | $0.50 | la piel regresa y la sonrisa se abre |
|   |       | **clips usados**             | **$5.24** | |

Gasto total del día, con intentos fallidos: **$7.83** (saldo 17.91 → 10.08).

## Precios reales medidos (WaveSpeed no los reporta por trabajo; esto sale del saldo)

| modelo | lista | real | factor |
|---|---|---|---|
| Kling 2.6 pro image-to-video | $0.35 | **$0.35** | 1.0× (no acepta resolución ni duración libres) |
| Kling o3 pro reference-to-video | $0.56 | **$0.84** | 1.5× |
| Seedance 2.0 fast **480p** | $0.50 | **$0.50** | 1.0× |
| Seedance 2.0 fast **1080p** | $0.50 | **$2.50** | 5× |

**Seedance cobra por píxeles.** 1080p tiene 5.05× los píxeles de 480p y cobró exactamente 5×.
El tramo 3 costó $2 de más por haberlo pedido en 1080p sin necesidad.

## Lo que se descartó y por qué

- **`kling-v2.6-pro/motion-control`** ($0.336, el más barato con video de control): **no sirve**.
  Es transferencia de movimiento de *personajes* y exige detectar a alguien de medio cuerpo.
  Rechazó el corte anatómico: *"No complete upper body detected"*. No cobró.
- **`reference-to-video` para todo**: funciona donde el Blender tiene movimiento real (tramo 5),
  falla donde está quieto (tramo 6: copió el contorno verde menta del render gris y volteó el
  implante). No es una vía pareja.
- **Seedance para todo**: la calidad es la mejor, pero a 1080p son $2.50 por tramo, $17.50 el video.

## Las tres trampas que costaron intentos

1. **Kling cruza por disolvencia cuando los dos cuadros llave son muy distintos.** Por eso el
   despegue (tramo 3) y el regreso de la piel (tramo 7) le salieron con la anatomía encimada
   sobre la cara. Dos intentos de prompt no lo arreglaron; Seedance lo resolvió a la primera
   porque respeta un orden de eventos escrito ("primero sólo la piel, después revelar detrás").
2. **"Encima" es ambiguo en esta vista.** El hueso está arriba y los dientes cuelgan, así que
   "el pilar va encima del implante" es correcto anatómicamente pero todos los modelos lo leen
   como "arriba en pantalla" y se lo pegan al techo del hueso. Tres intentos del tramo 6 se
   fueron en eso. **Se arregló quitando el pilar**, que además la voz nunca menciona.
3. **"Aparece" hace que el modelo meta una pieza volando.** En el tramo 5, "aparece una tapa de
   cicatrización" produjo un segundo tornillo bajando del cielo. Hay que escribir que la pieza
   ya es parte de lo que está en cuadro.

## Pendiente conocido: el brinco del segundo 20

En el corte de los 20 s **el implante se regresa**: el tramo 4 termina con él ya entrando en el
hueso y el tramo 5 empieza con él otra vez abajo, afuera.

Es estructural, no un error del modelo. El tramo 4 termina en el cuadro llave `06_implante_entra`,
que corresponde al segundo **20.67** del Blender, no al 20.00; y `reference-to-video` no acepta
cuadro inicial, se guía sólo por el Blender. Mezclar los dos métodos no empalma.

Arreglo recomendado: **rehacer el tramo 4 con `reference-to-video`** y el pedazo de Blender de
15 a 20 s (`MOVIMIENTO_BLENDER_T4.mp4`, lo genera solo `correr_con_blender.py 4`). Así los dos
tramos siguen la misma línea de tiempo y empalman por construcción. **$0.84.**

## Otros pendientes menores

- La encía de los tramos 4, 5 y 6 se ve bastante roja. **No es de los modelos: ya viene así en
  los cuadros llave 06, 07 y 08** del 15 sep. Si a Alberto le parece irritada, se regeneran esos
  tres cuadros con GPT Image 2 (centavos) y se rehacen esos tramos.
- El tramo 7 es 480p subido a 1080: pierde textura fina de piel. Comparación en
  `COMPARACION_NITIDEZ_T7.jpg`. A 720p serían ~$1.13.
- Sigue sin resolverse lo del 14 sep: la etiqueta del frasco dice sólo "Boswellia Serrata" — ese
  pendiente es del otro cliente (360 Salud), no de éste.
- Afirmaciones médicas genéricas. **Confirmar con Alberto antes de publicar**, sobre todo
  "con los meses" y que el texto no promete resultados.
