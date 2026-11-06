# Snitch-Colibrí — mecanismo de vuelo batiente

Replicar la snitch dorada con la mecánica de un colibrí: esfera dorada con dos alas
que baten de verdad, vuelo libre estacionario y errático.

Todos los números de este documento salen de `calculos_vuelo.py` (modelo cuasi-estacionario
de elemento de pala para alas batientes en hover). El modelo está validado contra dos
aparatos reales antes de usarlo para diseñar:

| Referencia | Masa real | Sustentación que predice el modelo | ¿Coherente? |
|---|---|---|---|
| Colibrí Amazilia (biológico) | 4.5 g | 7.8 g (margen 1.74×) | sí, un colibrí carga y maniobra |
| Nano Hummingbird, AeroVironment 2011 | 19 g | 34.9 g (margen 1.84×) | sí, voló libre 11 min |

## Veredicto antes de gastar un peso

| Variante | Qué es | Veredicto |
|---|---|---|
| **A — Snitch voladora 55 mm** | Esfera de 55 mm, alas de 150 mm, 29.4 g, batido 31 Hz | **Vuela.** Margen 1.36×, 11.5 min |
| **B — Alas separadas, sin clap** | Lo mismo pero con amplitud de 160° y alas que no se tocan | **No vuela.** 22.6 g de sustentación para 25 g de masa (margen 0.90×) |
| **C — Esfera canónica de 40 mm** | El tamaño que describe el libro | **No vuela batiendo.** 7.1 g de sustentación para 12 g (margen 0.59×). Se hace por levitación magnética |

Las dos cosas que NO son opcionales en la variante A:

1. **Amplitud de 180° con clap-and-fling** (las alas se tocan arriba del todo). Es lo que
   sube el C_L medio de 1.8 a 2.2 y da el 20 % de sustentación que falta. Con 160° no vuela.
2. **Techo de masa de 33 g.** A 33.4 g el margen cae a 1.20× y ya no hay autoridad de
   control. Cada tornillo se pesa.

## El mecanismo, etapa por etapa

El problema central: un motor gira a 15 000 rpm en un solo sentido, y un ala tiene que
barrer 180° de ida y vuelta 31 veces por segundo, volteándose en cada extremo. Cuatro etapas.

### Etapa 1 — Reducción 8:1
Motor coreless 8×20 mm (tipo 8520), ~15 000 rpm bajo carga. Piñón de 9 dientes módulo 0.4
en el eje de 1.0 mm, corona de 72 dientes (28.8 mm de diámetro primitivo, cabe en la esfera
de 55 mm). 15 000 / 8 / 60 = **31 Hz de batido**.

### Etapa 2 — Manivela y palanca ranurada: rotación → oscilación
La corona lleva un pin de acero de 1.0 mm a radio **r = 2.8 mm** de su centro. Ese pin corre
en una ranura recta de 1.1 mm tallada en el brazo oscilante, cuyo pivote está a **d = 4.0 mm**
del centro de la corona.

    θ_max = asin(r/d) = asin(0.70) = ±44.4°  →  88.8° de barrido

Es el mecanismo de la limadora. Se usa en lugar de un cuatro-barras porque tiene una sola
junta deslizante en vez de tres pasadores: menos juego y menos piezas que fallen a 31 Hz,
que son 1.9 millones de ciclos por hora de vuelo.

### Etapa 3 — Amplificador por cinta 2:1
88.8° no alcanzan para el clap. Un tambor de **Ø 19.2 mm** en el pivote de la palanca tira de
una cinta de Kevlar de 0.2 mm pretensada, enrollada en un tambor de **Ø 9.6 mm** en el eje
del ala:

    88.8° × 2 = 177.6° de barrido del ala  →  clap-and-fling, lo que exige el punto 1

**Por qué cinta y no sectores dentados.** Con un par de sectores (radios 9.6 y 4.8 mm,
módulo 0.4) la distancia entre centros queda fija en 14.4 mm, y eso empuja los ejes de las
dos alas a 37 mm uno del otro: las alas ya no se alcanzan y **se pierde el clap**, que es
justo lo que separa la variante A de la B. La cinta no impone distancia, así que los ejes se
ponen a 11 mm, las alas se solapan y el clap existe. De paso pesa menos y no tiene juego de
dientes que se salte. Es también la solución del Nano Hummingbird, que transmite por cuerda.

