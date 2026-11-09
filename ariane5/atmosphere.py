"""Modèle atmosphérique ISA (7 couches), vitesse du son, Mach et Cd."""

import numpy as np

from .constants import (
    CD_DATA, G_0, GAMMA_AIR, H_BASES, L_GRAD, MACH_DATA,
    P_SOL, R_S_AIR, R_T, T_SOL,
)


def _calculer_bases():
    """Température et pression à la base de chaque couche ISA."""
    t_bases = [T_SOL]
    p_bases = [P_SOL]
    for i in range(1, len(L_GRAD)):
        dh = H_BASES[i] - H_BASES[i - 1]
        grad = L_GRAD[i - 1]
        t_prev, p_prev = t_bases[-1], p_bases[-1]
        if grad != 0.0:
            t_next = t_prev + grad * dh
            p_next = p_prev * (t_next / t_prev) ** (-G_0 / (R_S_AIR * grad))
        else:
            t_next = t_prev
            p_next = p_prev * np.exp(-G_0 * dh / (R_S_AIR * t_prev))
        t_bases.append(t_next)
        p_bases.append(p_next)
    return tuple(t_bases), tuple(p_bases)


T_BASES, P_BASES = _calculer_bases()

# Température au sommet de la dernière couche (utilisée au-delà de la limite ISA)
_DH_DERNIERE = H_BASES[-1] - H_BASES[-2]
T_HAUT = T_BASES[-1] + L_GRAD[-1] * _DH_DERNIERE


def atmosphere(y):
    """Modèle ISA : renvoie (rho, T, P) à l'altitude géométrique y (m).

    Convertit y en altitude géopotentielle H. Au-delà de la dernière couche
    (~86 km), la densité et la pression sont considérées nulles.
    """
    if y < 0.0:
        return P_SOL / (R_S_AIR * T_SOL), T_SOL, P_SOL

    h = (R_T * y) / (R_T + y)

    if h >= H_BASES[-1]:
        return 0.0, T_HAUT, 0.0

    # Identification de la couche courante (0 à 6)
    couche = 0
    while couche < len(L_GRAD) - 1 and h >= H_BASES[couche + 1]:
        couche += 1

    t_b = T_BASES[couche]
    p_b = P_BASES[couche]
    grad = L_GRAD[couche]
    dh = h - H_BASES[couche]

    if grad != 0.0:
        # Gradient de température : T linéaire
        t = t_b + grad * dh
        p = p_b * (t / t_b) ** (-G_0 / (R_S_AIR * grad))
    else:
        # Couche isotherme : P exponentielle décroissante
        t = t_b
        p = p_b * np.exp(-G_0 * dh / (R_S_AIR * t_b))

    rho = p / (R_S_AIR * t)  # gaz parfait
    return rho, t, p


def vitesse_son(t):
    """Vitesse du son (m/s) à la température t (K)."""
    if t <= 0.0:
        return 0.0
    return float(np.sqrt(GAMMA_AIR * R_S_AIR * t))


def nombre_de_mach(t, v):
    """Nombre de Mach pour une température t (K) et une vitesse v (m/s)."""
    c = vitesse_son(t)
    if v <= 0.0 or c <= 0.0:
        return 0.0
    return v / c


def calculer_cd(t, v):
    """Coefficient de traînée interpolé en fonction du Mach."""
    return float(np.interp(nombre_de_mach(t, v), MACH_DATA, CD_DATA))
