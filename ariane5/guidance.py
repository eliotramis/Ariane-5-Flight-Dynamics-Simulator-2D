"""Loi de guidage : angle de tangage par rapport à l'horizontale locale."""

import numpy as np

from .vehicle import T_SEP_EAP, T_SEP_EPC

T_DEBUT_BASCULE = 15.0       # Fin de la montée verticale (s)
T_FIN_PITCH = 1400.0         # Fin de la loi de tangage de l'ESC (s)


def angle_tangage_deg(t):
    """Angle de poussée (°) par rapport à l'horizontale locale (90° = vertical)."""
    if t < T_DEBUT_BASCULE:
        return 90.0
    if t <= T_SEP_EAP:
        # Phase EAP + EPC : 90° -> 50°
        return float(np.interp(t, [T_DEBUT_BASCULE, T_SEP_EAP], [90.0, 50.0]))
    if t <= T_SEP_EPC:
        # Phase EPC seul : 50° -> 35°
        return float(np.interp(t, [T_SEP_EAP, T_SEP_EPC], [50.0, 35.0]))
    # Phase ESC : 35° -> 0° (horizontale)
    return float(np.interp(t, [T_SEP_EPC, T_FIN_PITCH], [35.0, 0.0]))
