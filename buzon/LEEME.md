# Buzón entre las dos sesiones de Claude en Modal

Hay DOS Claude en el mismo sandbox `nexus-claude` (cuenta Modal carlosfavelajeje), con la misma memoria y el mismo workspace:
- **nexus**  → cuenta Claude charlyfavela666 (`/vol/claude-config`). Su uso está por acabarse.
- **nexus2** → cuenta Claude carlosfavelajeje@gmail.com (`/vol/claude-config-2`). Toma el trabajo pesado.

## Cómo comunicarse
- Mensaje para la otra sesión: crea `buzon/para_nexus2/AAAAMMDD_HHMM_tema.md` o `buzon/para_nexus/...`.
- Al empezar cada vuelta del loop, revisa tu carpeta; al atender un mensaje muévelo a `buzon/hecho/`.
- Antes de tomar un cliente, anótalo en `buzon/tomados.md` (`cliente · sesión · hora`) para no trabajar los dos lo mismo ni correr dos GPU contra el mismo volumen.
- WhatsApp: solo UNA sesión corre el loop que contesta a Carlos (por defecto **nexus2**). nexus solo trabaja lo que le dejen en el buzón.
