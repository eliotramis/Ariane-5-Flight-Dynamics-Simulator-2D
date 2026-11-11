"""Ajuste le modèle sur les repères de vols réels (voir reference.py).

Les masses, Isp, poussées EPC/ESC et la séquence de vol sont fixées par les
sources (ariane5/vehicle.py). Ne sont ajustées que les grandeurs non publiées :
  - la loi de tangage (angles aux nœuds PITCH_T),
  - la FORME de la courbe de poussée des EAP (son impulsion totale reste celle
    des 240 t d'ergols, et le pic est borné par les 6 709 kN mesurés),
  - un facteur d'échelle global sur Cd(Mach).

Usage : python -m calibration.fit [--reprise] [--ecrire]
  --reprise : repart de la dernière solution (calibration/x_opt.npy)
  --ecrire  : écrit la solution dans ariane5/guidance.py, vehicle.py, constants.py
"""

import re
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from ariane5 import atmosphere as atm
from ariane5 import constants as c
from ariane5 import guidance as g
from ariane5 import vehicle as v
from ariane5.analysis import orbite_injection, pression_dynamique
from ariane5.constants import GAMMA_AIR, P_SOL, R_S_AIR
from ariane5.simulation import simuler
from calibration.reference import REF

RACINE = Path(__file__).resolve().parent.parent
FICHIER_X = RACINE / "calibration" / "x_opt.npy"

# Nœuds de la loi de tangage (s) : vertical jusqu'à 6 s (bascule à H0+12,7 s)
PITCH_T = np.array([0.0, 6.0, 20.0, 60.0, 135.2, 300.0, 522.7,
                    700.0, 900.0, 1100.0, 1300.0, 1500.0])
N_PITCH = len(PITCH_T) - 2
I_PITCH_EPC = list(PITCH_T[2:]).index(522.7)     # dernier nœud phase EPC
CD_REF = np.array(c.CD_DATA)
N_EAP = len(v.T_EAP_TEMPS) - 1                    # la poussée à 135 s reste nulle
I_CD = N_PITCH
I_EAP = N_PITCH + 1

X0 = np.concatenate([
    np.interp(PITCH_T[2:], g.PITCH_TEMPS, g.PITCH_ANGLES), [1.0], v._FORME_EAP[:-1],
])
LO = np.concatenate([[60.0, 30.0, 10.0, 5.0, -5.0], [-30.0] * (N_PITCH - 5), [0.5], [0.3] * N_EAP])
HI = np.concatenate([[90.0, 89.0, 80.0, 70.0, 60.0], [60.0] * (N_PITCH - 5), [2.0], [9.0] * N_EAP])


def courbe_eap(x):
    return v.normaliser_poussee_eap(np.concatenate([x[I_EAP:I_EAP + N_EAP], [0.0]]))


def appliquer(x):
    g.PITCH_TEMPS = PITCH_T
    g.PITCH_ANGLES = np.concatenate([[90.0, 90.0], x[:N_PITCH]])
    atm.CD_DATA = tuple(CD_REF * x[I_CD])
    v.T_EAP_FORCE = courbe_eap(x)


def _sommet(t, y, i):
    """Sommet continu (parabole) de y autour de l'indice i."""
    if i <= 0 or i >= len(y) - 1:
        return float(t[i]), float(y[i])
    c2, c1, c0 = np.polyfit(t[i - 1:i + 2] - t[i], y[i - 1:i + 2], 2)
    d = -c1 / (2 * c2) if c2 < 0 else 0.0
    return float(t[i] + d), float(c0 + c1 * d + c2 * d * d)


def metriques(x):
    """Simule et renvoie les grandeurs comparables aux repères."""
    appliquer(x)
    tr = simuler(t_final=1700.0, pas=0.5)
    t, h, V = tr.temps, tr.altitudes / 1e3, tr.vitesses_relatives
    a = np.sqrt(GAMMA_AIR * R_S_AIR * np.array([atm.atmosphere(z * 1e3)[1] for z in h]))
    mach = V / a

    def a_t(T, arr):
        return float(np.interp(T, t, arr))

    # Mach 1 : croisement interpolé
    i1 = int(np.argmax(mach >= 1)) if (mach >= 1).any() else len(t) - 1
    i0 = max(i1 - 1, 0)
    f = (1 - mach[i0]) / (mach[i1] - mach[i0]) if mach[i1] != mach[i0] else 0.0
    t_m1 = t[i0] + f * (t[i1] - t[i0])

    # Max-Q (phase EAP) : sommet interpolé
    q = pression_dynamique(tr)
    sel = np.where(t < 130.0)[0]
    t_q, q_max = _sommet(t, q, sel[int(np.argmax(q[sel]))])

    orb = orbite_injection(tr, v.MASSE_ORBITALE_FINALE)
    if orb is None:   # extinction non atteinte (impact) : pénalité continue
        esc_t, esc_alt, per, apo = t[-1], h[-1], -R_PEN, 0.0
    else:
        esc_t, esc_alt = orb.temps, orb.altitude / 1e3
        per, apo = orb.perigee / 1e3, min(orb.apogee / 1e3, 2e5)

    f_eap = v.T_EAP_FORCE
    return {
        "mach1_t": float(t_m1), "mach1_alt_km": a_t(t_m1, h),
        "maxq_t": t_q, "maxq_alt_km": a_t(t_q, h),
        "eap_alt_km": a_t(v.T_SEP_EAP, h), "eap_v": a_t(v.T_SEP_EAP, V),
        "coiffe_alt_km": a_t(v.T_COIFFE, h),
        "epc_alt_km": a_t(v.T_ARRET_EPC, h), "epc_v": a_t(v.T_ARRET_EPC, V),
        "esc_t": esc_t, "esc_alt_km": esc_alt,
        "perigee_km": per, "apogee_km": apo,
        "poussee_0_MN": (2 * (f_eap[0] - v.A_E_EAP * P_SOL)
                         + v.T_EPC_CONSTANTE - v.A_E_EPC * P_SOL) / 1e6,
        "_h_min_esc_km": float(h[(t >= v.T_ARRET_EPC) & (t <= esc_t)].min()),
        "_maxq_kpa": q_max / 1e3,
        "_f_eap_max_MN": float(f_eap.max()) / 1e6,
        "_orbite": orb,
    }


