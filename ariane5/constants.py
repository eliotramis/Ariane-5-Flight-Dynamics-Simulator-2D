"""Constantes physiques et paramètres du modèle atmosphérique (ISA)."""

import math

R_T = 6_378_000.0       # Rayon terrestre (m)
G_0 = 9.80665           # Pesanteur conventionnelle (Isp, modèle ISA) (m/s^2)
MU_TERRE = 3.986004418e14   # Paramètre gravitationnel terrestre (m^3/s^2)
OMEGA_T = 7.292115e-5     # Vitesse de rotation de la Terre (rad/s)
LATITUDE_KOUROU_DEG = 5.24   # Latitude du Centre Spatial Guyanais (°)
R_S_AIR = 287.058       # Constante spécifique de l'air sec (J/(kg.K))
GAMMA_AIR = 1.4         # Indice adiabatique de l'air

T_SOL = 288.15          # Température au niveau de la mer (K)
P_SOL = 101_325.0       # Pression au niveau de la mer (Pa)

# Altitudes géopotentielles des bases de couches ISA (m).
# La dernière valeur (84 852 m géopotentiels) correspond à 86 km géométriques.
H_BASES = (0.0, 11_000.0, 20_000.0, 32_000.0, 47_000.0, 51_000.0, 71_000.0, 84_852.0)
# Gradients thermiques de chaque couche (K/m)
L_GRAD = (-0.0065, 0.0, 0.001, 0.0028, 0.0, -0.0028, -0.002)

# Coefficient de traînée en fonction du nombre de Mach
MACH_DATA = (0.0, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 25.0)
CD_DATA = (0.339, 0.339, 0.415, 0.566, 0.640, 0.604, 0.490, 0.377, 0.264, 0.189, 0.113, 0.075)

# Le plan de vol (x, y) est assimilé au plan de la latitude de Kourou : la
# vitesse d'entraînement vaut OMEGA_EFF * r (~463 m/s au sol).
OMEGA_EFF = OMEGA_T * math.cos(math.radians(LATITUDE_KOUROU_DEG))
