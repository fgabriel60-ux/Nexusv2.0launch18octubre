# Video de la Snitch-Colibrí — listo para encolar, sin gastar todavía

21 segundos en 5 tomas verticales. **Nada está encolado:** la cuenta `carlosfavelajeje` va en
saldo **−$10.18** (crédito de $30 agotado, facturado $40.23 al 3 nov), así que esto ya se
cobra de tarjeta. Falta tu OK.

Costo estimado con tus corridas del 1 de nov como referencia:
`cuadros` salió entre $0.14 y $0.27, `animar` entre $0.47 y $0.63. Aquí son 6 cuadros y
5 tomas → **~$0.85 USD**.

## Paso 1 — las 4 referencias las genera Codex

Qwen-Image-Edit necesita fotos de partida y no hay fotos reales de un aparato que no existe.
Según la regla, las imágenes las hace Codex. Cuatro PNG en `proyectos/snitch_colibri/refs/`:

| Archivo | Qué pedirle a Codex |
|---|---|
| `esfera_dorada.png` | Esfera de latón dorado grabado del tamaño de una pelota de golf, con una ranura fina en el polo superior y dos ranuras laterales cerradas, acabado envejecido con marcas de uso, sobre fondo gris neutro, luz de estudio suave, foto macro real, vertical 720×1280. |
| `alas_mylar.png` | Par de alas de ornitóptero de 75 mm: membrana de Mylar dorado translúcido iridiscente con dos nervaduras de fibra de carbono negra visibles, borde de ataque recto y punta redondeada, extendidas sobre fondo negro mate, retroiluminadas, foto macro real, vertical. |
| `mecanismo_interior.png` | Mecanismo de relojería diminuto en latón dorado dentro de media cáscara esférica abierta: una corona dentada grande horizontal, una palanca con ranura, dos tambores pequeños unidos por una cinta tensada, ejes de acero. Macro extremo, luz dura lateral, foto real, vertical. |
| `mesa_taller.png` | Mesa de taller de madera gastada vista casi desde arriba, con un calibrador, pinzas finas de electrónica, un cúter y un plano técnico impreso al lado, luz de ventana lateral, foto real, vertical. |

## Paso 2 — cuadros (Qwen), cuando autorices

    cd /workspaces/Nexusv2.0launch18octubre
    echo "GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run clientes/_escenas_carlos/escenas_carlos_modal.py::cuadros_par --spec proyectos/snitch_colibri/escenas_snitch.json > proyectos/snitch_colibri/cuadros.log 2>&1" \
      > entregables/fila_escenas/pendientes/$(date +%Y%m%d_%H%M)_snitch.sh

`cuadros_par` reparte los 6 cuadros en contenedores a la vez; sale más rápido por el mismo
precio. Revisar los PNG en `cuadros/` antes de animar: si la esfera sale de plástico o las
alas de plumas, se corrige el prompt y se repite solo ese cuadro, que es lo barato.

## Paso 3 — animar (MiniMax H3), solo con los cuadros aprobados

    echo "GASTO_PERFIL=carlosfavelajeje python3 gasto_modal.py run clientes/_escenas_carlos/escenas_carlos_modal.py::animar --spec proyectos/snitch_colibri/escenas_snitch.json > proyectos/snitch_colibri/animar.log 2>&1" \
      > entregables/fila_escenas/pendientes/$(date +%Y%m%d_%H%M)_snitch_animar.sh

## Las 5 tomas

| Toma | Seg | Qué pasa |
|---|---:|---|
| T1 · reposo | 4 | La esfera cerrada en la mesa, un reflejo recorre el latón. Es la que vende el objeto. |
| T2 · abre | 4 | Las alas se despliegan con movimiento mecánico y quedan extendidas. |
| T3 · vuelo | 5 | Flota con las alas en dos arcos borrosos, el cuerpo oscilando apenas. La toma clave. |
| T4 · mecanismo | 4 | Macro de la corona girando y la palanca oscilando. Lo que nadie más muestra. |
| T5 · mano | 4 | La mano se cierra y la esfera escapa hacia arriba. El cierre. |

## Lo que no va a funcionar bien, para que no sea sorpresa

- **El batido a 31 Hz no se puede mostrar nítido.** A 24 fps son 1.3 aletazos por cuadro:
  en video real solo se ve el arco borroso, igual que un colibrí en un celular. Por eso T3
  se pide con las alas borrosas a propósito; pedirlas nítidas da el aspecto de muñeco.
- **MiniMax va a querer mover la esfera como un dron.** Si sale flotando demasiado estable,
  bajar a 4 s y agregar la deriva lateral en el prompt.
- **El clap-and-fling (las alas tocándose arriba) no se va a ver.** Eso se enseña con el
  dibujo animado de la página, no con el video generado.