La cinta es la pieza de desgaste del aparato: va pretensada con dos resortes y se cambia
cada pocas horas de vuelo. Llevar repuestos cortados a medida.

Las dos alas salen del mismo cigüeñal, con los pines a 180°, para que baten en espejo
perfecto. Un desfase entre alas rompe el clap y mete par de alabeo parásito.

### Etapa 4 — Muñeca de torsión pasiva: el ángulo de ataque y el ocho
Aquí está el ingenio y es lo que copia al colibrí de verdad. **El ángulo de ataque no se
actúa.** El ala se monta en un casquillo libre sobre el borde de ataque (varilla de carbono
de 1.0 mm), con el centro de presión **2 mm por detrás** de ese eje de torsión. En cada
extremo del barrido, la inercia del ala y la presión dinámica voltean el ala solas, y dos
topes impresos en el casquillo la detienen en el ángulo elegido.

- Topes ajustables para un **AoA de 30° a 45°**; empezar en 38°, que es el rango que usa un
  colibrí en estacionario.
- El plano de batido se inclina **20° respecto a la horizontal**. Esa inclinación más el
  desfase de la torsión pasiva es lo que traza el **ocho horizontal** característico: no hay
  que programarlo, aparece.
- Sustentación en los dos medios ciclos (≈75 % en la ida, ≈25 % en la vuelta), igual que el
  pájaro. Un ala rígida sin muñeca da cero sustentación neta.

### Resorte de resonancia (ahorra 20-30 % de batería)
El motor no debe frenar y acelerar la inercia del ala 62 veces por segundo. Un resorte de
torsión en el eje del ala, sintonizado a la frecuencia de batido, devuelve esa energía:

    I_ala ≈ 1.31e-6 kg·m² (barra pivotando en el extremo) + ~45 % de masa de aire añadida ≈ 1.9e-6
    k = (2π·31)² × 1.9e-6 = 0.072 N·m/rad

Alambre de acero de piano de **0.5 mm**, espira de **1.5 mm** de diámetro interior,
**2 vueltas** (k = E·d⁴/(64·D·n) con E = 200 GPa). Pesa 0.04 g. Alternativa más tosca pero
más fácil de ajustar: una ballesta de fibra de vidrio de 0.3 mm recortada a la medida.

## Control: tres ejes sin sensores a bordo

Copiado del Nano Hummingbird, que es el único aparato de esta clase que voló libre.

| Eje | Cómo | Autoridad |
|---|---|---|
| Altura | frecuencia de batido (acelerador) | 31 Hz ± 5 |
| Cabeceo | servo inclina todo el plano de batido adelante/atrás | ±8° |
| Alabeo | servo inclina el plano de batido de lado | ±8° |
| Guiñada | servo cambia el tope de AoA de **una sola** ala → arrastre diferencial | ±6° |

Tres microservos lineales de 1.1 g y una placa de control brushed 1S con giroscopio
(tipo placa de whoop). **Sin el giro es impilotable**: el aparato tiene un periodo natural
de cabeceo de décimas de segundo, más rápido que la mano de una persona.

### El comportamiento de snitch está en el firmware, no en la mecánica
- **Errático:** ruido de Perlin de 0.5–2 Hz inyectado como consigna de alabeo y cabeceo
  sobre el hover estabilizado. Da el zigzag creíble sin que se caiga.
- **Esquiva:** no caben sensores en 29 g. Lazo externo: una webcam fija ve la esfera y las
  manos, una PC calcula el vector de escape y manda la corrección por el mismo enlace RC.
- **Lo que no se puede:** la snitch del libro vuela media hora. Aquí son 11.5 minutos, y es
  un límite de química de batería, no de diseño.

## Presupuesto de masa (el documento más importante del proyecto)

