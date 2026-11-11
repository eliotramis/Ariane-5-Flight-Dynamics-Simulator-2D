"""Loi de guidage : angle de tangage par rapport à l'horizontale locale."""

import numpy as np

# Table (temps depuis le décollage en s, angle en °) interpolée linéairement.
# 90° = vertical, 0° = horizontale locale. Valeurs ajustées sur les vols réels
# (voir calibration/).
PITCH_TEMPS = np.array([0, 6, 20, 60, 135.2, 300, 522.7, 700, 900, 1100, 1300, 1500])
PITCH_ANGLES = np.array([90.00, 90.00, 77.35, 45.34, 31.81, 19.50, 4.56, -1.88, -4.36, 0.11, 5.08, 11.57])


def angle_tangage_deg(t):
    """Angle de poussée (°) par rapport à l'horizontale locale (90° = vertical)."""
    return float(np.interp(t, PITCH_TEMPS, PITCH_ANGLES))
