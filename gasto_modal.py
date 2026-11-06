"""Manda trabajos de GPU a la cuenta Modal `fgabriel60` (aunque Claude corra en otra) y reporta cuánto gastó cada uno y el saldo restante.

  python3 gasto_modal.py saldo                              # saldo restante según el facturado
  python3 gasto_modal.py run clientes/X/video/x_modal.py [::funcion] [args...]   # = `modal run`, y al final imprime gasto y saldo
  python3 gasto_modal.py vigilar                            # detiene todo al llegar a LIMITE_GASTO ($14 gastados)
  python3 gasto_modal.py inicializar 15.00                  # fija el saldo actual (una vez, o al recargar)
Libro de gastos: gastos_fgabriel60.jsonl (junto a este archivo). Dentro del sandbox lee el token de /vol/claude-config/modal-fgabriel60.env;
fuera usa el perfil fgabriel60 de ~/.modal.toml. El facturado de Modal tarda unos minutos en aparecer: si el gasto sale en 0, repetir `saldo` luego."""
import json
import os
import re
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PERFIL = os.environ.get("GASTO_PERFIL", "charlyfavela666")   # 3 nov 2026: Carlos mudó TODO a charlyfavela666 ($30 de crédito intactos).
# carlosfavelajeje quedó agotada: consumió $39.98 sobre $30 de crédito y ya cobra dinero real ($9.85),
# de los cuales $24.80 fueron la app desplegada nexus-claude corriendo sin parar desde el 31 oct.
LIBRO = f"{AQUI}/gastos_{PERFIL}.jsonl"
ENV_TOKEN = f"/vol/claude-config/modal-{PERFIL}.env"   # dentro del sandbox: token del perfil (modal-fgabriel60.env / modal-charlyfavela666.env)
CREDITO = PERFIL in ("charlyfavela666", "carlosfavelajeje")
# 3 nov 2026: Carlos pidió TOPE ILIMITADO (antes 28.0 con crédito / 14.7 sin crédito).
# OJO: al momento del cambio carlosfavelajeje iba facturado en $39.61 sobre un crédito de $30 (saldo -$9.56),
# así que ya no hay vigía que detenga el gasto. Para volver al tope anterior: LIMITE_GASTO = 28.0 if CREDITO else 14.7
LIMITE_GASTO = float("inf")  # Carlos (30 oct 20:50): tope de $6 más en fgabriel60 (iba en $8.71 gastados); 666 se reserva para el sandbox de Claude


def _entorno():
    env = dict(os.environ)
    env["MODAL_IMAGE_BUILDER_VERSION"] = "2025.06"   # el cliente instalado no soporta la versión de imagen 2026.10 de la cuenta
    if PERFIL != "fgabriel60" and not os.path.exists(ENV_TOKEN):
        env["MODAL_PROFILE"] = PERFIL
    elif os.path.exists(ENV_TOKEN):
        for l in open(ENV_TOKEN):
            if "=" in l:
                k, v = l.strip().split("=", 1)
                env[k] = v
    else:
        env["MODAL_PROFILE"] = "fgabriel60"
    return env


def _modal(*args):
    r = subprocess.run(["modal", *args], env=_entorno(), capture_output=True, text=True)
    return r.stdout + r.stderr


def facturado():
    """(facturado por encima del crédito, consumo total) del periodo según `modal billing summary`."""
    t = _modal("billing", "summary")
    f = re.search(r"Billed Cost:\s*\$?([\d.]+)", t)
    m = re.search(r"Metered Cost:\s*([\d.]+)", t)
    if CREDITO and m:   # con crédito gratis el facturado es $0: el gasto real es el consumo medido
        return float(m.group(1)), float(m.group(1))
    if not f:
        sys.exit("No pude leer el facturado:\n" + t[-500:])
    return float(f.group(1)), float(m.group(1)) if m else 0.0


def _libro():
    return [json.loads(l) for l in open(LIBRO)] if os.path.exists(LIBRO) else []


