"""Paramètres du lanceur Ariane 5 (masses, surfaces, propulsion)."""

import math

import numpy as np

# - Masses -
M_0 = 780_000.0              # Masse totale au décollage (kg)
M_PAYLOAD = 10_000.0         # Masse des satellites (kg)
M_ESC_VIDE = 4_500.0         # Masse de la structure de l'étage supérieur (kg)
MASSE_ORBITALE_FINALE = M_PAYLOAD + M_ESC_VIDE   # Masse en fin de combustion (kg)

M_EAP_SECHE = 76_000.0       # Masse larguée avec les 2 EAP (kg)
M_EPC_SECHE = 14_000.0       # Masse larguée avec l'EPC (kg)

# - Surfaces de référence -
D_EPC = 5.4                  # Diamètre de l'EPC (m)
S_EPC = math.pi * D_EPC**2 / 4
D_EAP = 3.05                 # Diamètre d'un EAP (m)
S_EAP = math.pi * D_EAP**2 / 4
S_PHASE_1 = S_EPC + 2 * S_EAP    # EPC + 2 EAP
S_APRES_EAP = S_EPC              # EPC seul (après largage des EAP)

# - EAP (un seul booster) -
T_EAP_TEMPS = np.array([0.0, 20.0, 50.0, 90.0, 130.0, 135.0])
T_EAP_FORCE = np.array([6_500_000.0, 7_000_000.0, 4_200_000.0, 6_000_000.0, 900_000.0, 0.0])
ISP_EAP = 275.0
A_E_EAP = 2.9                # Section de sortie de tuyère (m^2)

# - EPC -
T_EPC_CONSTANTE = 1_350_000.0    # Poussée dans le vide (N)
ISP_EPC = 432.0
A_E_EPC = 3.0

# - ESC -
T_ESC = 64_800.0
ISP_ESC = 446.0

# - Séquence de vol (s) -
T_SEP_EAP = 135.0
T_SEP_EPC = 540.0
