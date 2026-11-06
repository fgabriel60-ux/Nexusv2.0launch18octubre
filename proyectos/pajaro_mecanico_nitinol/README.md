# Pájaro mecánico de nitinol (Swooping Evil) — mecanismo interno

> **Todo esto es SIMULACIÓN (modelo cinemático + dinámico 1D en Python). No hay prototipo ni prueba física.**
> Suposición: el «alambre de nitrilo» es **nitinol (NiTi)**, la aleación con memoria de forma / superelástica.

## Archivos
| Archivo | Qué es |
|---|---|
| `modelo.py` | Parámetros, geometría de puntales, dinámica del carrito+volante, dinámica del aleteo, chequeo de reenrollado |
| `render.py` | Anima (`python3 render.py`), y genera `diagrama_piezas.png` y `verificacion.png` (`python3 render.py --extra`) |
| `animacion_mecanismo.gif` / `.mp4` | Vistas superior y lateral con las 6 fases rotuladas (cámara lenta indicada en pantalla) |
| `diagrama_piezas.png` | Piezas numeradas y fases |
| `verificacion.png` | θ(s), fuerza sobre el carrito, velocidades, aleteo, frecuencia y balance de energía |

## Concepto (6 fases)
1. **Enrollado.** Tres alambres NiTi iguales (espina central + 2 costillas) en un rollo plano de Ø48 mm en la cola (H), como un matasuegras. Las raíces de los tres están en la cabeza T. La espina está termofijada *enrollada* (memoria); las costillas, rectas pero con raíz flexible. Un **pestillo** retiene todo.
2. **Lanzamiento.** Un latigazo lanza T hacia adelante y el rollo se desenrolla (120 mm de alambre). El carrito K, unido por los puntales, es arrastrado detrás de T.
3. **El carrito corre.** Al frenar T (fin del alambre), la inercia de K rompe un **detente de bola** (dispara por inercia). K corre por la espina hacia T empujado por un resorte de precarga y por las alas, que están termofijadas abiertas a 70°. Los **puntales** (tipo paraguas) abren las costillas de ~5° a 80° en 38 mm de carrera. En esa misma carrera K sigue un **surco helicoidal** (paso 40 mm/rev, entrada con rampa de 12 mm) que hace girar el tubo y su volante.
4. **Tope y aleteo.** K llega al tope y acopla un **embrague** entre volante y manivela (reducción 6:1). La manivela, con biela a cada costilla, bate **ambas alas en fase** (arriba/abajo).
5. **Reenrollado (el mecanismo inventado).** La manivela mueve un tren reductor hasta un **contador**: tras N = 12 aleteos, una muesca libera el **pestillo**. El rollo de NiTi recupera su forma por memoria (fuerza constante ≈ 0.5 N). Al entrar, un **embudo en H** cierra las costillas, devuelve a K (que desacopla el embrague) y el rollo se enrolla otra vez.
6. **Listo** para otro lanzamiento.

**Por qué esta opción de reenrollado:** no necesita motor ni electrónica. Toda la energía de retorno ya está guardada en el nitinol al desenrollarlo (comportamiento de resorte de fuerza constante, como una cinta métrica). El contador solo suelta un pestillo. Alternativas descartadas: trinquete + banda de retorno (más piezas y más fricción), y desacople simple por fin de rosca (no controla *cuántos* aleteos).

## Ajuste por la referencia de aleteo (GIF añadido)
En los cuadros: alas anchas con borde de espinas, batido **simétrico y en fase**, de **gran amplitud**: suben hasta plegarse sobre el cuerpo. Cambié respecto al primer diseño: amplitud de ±26° a **−31° … +50°** (eje de manivela desplazado 3 mm hacia arriba, r = 9 mm, b = 10 mm) y membrana con borde de espinas (por fabricar). Ojo: el GIF tiene solo 38 cuadros y no permite medir la frecuencia; los 2–3 Hz son suposición mía.