R_PEN = 2000.0   # périgée fictif (km) si l'orbite n'est pas atteinte


def residus(x):
    m = metriques(x)
    r = [(m[k] - REF[k][0]) / REF[k][1] for k in REF]
    # ESA : séparation EPC entre 160 et 210 km ; la combustion ESC fait
    # ensuite monter l'orbite (pas de « plongée » sous ~150 km)
    r.append(max(0.0, 160.0 - m["epc_alt_km"]) / 5.0)
    r.append(max(0.0, 150.0 - m["_h_min_esc_km"]) / 5.0)
    # Pic de poussée EAP borné par l'essai au banc (6 709 kN)
    r.append(max(0.0, m["_f_eap_max_MN"] - v.F_EAP_MAX / 1e6) / 0.05)
    # Cd proche du nominal ; courbe EAP lisse ; tangage décroissant jusqu'à
    # l'arrêt EPC (la phase ESC est libre)
    r.append((x[I_CD] - 1.0) / 0.3)
    r += list(np.diff(x[I_EAP:I_EAP + N_EAP]) / 1.5)
    r += [max(0.0, x[i + 1] - x[i]) / 2.0 for i in range(I_PITCH_EPC)]
    return np.array(r)


def tableau(x, titre):
    m = metriques(x)
    print(f"\n{titre}")
    print(f"{'repère':<15}{'réel':>10}{'modèle':>10}{'écart':>10}{'écart/σ':>9}")
    for k, (val, sig, _) in REF.items():
        print(f"{k:<15}{val:>10.1f}{m[k]:>10.1f}{m[k] - val:>+10.1f}{(m[k] - val) / sig:>+9.1f}")
    print(f"Max-Q : {m['_maxq_kpa']:.1f} kPa ; pic EAP : {m['_f_eap_max_MN']:.3f} MN ; "
          f"altitude min. phase ESC : {m['_h_min_esc_km']:.0f} km")
    return m


def ecrire_solution(x):
    """Reporte la solution dans le code du modèle."""
    ang = np.concatenate([[90.0, 90.0], x[:N_PITCH]])
    p = RACINE / "ariane5" / "guidance.py"
    s = p.read_text()
    s = re.sub(r"PITCH_TEMPS = np\.array\(\[.*?\]\)",
               "PITCH_TEMPS = np.array([%s])" % ", ".join(f"{t:g}" for t in PITCH_T), s, flags=re.S)
    s = re.sub(r"PITCH_ANGLES = np\.array\(\[.*?\]\)",
               "PITCH_ANGLES = np.array([%s])" % ", ".join(f"{a:.2f}" for a in ang), s, flags=re.S)
    p.write_text(s)

    p = RACINE / "ariane5" / "vehicle.py"
    s = p.read_text()
    forme = np.concatenate([x[I_EAP:I_EAP + N_EAP], [0.0]])
    s = re.sub(r"_FORME_EAP = np\.array\(\[.*?\]\)",
               "_FORME_EAP = np.array([%s])" % ", ".join(f"{f:.3f}" for f in forme), s, flags=re.S)
    p.write_text(s)

    p = RACINE / "ariane5" / "constants.py"
    s = p.read_text()
    cd = CD_REF * x[I_CD]
    s = re.sub(r"CD_DATA = \(.*?\)", "CD_DATA = (%s)" % ", ".join(f"{v_:.3f}" for v_ in cd), s, flags=re.S)
    p.write_text(s)
    print("Solution écrite dans ariane5/guidance.py, vehicle.py et constants.py")


if __name__ == "__main__":
    t0 = time.time()
    x_init = np.load(FICHIER_X) if "--reprise" in sys.argv else X0
    x_init = np.clip(x_init, LO + 1e-9, HI - 1e-9)
    tableau(x_init, "AVANT")
    sol = least_squares(residus, x_init, bounds=(LO, HI), diff_step=1e-3,
                        x_scale=np.maximum(np.abs(x_init), 1.0),
                        xtol=1e-10, ftol=1e-10, max_nfev=200, verbose=1)
    m = tableau(sol.x, "APRÈS calibration")
    np.save(FICHIER_X, sol.x)
    print("\nx_opt =", np.round(sol.x, 3).tolist(), f"({time.time() - t0:.0f} s)")
    if "--ecrire" in sys.argv:
        ecrire_solution(sol.x)
