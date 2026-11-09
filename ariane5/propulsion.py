"""Poussée et débit massique selon la phase de vol."""

from enum import IntEnum

import numpy as np

from . import vehicle as v
from .constants import G_0


class Phase(IntEnum):
    EAP_EPC = 1    # EPC + 2 EAP
    EPC = 2        # EPC seul
    ESC = 3        # Étage supérieur
    BALISTIQUE = 4 # Moteurs éteints


def poussee_et_debit(phase, t, p_ambiante):
    """Renvoie (poussée réelle en N, dm/dt en kg/s) pour la phase donnée.

    La poussée est corrigée de la pression ambiante pour l'EPC et les EAP
    (F = F_vide - A_e * P). Le débit est calculé à partir de la poussée
    dans le vide : dm/dt = -F_vide / (Isp * g0).
    """
    if phase == Phase.EAP_EPC:
        f_epc = v.T_EPC_CONSTANTE - v.A_E_EPC * p_ambiante
        dm_epc = -v.T_EPC_CONSTANTE / (v.ISP_EPC * G_0)

        f_eap_vide = float(np.interp(t, v.T_EAP_TEMPS, v.T_EAP_FORCE))
        f_eap = f_eap_vide - v.A_E_EAP * p_ambiante
        dm_eap = -f_eap_vide / (v.ISP_EAP * G_0)

        return f_epc + 2 * f_eap, dm_epc + 2 * dm_eap

    if phase == Phase.EPC:
        f = v.T_EPC_CONSTANTE - v.A_E_EPC * p_ambiante
        return f, -v.T_EPC_CONSTANTE / (v.ISP_EPC * G_0)

    if phase == Phase.ESC:
        return v.T_ESC, -v.T_ESC / (v.ISP_ESC * G_0)

    return 0.0, 0.0
