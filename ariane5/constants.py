"""Constantes physiques et paramètres du modèle atmosphérique (ISA)."""

R_T = 6_378_000.0       # Rayon terrestre (m)
G_0 = 9.80665           # Gravité au niveau de la mer (m/s^2)
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
CD_DATA = (0.45, 0.45, 0.55, 0.75, 0.85, 0.80, 0.65, 0.50, 0.35, 0.25, 0.15, 0.10)
