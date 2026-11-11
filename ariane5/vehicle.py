"""Paramètres du lanceur Ariane 5 ECA (masses, surfaces, propulsion).

Toutes les données d'entrée sont sourcées (voir README, section Calibration) ;
la masse au décollage, la masse larguée avec l'EPC et la masse finale en sont
déduites par bilan de masse au lieu d'être fixées à la main.

Les temps sont comptés depuis le DÉCOLLAGE, qui a lieu à H0 + 7,3 s
(H0 = allumage du Vulcain 2).
"""

import math

import numpy as np

from .constants import G_0

# - Séquence de vol (s depuis le décollage ; Spaceflight Now VA213/VA220,
#   Arianespace) -
T_PRE_DECOLLAGE = 7.3        # Vulcain 2 allumé 7,3 s avant le décollage
T_SEP_EAP = 135.2            # H0 + 142,5 s
T_COIFFE = 188.0             # H0 + 191 à 201 s
T_ARRET_EPC = 522.7          # H0 + 530 s : arrêt du Vulcain 2
T_SEP_EPC = 528.7            # H0 + 536 s : séparation EPC / composite supérieur
T_ALLUMAGE_ESC = 532.7       # H0 + 540 s : allumage du HM7B

# - EAP P241 (un booster) : Wikipédia (273 t dont 33 t à vide),
#   ESA bulletin 104 (essai : Isp vide 275,4 s, 129-130 s, poussée vide
#   max 6 709 kN, moyenne 4 984 kN) -
M_EAP_ERGOLS = 240_000.0
M_EAP_VIDE = 33_000.0
ISP_EAP = 275.4
D_SORTIE_EAP = 2.9           # Diamètre de sortie de tuyère (m), ESA : 3,1 m hors-tout
A_E_EAP = math.pi * D_SORTIE_EAP**2 / 4
F_EAP_MAX = 6_709_000.0      # Poussée vide maximale mesurée (N)

# Forme de la courbe de poussée vide (ajustée, voir calibration/) ; elle est
# renormalisée pour que l'impulsion totale corresponde exactement aux 240 t
# d'ergols : I = M_EAP_ERGOLS * ISP_EAP * G_0.
T_EAP_TEMPS = np.array([0.0, 15.0, 30.0, 50.0, 70.0, 90.0, 110.0, 130.0, 135.0])
_FORME_EAP = np.array([6.962, 6.961, 4.648, 5.652, 6.175, 4.648, 3.340, 2.924, 0.000])


def normaliser_poussee_eap(forme, temps=T_EAP_TEMPS):
    """Met une forme de courbe à l'échelle de l'impulsion totale réelle (N)."""
    forme = np.asarray(forme, dtype=float)
    impulsion = float(np.sum(0.5 * (forme[1:] + forme[:-1]) * np.diff(temps)))
    return forme * (M_EAP_ERGOLS * ISP_EAP * G_0 / impulsion)


T_EAP_FORCE = normaliser_poussee_eap(_FORME_EAP)

# - EPC H173 / Vulcain 2 : ESA bulletin 123 (188 t dont 173 t d'ergols) ;
#   Wikipédia Vulcain (1 359 kN vide, diamètre de sortie 2,09 m) ;
#   Isp 429 s et 323 kg/s (étude tuyère double galbe) -
M_EPC_ERGOLS = 173_000.0
M_EPC_VIDE = 15_000.0
T_EPC_CONSTANTE = 1_359_000.0    # Poussée dans le vide (N)
ISP_EPC = 429.0
D_SORTIE_EPC = 2.09
A_E_EPC = math.pi * D_SORTIE_EPC**2 / 4
DEBIT_EPC = T_EPC_CONSTANTE / (ISP_EPC * G_0)   # ~323 kg/s

# - ESC-A / HM7B : Wikipédia (4,54 t à vide, Isp 446 s), ESA (14,7 t
#   d'ergols, ~6,5 t de poussée). Poussée 64,8 kN : cohérente avec la
#   combustion de 16 min 27 s du vol VA230 (14,7 t / 987 s = 14,9 kg/s) -
M_ESC_ERGOLS = 14_700.0
M_ESC_VIDE = 4_540.0
T_ESC = 64_800.0
ISP_ESC = 446.0

# - Composite supérieur -
M_VEB = 1_370.0              # Case à équipements (ESA : 1 300 kg + 70 kg d'hydrazine)
M_COIFFE = 2_900.0           # Coiffe longue 17 m (capcomespace : 2,9 t)
# Charge utile de référence : vol VA230, EchoStar 18 + BRIsat (2016),
# SYLDA compris (Spaceflight Now : 10 731 kg)
M_PAYLOAD = 10_731.0

# - Bilan de masse (déduit) -
# Ergols EPC brûlés avant le décollage, puis restant à la séparation
_ERGOLS_EPC_AVANT_DECOLLAGE = DEBIT_EPC * T_PRE_DECOLLAGE
_ERGOLS_EPC_RESIDUELS = M_EPC_ERGOLS - DEBIT_EPC * (T_PRE_DECOLLAGE + T_ARRET_EPC)

M_EAP_SECHE = 2 * M_EAP_VIDE                         # Masse larguée avec les 2 EAP (kg)
M_EPC_SECHE = M_EPC_VIDE + _ERGOLS_EPC_RESIDUELS     # Masse larguée avec l'EPC (kg)
MASSE_ORBITALE_FINALE = M_PAYLOAD + M_VEB + M_ESC_VIDE   # Masse en fin de combustion (kg)

M_0 = (2 * (M_EAP_ERGOLS + M_EAP_VIDE) + M_EPC_ERGOLS + M_EPC_VIDE
       + M_ESC_ERGOLS + M_ESC_VIDE + M_VEB + M_COIFFE + M_PAYLOAD
       - _ERGOLS_EPC_AVANT_DECOLLAGE)                # Masse au décollage (kg)

# - Surfaces de référence -
D_EPC = 5.4                  # Diamètre de l'EPC (m)
S_EPC = math.pi * D_EPC**2 / 4
D_EAP = 3.05                 # Diamètre d'un EAP (m)
S_EAP = math.pi * D_EAP**2 / 4
S_PHASE_1 = S_EPC + 2 * S_EAP    # EPC + 2 EAP
S_APRES_EAP = S_EPC              # EPC seul (après largage des EAP)
