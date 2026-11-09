"""Second membre des équations du mouvement (repère géocentrique 2D)."""

import math

from . import vehicle as v
from .atmosphere import atmosphere, calculer_cd
from .constants import G_0, R_T
from .guidance import angle_tangage_deg
from .propulsion import Phase, poussee_et_debit


def distance_radiale(x, y):
    """Distance au centre de la Terre (m)."""
    return math.hypot(x, y + R_T)


def altitude(x, y):
    """Altitude au-dessus de la Terre sphérique (m)."""
    return distance_radiale(x, y) - R_T


def gravite_norme(r):
    """Norme de l'accélération de la pesanteur à la distance r (m/s^2)."""
    if r <= 0.0:
        return 0.0
    return G_0 * (R_T / r) ** 2


def surface_reference(phase):
    """Surface de référence aérodynamique selon la configuration du lanceur."""
    return v.S_PHASE_1 if phase == Phase.EAP_EPC else v.S_APRES_EAP


def dynamique_fusee(t, state, phase):
    """Dérivée du vecteur d'état [x, y, vx, vy, m] pour la phase donnée.

    La phase est passée explicitement (et non déduite de t) pour éviter les
    ambiguïtés aux instants de séparation.
    """
    x, y, vx, vy, m = state

    r = distance_radiale(x, y)
    alt = r - R_T
    g_r = gravite_norme(r)
    rho, temp, pression = atmosphere(alt)

    # - Poids -
    p_x = -m * g_r * x / r
    p_y = -m * g_r * (y + R_T) / r

    # - Traînée -
    d_x = d_y = 0.0
    v_norme = math.hypot(vx, vy)
    if v_norme > 1.0 and rho > 0.0:
        c_d = calculer_cd(temp, v_norme)
        d_norme = 0.5 * rho * v_norme**2 * c_d * surface_reference(phase)
        d_x = -d_norme * vx / v_norme
        d_y = -d_norme * vy / v_norme

    # - Poussée -
    f_t, dm_dt = poussee_et_debit(phase, t, pression)
    t_x = t_y = 0.0
    if f_t > 0.0:
        # Horizontale locale + consigne de tangage
        theta = math.atan2(y + R_T, x) - math.pi / 2 + math.radians(angle_tangage_deg(t))
        t_x = f_t * math.cos(theta)
        t_y = f_t * math.sin(theta)

    ax = (p_x + t_x + d_x) / m
    ay = (p_y + t_y + d_y) / m

    return [vx, vy, ax, ay, dm_dt]
