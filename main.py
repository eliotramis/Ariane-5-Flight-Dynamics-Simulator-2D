"""Point d'entrée : simule le vol d'Ariane 5 et affiche les résultats."""

import matplotlib.pyplot as plt

from ariane5.analysis import calculer_max_q, pression_dynamique
from ariane5.plotting import afficher_rapport, tracer_profils, tracer_trajectoire
from ariane5.simulation import simuler


def main():
    traj = simuler(t_final=20_000.0, pas=0.1)
    q = pression_dynamique(traj)
    max_q = calculer_max_q(traj, q)

    afficher_rapport(traj, max_q)
    tracer_profils(traj, q, max_q)
    tracer_trajectoire(traj)
    plt.show()


if __name__ == "__main__":
    main()
