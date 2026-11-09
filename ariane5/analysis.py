"""Post-traitement : pression dynamique et Max-Q."""

from dataclasses import dataclass

import numpy as np

from .atmosphere import atmosphere
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
    """q = 1/2 * rho * v^2 le long de la trajectoire (Pa)."""
    densites = np.array([atmosphere(h)[0] for h in traj.altitudes])
    return 0.5 * densites * traj.vitesses**2


def calculer_max_q(traj: Trajectoire, q=None):
    if q is None:
        q = pression_dynamique(traj)
    indices = np.where(traj.temps < T_MAX_RECHERCHE_MAXQ)[0]
    i = indices[np.argmax(q[indices])]
    return MaxQ(
        valeur=float(q[i]), temps=float(traj.temps[i]),
        altitude=float(traj.altitudes[i]), vitesse=float(traj.vitesses[i]),
        position=float(traj.x[i]),
    )
