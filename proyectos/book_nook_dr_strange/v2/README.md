# Book nook Sanctum Sanctorum — v2 (más detalle)

La v1 sigue intacta en la carpeta superior. Misma caja: 150 × 200 × 255 mm, MDF 3 mm (`T` en el script: medir el espesor real), kerf 0.12 mm compensado.

## Qué cambió respecto a v1
- Ventana del Sanctum: aro con radios y 2 anillos de retícula, 4 barras curvas, aro ornamental grabado (anillos + radios cortos) y aro dentado calado delante.
- Fachada de ladrillo grabada (marco 1), con cornisa, denticulos calados y molduras grabadas.
- Capas nuevas: `marco1b_arco` y `marco4b_arco_profundo` (arcos con festoneado calado). Ahora son 5 marcos de arco/fachada más balcón y escalera: 20 piezas distintas.
- Balcón: barrotes de 2.4 mm, riel medio, pasamanos, dos faroles calados.
- Escalera de 3 escalones con postes y pomos, cofre y pedestales con cajones.
- Puerta con 4 paneles y montante en `marco5_aro_puerta`.
- Ventanas laterales caladas (arco con parteluz) en ambas paredes.
- Texturas grabadas: ladrillo, sillares de piedra, vetas de madera, parquet en espiga.
- Techo con relieve: `techo_relieve` (se **pega** sobre la celosía, sin pestañas) deja 4 ventanas por celda.
- Hojas: 3 hojas de 600×400 (antes 4) con empaquetado MaxRects y rotación.
- Etiquetas en capa propia `ETIQUETAS` (verde en SVG/DXF): **desactivarla** al cortar; no están en CORTE ni GRABADO.
- Vista previa completa (`vista_completa.png`): incluye techo y pared derecha en transparencia.

## Archivos
`hoja_1..3_corte.svg/.dxf` (capas CORTE rojo, GRABADO azul, ETIQUETAS verde), `hoja_N_preview.png`, `vista_frontal.png`, `vista_completa.png`, `generar_booknook_v2.py` (shapely, ezdxf, cairosvg; tarda ~1 min por la búsqueda de empaquetado).

## Ensamble (orden)
1. `base_fondo` + 2 `nervio_piso` → `piso`.
2. Paredes laterales (cara grabada hacia dentro) con las pestañas de base y piso.
3. `tapa_trasera`, `fondo_ventana` (papel pergamino detrás de la ventana).
4. Marcos de atrás hacia delante: `marco5_aro_puerta`, `marco4b_arco_profundo`, `marco4_pilastras`, `marco3_escalera_cofre`, `marco2_balcon`, `marco1b_arco`, `marco1_fachada`.
5. `techo_celosia`, pegar `techo_relieve` encima, 2 `nervio_techo`, `tapa_superior`.

## Pintura y LED
Ladrillo ocre/rojizo lavado con tinta oscura en las juntas; madera nogal en paredes; dorado en baranda, farolas, denticulos y celosía. LED cálido 3000 K en la cámara del techo (luz por celosía y relieve) y detrás de la ventana; cables por los orificios de Ø8 mm.

## Verificado por código / no verificado
Verificado: sin interferencias entre piezas ensambladas, sin piezas partidas, puentes ≥ 2 mm, separación ≥ 2 mm entre piezas en hoja. **No** probado: corte real, ajuste de pestañas con el MDF real, fragilidad de barrotes (2.4 mm) y del festoneado; la fidelidad al Sanctum es estilizada (las barras de la ventana no son una copia exacta).
