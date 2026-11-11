"""Second membre des équations du mouvement (repère géocentrique 2D)."""

import math

from . import vehicle as v
from .atmosphere import atmosphere, calculer_cd
from .constants import MU_TERRE, OMEGA_EFF, R_T
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
    return MU_TERRE / r**2   # ~9,798 m/s^2 au sol (et non G_0 = 9,80665)


def vitesse_atmosphere(x, y):
    """Vitesse d'entraînement de l'atmosphère (rotation de la Terre), vers l'est."""
    return OMEGA_EFF * (y + R_T), -OMEGA_EFF * x


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
    # Calculée avec la vitesse relative à l'atmosphère (qui tourne avec la Terre)
    d_x = d_y = 0.0
    w_x, w_y = vitesse_atmosphere(x, y)
    vr_x, vr_y = vx - w_x, vy - w_y
    v_norme = math.hypot(vr_x, vr_y)
    if v_norme > 1.0 and rho > 0.0:
        c_d = calculer_cd(temp, v_norme)
        d_norme = 0.5 * rho * v_norme**2 * c_d * surface_reference(phase)
        d_x = -d_norme * vr_x / v_norme
        d_y = -d_norme * vr_y / v_norme

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