## Resultados de la simulación
- **Puntales:** θ de ~5° a 80° con 38 mm de carrera de K. Fuerza de empuje en todo el recorrido > fricción (0.03 N).
- **Surco → volante:** K llega al tope a 0.70 m/s; volante a 110 rad/s con **18 mJ** (la rampa del surco evita perder ~95 % de la energía que costaría un enganche brusco).
- **Aleteo:** 12 aleteos en 5.8 s, frecuencia de 2.8 → 1.6 Hz (cae por aire y fricción). Con el volante sobrante llegaría a ~16.
- **Reenrollado:** energía de recoil 61 mJ contra 28 mJ para cerrar alas + resorte + fricción → **margen ×2.2**.
- **Sensibilidad** (aleteos hasta parar, N objetivo = 12): fricción de rodamiento ×2 → 10 (**ya no llega a 12**); fricción de K ×3 → 15 (margen de recoil ×1.4); arrastre de aire ×1.5 → 14; E_NiTi 40 GPa → 16 (margen ×1.8).

## Dimensiones y materiales (valores del modelo)
- **Espina NiTi Ø0.70 mm**, 120 mm, rollo de R = 24 mm (deformación 1.5 %, dentro de lo elástico). **Costillas NiTi Ø0.35 mm**, 120 mm; envergadura abierta ≈ 235 mm. Raíz flexible de 30 mm (deformación < 1 %).
- **Puntales** Ø0.5 mm de acero; unión a 25 mm de la raíz, largo 26 mm (pandeo no es problema: Euler ≈ 9 N).
- **Carrito K:** latón, 6 g. **Resorte de precarga** ≈ 0.5 N. **Detente** de ≥ 1.2 N de retención (la simulación da 1.15 N justo al arrancar a 5°); la inercia al frenar T da ≈ 27 N.
- **Volante:** I = 3×10⁻⁶ kg·m² (≈ 10 g de latón, anillo Ø40/Ø28 × 1.6 mm), rodamientos de baja fricción (τ ≈ 1.5×10⁻⁵ N·m). Tren 6:1 y contador 1:12 impresos en 3D (resina) o cortados en láser.
- Masa total estimada ≈ 33 g. Cuerpo y H: impresión 3D; membrana: mylar o papel de seda con espinas.
- Nitinol: pedir **superelástico con Af < 15 °C**. Termofijar el rollo (~500 °C, temple en agua), costillas rectas con la raíz curvada a 70°.

## Cómo difiere de tu idea
- El giro por surcos **ocurre durante** la apertura de las alas (el surco cubre la misma carrera de K), no después. Hacerlo después exigiría un puntal telescópico con resorte para absorber el sobre-recorrido; lo dejé como mejora.
- Las alas se abren por puntales de paraguas, pero el **aleteo** va por manivela y bielas, no por el mismo carrito (el carrito solo alcanzaba un batido de barrido horizontal, no arriba/abajo).

## Riesgos y defectos conocidos
1. **Configuración casi singular** con las alas cerradas: el modelo da 1–2 N sobre K a 3–6°; si el detente es débil, las alas se abren solas.
2. **Disparo accidental** del detente al sacudir el pájaro.
3. **No vuela por su cuenta:** 18 mJ no sostienen vuelo. Es un mecanismo de exhibición o de lanzamiento.
4. **Margen ajustado en fricción:** con rodamientos ×2 peores ya no llega a 12 aleteos.
5. **Volante de 10 g + conjunto de 33 g** pesan mucho para alambres de Ø0.35 mm; las costillas pueden flexionar.
6. **Bielas a rótula a escala pequeña** (pasadores de 0.5 mm) se atoran fácilmente; la raíz flexible de nitinol sometida a dos movimientos (abrir y batir) puede torcerse.
7. **El desenrollado lo da la inercia del lanzamiento** (supuesto 3–4 m/s en T); con un tiro suave puede quedarse a medias.
8. El rollo recoge **las 3 espinas juntas**; que las costillas rectas reingresen ordenadas al embudo no está modelado.
9. El modelo es 1D en cada fase; sin contacto real, holguras ni tolerancias.

## Pruebas físicas por hacer (en orden)
1. Medir fuerza de recoil del rollo (dinamómetro) para Ø0.6/0.7 mm y R = 20–30 mm.
2. Probar un solo ala: raíz flexible + puntal; medir θ(s) real y la fuerza en el arranque.
3. Probar el surco con volante: velocidad de salida y pérdida en el enganche.
4. Probar manivela + bielas con la membrana y contar aleteos hasta parar (comparar con 12).
5. Probar el contador y el pestillo, y el cierre por el embudo (¿reingresan bien las costillas?).
6. Probar el ciclo completo 20 veces y medir dispersión; ajustar el detente.
