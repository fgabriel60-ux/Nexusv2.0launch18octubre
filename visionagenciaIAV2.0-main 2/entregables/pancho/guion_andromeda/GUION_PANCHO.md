# Pancho Mecánico — guion nuevo (18 sep 2026)

## Guion recomendado: A · "Antes de pagar" (~22 s)

| Escena Nexus | Toma | Voz |
|---|---|---|
| HOOK (0–3 s) | Stride en el taller, caminando hacia la cámara | ¿Te quieren cambiar medio carro? Antes de pagar, escúchame. |
| DEMO (3–9 s) | Adentro, camioneta en las rampas | Hay talleres que cambian piezas hasta atinarle… y tú pagas cada intento. Yo primero encuentro la falla. |
| TRUST (9–15 s) | Banqueta / fachada del taller | Aquí un carro se arregla entendiéndolo, no cambiándole todo. |
| CTA (15–22 s) | Patio, saliendo a la luz | Mándame por WhatsApp una foto o un audio del ruido, y hoy te digo qué tiene y cuánto cuesta. |

### Por qué funciona (psicología del cliente de taller)
1. **El miedo real no es el precio, es que lo roben.** El hook toca justo esa herida ("cambiar medio carro") y frena el scroll con una pregunta que el cliente ya se hizo.
2. **Enemigo común.** "Talleres que cambian piezas hasta atinarle" pone a Pancho del lado del cliente sin atacar a nadie con nombre.
3. **Aversión a la pérdida.** "Tú pagas cada intento" convierte el problema en dinero que se pierde.
4. **Autoridad por método, no por presumir.** "Aquí un carro se arregla entendiéndolo" da confianza con su forma de trabajar, sin sonar a comercial.
5. **CTA de fricción mínima.** Mandar una foto o **un audio del ruido** cuesta 5 segundos y es algo que el cliente sí puede hacer desde el carro. Eso abre conversación, que es lo que optimiza la campaña.
6. **Inmediatez concreta.** "Hoy te digo qué tiene y cuánto cuesta" = certeza de precio antes de comprometerse.

## Alternativas (para variedad de creativos en Meta)

**B · "Ese ruido"** (urgencia):
Ese ruido no se va a quitar solo, y cada semana sale más caro. Grábalo con tu celular y mándamelo por WhatsApp. Yo lo escucho y te digo qué es, antes de que gastes un peso. Soy Pancho, mecánico. Te digo qué tiene, cuánto cuesta, y te lo dejo andando.

**C · "La regla del taller"** (confianza):
En mi taller hay una regla: si no sabes qué tiene el carro, no le cambies nada. Así trabajo. Primero encuentro la falla, luego te digo el precio, y solo cambio lo que de verdad falla. Tú decides con el precio en la mano. Manda foto por WhatsApp y hoy mismo te paso el precio.

La Andromeda real de Meta premia **conceptos distintos** (ángulo, escena y emoción diferentes), no diferencias de palabras. Por eso A, B y C atacan tres motivos distintos: miedo al abuso, urgencia y confianza.

## Qué dijo el simulador de Andromeda Lab
Mismo historial y contexto de la campaña ganadora, 966.63 MXN, 19 días, semilla 42:

| Guion | Conversaciones mediana (P10–P90) | Costo mediana |
|---|---:|---:|
| Actual (historia, el anuncio que ya corre) | 93 (71–127) | $10.39 |
| A · Antes de pagar | 93 (71–127) | $10.39 |
| B · Ese ruido | 93 (71–127) | $10.39 |
| C · La regla del taller | 93 (71–127) | $10.39 |

**Los cuatro salen idénticos**, y es lo esperado: el modelo textual está apagado (`text_model_enabled: false`) porque el historial tiene muy pocos anuncios y campañas para validarlo. El motor trata a todas las ideas con la "base común". Además, ese historial es de anuncios de la agencia, no de talleres.
**Ningún guion puede "ganarle" al simulador hoy.** Para que distinga guiones necesita ≥8 anuncios de mensajes con su texto y ≥3 campañas. La forma de llegar ahí es correr A, B y C como anuncios reales y meter sus resultados al historial.

## Pendiente de confirmar con Pancho
- Que sí contesta **el mismo día** con precio (el guion lo promete).
- Que acepta **audios del ruido** por WhatsApp.
- El guion nuevo ya **no menciona al papá** (A, B y C). El anuncio actual sí lo hace.
- No se prometió diagnóstico gratis ni garantía: no inventar ofertas que él no dé.
