"""Post-traitement : pression dynamique, Max-Q et orbite d'injection."""

import math
from dataclasses import dataclass

import numpy as np

from .atmosphere import atmosphere
from .constants import MU_TERRE, R_T
from .simulation import Trajectoire

T_MAX_RECHERCHE_MAXQ = 130.0   # Le Max-Q est cherché pendant la phase EAP (s)


@dataclass
class MaxQ:
    valeur: float      # Pa
    temps: float       # s
    altitude: float    # m
    vitesse: float     # m/s
    position: float    # m


def pression_dynamique(traj: Trajectoire):
    """q = 1/2 * rho * v^2 (v relative à l'atmosphère) le long de la trajectoire (Pa)."""
    densites = np.array([atmosphere(h)[0] for h in traj.altitudes])
    return 0.5 * densites * traj.vitesses_relatives**2


def calculer_max_q(traj: Trajectoire, q=None):
    if q is None:
        q = pression_dynamique(traj)
    indices = np.where(traj.temps < T_MAX_RECHERCHE_MAXQ)[0]
    i = indices[np.argmax(q[indices])]
    return MaxQ(
        valeur=float(q[i]), temps=float(traj.temps[i]),
        altitude=float(traj.altitudes[i]), vitesse=float(traj.vitesses_relatives[i]),
        position=float(traj.x[i]),
    )



@dataclass
class Orbite:
    temps: float             # instant de l'extinction ESC (s)
    altitude: float          # altitude à l'extinction (m)
    vitesse_inertielle: float
    vitesse_relative: float
    pente: float             # angle de pente de vol inertiel (°)
    perigee: float           # altitude du périgée (m)
    apogee: float            # altitude de l'apogée (m)


def orbite_injection(traj: Trajectoire, masse_finale: float):
    """Orbite osculatrice à l'extinction de l'ESC (None si jamais atteinte).

    Le solveur arrête la combustion à quelques kg près de la masse finale :
    on vérifie que la combustion est terminée (tolérance de 50 kg), puis on
    lit l'état au premier instant où la masse atteint son minimum, qui est
    l'instant exact de l'extinction.
    """
    if traj.masse.min() > masse_finale + 50.0:
        return None
    i = int(np.argmax(traj.masse <= traj.masse.min() + 0.5))
    rx, ry = traj.x[i], traj.y[i] + R_T
    vx, vy = traj.vx[i], traj.vy[i]
    r = math.hypot(rx, ry)
    v = math.hypot(vx, vy)
    energie = v**2 / 2 - MU_TERRE / r
    h = rx * vy - ry * vx
    e = math.sqrt(max(1 + 2 * energie * h**2 / MU_TERRE**2, 0.0))
    p = h**2 / MU_TERRE
    v_radiale = (rx * vx + ry * vy) / r
    return Orbite(
        temps=float(traj.temps[i]), altitude=r - R_T, vitesse_inertielle=v,
        vitesse_relative=float(traj.vitesses_relatives[i]),
        pente=math.degrees(math.asin(max(-1.0, min(1.0, v_radiale / v)))),
        perigee=p / (1 + e) - R_T,
        apogee=(p / (1 - e) - R_T) if e < 1 else math.inf,
    )
