"""Rapport de vol et graphiques."""

import math

import matplotlib.pyplot as plt
import numpy as np

from .analysis import MaxQ
from .constants import R_T
from .simulation import Trajectoire

T_AFFICHAGE_MAX = 2500.0


def afficher_rapport(traj: Trajectoire, max_q: MaxQ):
    print("=== RAPPORT DE VOL ===")
    print(f"Apogée atteint : {np.max(traj.altitudes) / 1000:.2f} km")
    print(f"Max-Q : {max_q.valeur:.2f} Pascals")
    print(f" - Survenu à t = {max_q.temps:.2f} s")
    print(f" - Altitude = {max_q.altitude / 1000:.2f} km")
    print(f" - Vitesse = {max_q.vitesse:.2f} m/s")


def tracer_profils(traj: Trajectoire, q, max_q: MaxQ):
    """Altitude, vitesse et pression dynamique en fonction du temps."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    axes[0].plot(traj.temps, traj.altitudes / 1000.0, "b-", linewidth=2, label="Altitude (km)")
    axes[0].axvline(x=max_q.temps, color="r", linestyle="--", alpha=0.5)
    axes[0].set_ylabel("Altitude [km]")
    axes[0].set_title("Relevé de Vol (Modèle 2D, pitch angle non constant)")

    axes[1].plot(traj.temps, traj.vitesses, "g-", linewidth=2, label="Vitesse (m/s)")
    axes[1].axvline(x=max_q.temps, color="r", linestyle="--", alpha=0.5)
    axes[1].set_ylabel("Vitesse [m/s]")

    axes[2].plot(traj.temps, q, "r-", linewidth=2, label="Pression Dynamique $q$ (Pa)")
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

    ax.set_aspect("equal")
    ax.set_xlim(-8000, 8000)
    ax.set_ylim(-18000, 10000)   # L'origine (y=0) est au sommet du globe
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.grid(True, linestyle=":")
    ax.legend(loc="upper right")
    return fig
