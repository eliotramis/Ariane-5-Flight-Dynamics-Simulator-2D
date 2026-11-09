"""Intégration numérique de la trajectoire phase par phase."""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from . import vehicle as v
from .constants import R_T
from .dynamics import altitude, dynamique_fusee
from .propulsion import Phase

RTOL = 1e-8
ATOL = 1e-6


@dataclass
class Trajectoire:
    """Historique de la simulation (échantillonné à pas fixe par phase)."""

    temps: np.ndarray
    x: np.ndarray
    y: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    masse: np.ndarray

    @property
    def altitudes(self):
        return np.sqrt(self.x**2 + (self.y + R_T) ** 2) - R_T

    @property
    def vitesses(self):
        return np.hypot(self.vx, self.vy)


def _evt_impact_sol(t, state, phase):
    return altitude(state[0], state[1])


_evt_impact_sol.terminal = True
_evt_impact_sol.direction = -1       # seulement en descendant


def _evt_fin_combustion(t, state, phase):
    return state[4] - v.MASSE_ORBITALE_FINALE


_evt_fin_combustion.terminal = True
_evt_fin_combustion.direction = -1


def _integrer(phase, t0, t1, etat0, pas, events):
    n = max(int(round((t1 - t0) / pas)) + 1, 2)
    return solve_ivp(
        fun=dynamique_fusee, t_span=(t0, t1), y0=etat0,
        t_eval=np.linspace(t0, t1, n), events=events, args=(phase,),
        method="RK45", rtol=RTOL, atol=ATOL,
    )


def _evenement_declenche(sol, events, evenement):
    return len(sol.t_events[events.index(evenement)]) > 0


def simuler(t_final=20_000.0, pas=0.1):
    """Simule le vol complet et renvoie une `Trajectoire`.

    Phases : EAP+EPC -> EPC -> ESC (jusqu'à épuisement) -> vol balistique.
    La simulation s'arrête dès qu'un impact au sol est détecté.
    """
    etat = [0.0, 0.0, 0.0, 0.0, v.M_0]
    segments = []

    plan = [
        # (phase, t_début, t_fin, événements, masse larguée en fin de phase)
        (Phase.EAP_EPC, 0.0, v.T_SEP_EAP, [_evt_impact_sol], v.M_EAP_SECHE),
        (Phase.EPC, v.T_SEP_EAP, v.T_SEP_EPC, [_evt_impact_sol], v.M_EPC_SECHE),
        (Phase.ESC, v.T_SEP_EPC, t_final, [_evt_fin_combustion, _evt_impact_sol], 0.0),
    ]

    for phase, t0, t1, events, masse_larguee in plan:
        sol = _integrer(phase, t0, t1, etat, pas, events)
        segments.append(sol)
        if _evenement_declenche(sol, events, _evt_impact_sol):
            return _assembler(segments)
        etat = list(sol.y[:, -1])
        etat[4] -= masse_larguee

    # Vol balistique après extinction de l'ESC
    if _evenement_declenche(segments[-1], plan[-1][3], _evt_fin_combustion):
        t_extinction = segments[-1].t[-1]
        if t_extinction < t_final:
            segments.append(
                _integrer(Phase.BALISTIQUE, t_extinction, t_final, etat, pas, [_evt_impact_sol])
            )

    return _assembler(segments)


def _assembler(segments):
    return Trajectoire(
        temps=np.concatenate([s.t for s in segments]),
        x=np.concatenate([s.y[0] for s in segments]),
        y=np.concatenate([s.y[1] for s in segments]),
        vx=np.concatenate([s.y[2] for s in segments]),
        vy=np.concatenate([s.y[3] for s in segments]),
        masse=np.concatenate([s.y[4] for s in segments]),
    )