| g | Pieza |
|---:|---|
| 5.0 | motor coreless 8520, uno central |
| 2.0 | corona 72d + piñón 9d + cigüeñal + pin |
| 1.2 | 2 tambores + cinta de Kevlar + tensores |
| 1.4 | 2 alas (carbono 1.0/0.6 mm + Mylar 6 µm) |
| 0.5 | 2 resortes de resonancia + muñecas |
| 2.2 | bastidor interno de resina, en cercha |
| 6.5 | LiPo 1S 300 mAh HV |
| 2.8 | placa de control brushed 1S con giro |
| 3.3 | 3 microservos lineales de 1.1 g |
| 3.5 | 2 cáscaras esféricas de PETG, pared 0.35 mm |
| 1.0 | cables, tornillos, pegamento |
| **29.4** | **TOTAL** — techo absoluto 33 g |

Variante sin servos (dos motores independientes, control por amplitud diferencial):
27.7 g, margen 1.44×, 12.4 min. **Más fácil de construir y es por donde conviene empezar**,
aunque el control de guiñada es pobre.

## Lista de materiales y costo

| Pieza | Cant. | USD |
|---|---:|---:|
| Motor coreless 8520 | 2 (1 repuesto) | 8 |
| LiPo 1S 300 mAh HV | 3 | 12 |
| Placa control brushed 1S con giro | 1 | 25 |
| Microservo lineal 1.1 g | 3 | 15 |
| Varilla de carbono 1.0 / 0.6 mm | 1 m c/u | 8 |
| Mylar metalizado 6 µm | hoja A4 | 5 |
| Alambre de piano 0.5 mm | 1 m | 2 |
| Engranajes módulo 0.4 + cinta de Kevlar 0.2 mm | juego | 6 |
| Impresión en resina del bastidor y sectores | — | 10 |
| Pintura dorada + PETG de las cáscaras | — | 8 |
| **Total** | | **~99 USD / ~1 850 MXN** |

Los tambores, la corona y el bastidor van en **resina SLA**, no en FDM: el módulo 0.4 a
0.2 mm de capa sale con dientes redondeados y el engrane se salta.

## Plan de construcción, con criterio de aprobación

No se pasa de etapa sin cumplir el criterio. Cada etapa es un fin de semana.

1. **Banco de batido.** Mecanismo completo atornillado a una báscula de cocina, sin esfera
   ni batería, alimentado de fuente. *Criterio: la báscula marca ≥ 35 g de empuje a 31 Hz y
   el mecanismo sobrevive 10 minutos seguidos.* Si no da 35 g, no sigas: ajusta AoA y
   amplitud aquí, donde es barato.
2. **Alas.** Tres juegos con cuerda de 28, 30 y 32 mm; se mide cada uno en el banco. *Criterio:
   elegir el que dé más empuje por watt, no el que dé más empuje.*
3. **Resorte.** Sintonizar la k barriendo frecuencia y midiendo corriente. *Criterio: el consumo
   a 31 Hz baja al menos 15 % respecto a sin resorte.*
4. **Vuelo atado.** Todo montado, atado con hilo de 0.1 mm a un contrapeso que le quita 8 g.
   *Criterio: se sostiene y responde a los tres ejes.*
5. **Vuelo libre.** Quitar el hilo sobre una cama. *Criterio: 30 segundos de hover a media
   altura.*
6. **Cáscaras doradas y plegado.** Al final, cuando ya vuela. *Criterio: no subir de 33 g.*

El plegado de alas contra la esfera (lo que hace que parezca una snitch cerrada) es
**manual** en la versión 1: bisagra vertical en la raíz y pasador de resorte. El despliegue
automático por trinquete centrífugo al arrancar es una mejora para la versión 2, cuando ya
vuele; no se mete masa de adorno antes de volar.

## Variante C — la esfera canónica de 40 mm

Numéricamente imposible batiendo (7.1 g de sustentación para 12 g de masa). Las dos vías
honestas, y la primera es la más espectacular de las tres para exhibición y para video:

1. **Levitación magnética con energía inalámbrica.** Base con electroimán y sensor Hall en
   lazo cerrado, esfera con imán de neodimio de 6 mm, flotando a 25 mm. Las alas baten con
   un micromotor dentro, alimentado por acoplamiento inductivo desde la misma base:
   **autonomía ilimitada** y la esfera gira sobre sí misma. No vuela por la sala, pero flota
   de verdad y bate de verdad.
2. **Atada a brazo giratorio.** Hilo de pescar de 0.1 mm desde un eje en el techo. Vuela en
   círculo real; en cámara el hilo no se ve.