def _anotar(**d):
    with open(LIBRO, "a") as f:
        f.write(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M:%S"), **d}, ensure_ascii=False) + "\n")


def saldo(fact=None):
    ini = [e for e in _libro() if e.get("tipo") == "inicio"]
    if not ini:
        sys.exit("Falta fijar el saldo: python3 gasto_modal.py inicializar 15.00")
    fact = facturado()[0] if fact is None else fact
    return ini[-1]["saldo"] - (fact - ini[-1]["facturado"]), fact


def _por_app():
    """Costo de hoy por app (Object ID) según el reporte por hora."""
    t = _modal("billing", "report", "--for", "today", "--resolution", "h", "--show-resources", "--json")
    try:
        filas = json.loads(t[t.index("["):t.rindex("]") + 1])
    except ValueError:
        return {}
    d = {}
    for f in filas:
        k = (f.get("object_id") or f.get("Object ID"), f.get("description") or f.get("Description"))
        d[k] = d.get(k, 0) + float(f.get("cost") or f.get("Cost") or 0)
    return d


def gastado():
    ini = [e for e in _libro() if e.get("tipo") == "inicio"][-1]
    return ini["saldo"] - saldo()[0] + 0.0


def detener_todo():
    """Detiene las apps efímeras en marcha de fgabriel60 (no toca las desplegadas)."""
    apps = json.loads(_modal("app", "list", "--json") or "[]")
    for a in apps:
        if a.get("state") == "ephemeral":
            print("deteniendo", a["description"], a["app_id"], flush=True)
            _modal("app", "stop", "-y", a["app_id"])


def vigilar():
    """Cada 2 min revisa el gasto; al llegar a LIMITE_GASTO detiene todo y avisa en vigilante.log."""
    while True:
        g = gastado()
        print(time.strftime("%H:%M:%S"), f"gastado ${g:.2f} de ${LIMITE_GASTO:.2f}", flush=True)
        if g >= LIMITE_GASTO:
            detener_todo()
            _anotar(tipo="alto", gastado=round(g, 2))
            print("LÍMITE ALCANZADO: todo detenido", flush=True)
            return
        time.sleep(120)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "saldo"
    if cmd == "inicializar":
        fact = facturado()[0]
        _anotar(tipo="inicio", saldo=float(sys.argv[2]), facturado=fact)
        print(f"Saldo fijado en ${float(sys.argv[2]):.2f} (facturado actual ${fact:.2f})")
    elif cmd == "saldo":
        s, fact = saldo()
        print(f"{PERFIL}: saldo restante ≈ ${s:.2f} (facturado ${fact:.2f})")
    elif cmd == "vigilar":
        vigilar()
    elif cmd == "run":
        if gastado() >= LIMITE_GASTO:
            sys.exit(f"Límite de ${LIMITE_GASTO:.0f} alcanzado: no se lanza el trabajo.")
        antes, fact0 = _por_app(), facturado()[0]
        t0 = time.time()
        rc = subprocess.run(["modal", "run", *sys.argv[2:]], env=_entorno()).returncode
        seg = time.time() - t0
        time.sleep(90)  # el reporte de Modal tarda en reflejar el trabajo
        despues = _por_app()
        costo = {k: v - antes.get(k, 0) for k, v in despues.items() if v - antes.get(k, 0) > 1e-4}
        total = sum(costo.values())
        s, fact1 = saldo()
        _anotar(tipo="trabajo", trabajo=" ".join(sys.argv[2:]), segundos=round(seg), costo=round(total, 4),
                apps={f"{k[1]}": round(v, 4) for k, v in costo.items()}, facturado=fact1, saldo=round(s, 2), rc=rc)
        print(f"\n== Reporte Modal {PERFIL} ==\nTrabajo: {' '.join(sys.argv[2:])}\nDuración: {seg/60:.1f} min  (código {rc})")
        for k, v in costo.items():
            print(f"  {k[1]} ({k[0]}): ${v:.3f}")
        print(f"Gasto del trabajo: ${total:.3f}\nSaldo restante ≈ ${s:.2f}")
        sys.exit(rc)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
