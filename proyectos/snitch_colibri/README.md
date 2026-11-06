# Snitch-Colibrí

Replicar la snitch dorada con la mecánica de batido de un colibrí.

| Archivo | Qué es |
|---|---|
| `DISENO.md` | El diseño mecánico completo: las 4 etapas del mecanismo, control, presupuesto de masa, lista de materiales, plan de construcción por etapas. |
| `calculos_vuelo.py` | La hoja de cálculo aerodinámica. Validada contra un colibrí real y contra el Nano Hummingbird antes de usarla. `python3 calculos_vuelo.py` |
| `mecanismo.html` | Explicador publicado: planta animada del mecanismo, corte de la muñeca de torsión y calculadora de vuelo en vivo. |
| `escenas_snitch.json` | Spec de 6 cuadros y 5 tomas para el pipeline Qwen + MiniMax. **No encolado.** |
| `VIDEO.md` | Cómo generarlo, qué pedirle a Codex y cuánto cuesta. |
| `refs/` | Donde van las 4 referencias que genera Codex. Vacío todavía. |
| `cuadros/` | Salida de Qwen. Vacío todavía. |

## En una línea

Esfera de 55 mm, alas de 150 mm, 29.4 g, batido de 31 Hz con clap-and-fling: **39.9 g de
sustentación, margen 1.36×, 11.5 minutos**, ~99 USD de materiales. La esfera canónica de
40 mm no vuela batiendo (7.1 g para 12 g de masa) y se hace por levitación magnética.
