# Book nook — Sanctum Sanctorum (Dr. Strange)

Diorama de estantería en MDF de 3 mm, corte y grabado láser. Interpretación estilizada del interior del Sanctum: pórtico de entrada, baranda dorada, escalones con cofre y pedestales, pilastras, aro dentado y la gran ventana circular con barras curvas, techo de celosía.

## Medidas
- Exterior: 150 (ancho) × 200 (fondo) × 255 (alto) mm. Para otro tamaño de libro, cambiar `W, D, H` en el script y revisar los intervalos de las uniones.
- MDF de 3 mm (`T` en el script: **medir el espesor real** antes de cortar; MDF común varía 2.7–3.0 mm). Kerf 0.12 mm (`KERF`), compensado en las rutas.
- 17 piezas distintas, 4 hojas de 600×400 mm (`hoja_N_corte.svg` / `.dxf`). Rojo = corte, azul = grabado (el texto azul son etiquetas de pieza, borrar o grabar suave).

## Archivos
- `hoja_1..4_corte.svg/.dxf` — archivos de corte (capas CORTE y GRABADO en el DXF).
- `hoja_N_preview.png`, `vista_frontal.png`, `vista_capas.png` — vistas previas (la oblicua va sin techo ni pared derecha).
- `generar_booknook.py` — generador (requiere `shapely`, `ezdxf`, `cairosvg`). Incluye verificaciones.

## Orden de ensamble
1. `base_fondo` (inferior) + 2 `nervio_piso` → `piso` encima (compartimento LED, 12 mm).
2. Pegar `lado_izq` y `lado_der` (la cara grabada va hacia dentro) con las pestañas de base y piso.
3. `tapa_trasera` (atrás), luego `fondo_ventana` (con papel albal/pergamino detrás de la ventana).
4. Marcos de atrás hacia adelante: `marco5_aro`, `marco4_pilastras`, `marco3_escalon_cofre`, `marco2_baranda`, `marco1_portico`.
5. `techo_celosia`, 2 `nervio_techo` y `tapa_superior` (cámara de luz superior de 9 mm).
Probar en seco antes de pegar; usar cola blanca en las pestañas.

## Pintura
Madera oscura (nogal/caoba) en paredes y pilastras; dorado/latón en baranda, denticulos y celosía; ventana en negro bronce con papel cálido detrás; piso en madera media.

## LED
- Tira LED cálida (3000 K) a lo largo del techo (entre celosía y tapa superior): luz hacia abajo por la celosía.
- Tira en la cámara trasera detrás de la ventana, y/o en el compartimento inferior. Cables salen por los orificios de Ø8 mm en `tapa_trasera` y `tapa_superior`.
