"""Rapport de vol et graphiques."""

import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from .analysis import MaxQ, Orbite
from .constants import R_T
from .simulation import Trajectoire

T_AFFICHAGE_MAX = 1700.0     # Phase propulsée (extinction ESC ~1 525 s)


def afficher_rapport(traj: Trajectoire, max_q: MaxQ, orbite: Optional[Orbite] = None):
    print("=== RAPPORT DE VOL ===")
    print(f"Altitude maximale simulée : {np.max(traj.altitudes) / 1000:.2f} km")
    print(f"Max-Q : {max_q.valeur:.2f} Pascals")
    print(f" - Survenu à t = {max_q.temps:.2f} s")
    print(f" - Altitude = {max_q.altitude / 1000:.2f} km")
    print(f" - Vitesse = {max_q.vitesse:.2f} m/s")
    if orbite is None:
        print("Extinction ESC : non atteinte")
        return
    print(f"Extinction ESC à t = {orbite.temps:.0f} s, altitude {orbite.altitude / 1000:.0f} km")
    print(f" - Vitesse inertielle = {orbite.vitesse_inertielle:.0f} m/s "
          f"(relative {orbite.vitesse_relative:.0f} m/s), pente {orbite.pente:.1f}°")
    print(f" - Orbite : périgée {orbite.perigee / 1000:.0f} km, apogée {orbite.apogee / 1000:.0f} km")


def tracer_profils(traj: Trajectoire, q, max_q: MaxQ):
    """Altitude, vitesse et pression dynamique en fonction du temps."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    vu = traj.temps <= T_AFFICHAGE_MAX

    axes[0].plot(traj.temps[vu], traj.altitudes[vu] / 1000.0, "b-", linewidth=2, label="Altitude (km)")
    axes[0].axvline(x=max_q.temps, color="r", linestyle="--", alpha=0.5)
    axes[0].set_ylabel("Altitude [km]")
    axes[0].set_title("Relevé de Vol (Modèle 2D, pitch angle non constant)")

    axes[1].plot(traj.temps[vu], traj.vitesses_relatives[vu], "g-", linewidth=2,
                 label="Vitesse relative sol (m/s)")
    axes[1].axvline(x=max_q.temps, color="r", linestyle="--", alpha=0.5)
    axes[1].set_ylabel("Vitesse [m/s]")

    axes[2].plot(traj.temps[vu], q[vu], "r-", linewidth=2, label="Pression Dynamique $q$ (Pa)")
    axes[2].plot(max_q.temps, max_q.valeur, "ko")
    axes[2].annotate(
        f"Max-Q: {max_q.valeur:.0f} Pa\n@ {max_q.altitude / 1000:.1f} km",
        xy=(max_q.temps, max_q.valeur),
        xytext=(max_q.temps + 10, max_q.valeur * 0.8),
    )
    axes[2].set_ylim(0, max_q.valeur * 1.2)
    axes[2].set_ylabel("Pression $q$ [Pa]")
    axes[2].set_xlabel("Temps [s]")

    for ax in axes:
        ax.set_xlim(0, T_AFFICHAGE_MAX)
        ax.grid(True, linestyle=":")
        ax.legend()
    return fig


def tracer_trajectoire(traj: Trajectoire):
    """Trajectoire de la fusée autour de la Terre."""
    fig, ax = plt.subplots()
    angles = np.linspace(0, 2 * math.pi, 500)

    ax.plot(R_T * np.cos(angles) / 1000.0, (R_T * np.sin(angles) - R_T) / 1000.0,
            "g-", linewidth=2, label="Terre (Rayon 6378 km)")
    r_atm = R_T + 100_000.0
    ax.plot(r_atm * np.cos(angles) / 1000.0, (r_atm * np.sin(angles) - R_T) / 1000.0,
            "c--", linewidth=1, alpha=0.5, label="Atmosphère (100 km)")
    ax.plot(traj.x / 1000.0, traj.y / 1000.0, "b-", linewidth=1, label="Trajectoire Fusée")

    # Cadrage sur la Terre et toute la trajectoire (l'origine y=0 est au
    # sommet du globe, à Kourou)
    xs = np.concatenate([traj.x / 1000.0, [-R_T / 1000.0, R_T / 1000.0]])
    ys = np.concatenate([traj.y / 1000.0, [0.0, -2 * R_T / 1000.0]])
    marge = 0.05 * max(np.ptp(xs), np.ptp(ys))
    ax.set_aspect("equal")
    ax.set_xlim(xs.min() - marge, xs.max() + marge)
    ax.set_ylim(ys.min() - marge, ys.max() + marge)
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.grid(True, linestyle=":")
    ax.legend(loc="upper right")
    return fig
