#!/usr/bin/env python3
"""Hoja de calculo aerodinamica para la Snitch-Colibri.
Modelo cuasi-estacionario de elemento de pala para alas batientes en vuelo
estacionario (hover), el estandar para ornitopteros a escala de insecto/colibri.
Referencias de validacion:
  - Colibri real (Amazilia): 4.5 g, 11 cm envergadura, 40 Hz  -> debe dar ~4.5 g
  - Nano Hummingbird (AeroVironment 2011): 19 g, 16.5 cm, 30 Hz -> debe dar ~19 g
"""
import math

RHO = 1.225          # densidad del aire kg/m3 (nivel del mar)
R2_HAT = 0.55        # segundo momento de area adimensional del ala (ala eliptica)
G = 9.80665

def analiza(nombre, masa_g, R_m, cuerda_m, freq_hz, amp_grados, CL=1.8,
            k_ind=1.2, eff_tren=0.40, bateria_mah=180, bateria_v=3.7,
            p_electronica_w=0.30, uso_bateria=0.80):
    """Devuelve sustentacion, margen, potencia y autonomia."""
    Phi = math.radians(amp_grados)          # amplitud total de barrido (rad)
    S = R_m * cuerda_m                      # area de UN ala (m2)
    AR = R_m / cuerda_m                     # relacion de aspecto de un ala

    # Velocidad media de la punta y velocidad de referencia ponderada
    U_tip = 2 * Phi * freq_hz * R_m
    U_ref = U_tip * R2_HAT

    # Sustentacion de las dos alas (promedio del ciclo)
    L_N = 2 * 0.5 * RHO * U_ref**2 * S * CL
    L_g = L_N / G * 1000
    peso_N = masa_g / 1000 * G
    margen = L_N / peso_N

    # Potencia inducida (teoria del disco actuador sobre el area barrida)
    A_disco = Phi * R_m**2
    P_ind = k_ind * peso_N**1.5 / math.sqrt(2 * RHO * A_disco)
    # Potencia de perfil: a este Reynolds es comparable a la inducida
    P_perfil = P_ind * 0.95
    P_aero = P_ind + P_perfil
    P_elec = P_aero / eff_tren + p_electronica_w

    # Autonomia
    Wh = bateria_mah / 1000 * bateria_v * uso_bateria
    minutos = Wh / P_elec * 60
    corriente_A = P_elec / bateria_v
    C_rate = corriente_A / (bateria_mah / 1000)

    # Reynolds en la cuerda media
    Re = U_ref * cuerda_m / 1.5e-5

    print(f"\n=== {nombre} ===")
    print(f"  masa {masa_g:.1f} g | envergadura alas {2*R_m*100:.1f} cm | cuerda {cuerda_m*100:.1f} cm | AR {AR:.1f}")
    print(f"  batido {freq_hz:.0f} Hz, amplitud {amp_grados:.0f} deg, CL medio {CL}")
    print(f"  vel. punta {U_tip:.1f} m/s | vel. referencia {U_ref:.2f} m/s | Re {Re:.0f}")
    print(f"  SUSTENTACION {L_N:.3f} N = {L_g:.1f} g   -> margen {margen:.2f}x", end="")
    print("  OK" if margen >= 1.20 else "  NO VUELA (necesita >=1.20)")
    print(f"  potencia aero {P_aero:.2f} W | electrica {P_elec:.2f} W | {corriente_A*1000:.0f} mA ({C_rate:.1f}C)")
    print(f"  AUTONOMIA {minutos:.1f} min con {bateria_mah} mAh 1S")
    return margen, minutos

print("#"*64)
print("VALIDACION DEL MODELO contra aparatos reales")
print("#"*64)
# Colibri real: amplitud ~165 deg, 40 Hz, ala 5.5 cm, cuerda 1.3 cm
analiza("Colibri real Amazilia (referencia biologica)", 4.5, 0.055, 0.013, 40, 165, CL=1.8)
# Nano Hummingbird: 16.5 cm total, usa clap-and-fling -> CL efectivo mas alto
analiza("Nano Hummingbird AeroVironment (referencia real)", 19.0, 0.075, 0.028, 30, 180, CL=2.2,
        bateria_mah=170)

print("\n" + "#"*64)
print("DISENO SNITCH-COLIBRI")
print("#"*64)
# A: la que vuela libre. Clap-and-fling (las alas se tocan arriba) -> CL 2.2
analiza("A - Snitch voladora (clap-and-fling, 2 motores)", 25.0, 0.075, 0.028, 30, 180, CL=2.2,
        bateria_mah=180)
# A con bateria mas grande
analiza("A+ - misma con bateria 300 mAh (+2 g)", 27.0, 0.075, 0.030, 31, 180, CL=2.2,
        bateria_mah=300)
# B: sin clap-and-fling, alas separadas (mas facil de construir)
analiza("B - alas separadas sin clap (mas facil)", 25.0, 0.075, 0.028, 30, 160, CL=1.8,
        bateria_mah=180)
# C: el tamano canonico de la snitch del libro
analiza("C - esfera canonica 4 cm (lo que pide el libro)", 12.0, 0.035, 0.014, 60, 180, CL=2.2,
        bateria_mah=60)

print("\n" + "#"*64)
print("DISENO FINAL con la masa real de la lista de materiales")
print("#"*64)
MASA = {
 "motor coreless 8520 (uno central)": 5.0,
 "corona 72d + pinon 9d + cigüenal + pin": 2.0,
 "2 sectores amplificadores + brazos": 1.2,
 "2 alas (carbono 1.0/0.6 mm + Mylar 6 um)": 1.4,
 "2 resortes de resonancia + munecas": 0.5,
 "bastidor interno (resina, cercha)": 2.2,
 "LiPo 1S 300 mAh HV": 6.5,
 "placa de control brushed 1S + giro": 2.8,
 "3 microservos lineales 1.1 g": 3.3,
 "2 cascaras esfericas PETG 0.35 mm": 3.5,
 "cables, tornillos, pegamento": 1.0,
}
for k, v in MASA.items():
    print(f"  {v:5.1f} g  {k}")
total = sum(MASA.values())
print(f"  {'-'*48}\n  {total:5.1f} g  TOTAL")
analiza("FINAL - Snitch-Colibri A (1 motor, 3 servos)", total, 0.075, 0.030, 31, 180, CL=2.2,
        bateria_mah=300)
print("\n  Sin los 3 servos (control por 2 motores, +1.6 g de motor):")
analiza("FINAL B - control por motores independientes", total - 3.3 + 1.6, 0.075, 0.030, 31, 180,
        CL=2.2, bateria_mah=300)
print("\n  Que pasa si se pasa de peso (margen critico 1.20):")
for extra in (2, 4, 6):
    m = total + extra
    L = 2*0.5*RHO*(2*math.radians(180)*31*0.075*R2_HAT)**2*(0.075*0.030)*2.2
    print(f"    {m:.1f} g -> margen {L/(m/1000*G):.2f}x", "OK" if L/(m/1000*G) >= 1.2 else "NO VUELA")
