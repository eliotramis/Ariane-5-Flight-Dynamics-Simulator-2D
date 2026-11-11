"""Repères de vols réels d'Ariane 5 ECA pour la calibration.

Les temps sont comptés depuis le DÉCOLLAGE (H0 + 7,3 s : le décollage a lieu
7,3 s après l'allumage du Vulcain 2, et les timelines publiées sont en H0).
Les vitesses sont relatives au sol (celles de la télémétrie).

Chaque repère : (valeur, incertitude 1 sigma, source).
"""

REF = {
    # Spaceflight Now, timelines VA213 / VA220 : Mach 1 à H0+48 s, 6,64-6,90 km
    "mach1_t":       (41.0, 1.0, "SFN VA213/VA220 : H0+48 s"),
    "mach1_alt_km":  (6.8, 0.3, "SFN VA213/VA220 : 6,64-6,90 km"),
    # ESA (bulletin 123) : Max-Q à T+65 s, séparation EAP à T+140 s. Cette
    # dernière valant H0+142,5 s, le « T » de l'ESA est H0 : Max-Q au
    # décollage + 57,7 s. (Spaceflight101 VA240 : T+1:0x, cohérent.)
    "maxq_t":        (57.7, 4.0, "ESA bulletin 123 : H0+65 s"),
    # Pas de valeur publiée pour Ariane 5 : plage générique des lanceurs lourds
    "maxq_alt_km":   (12.5, 2.0, "plage générique 11-14 km (non spécifique)"),
    # Séparation EAP : H0+142-143 s, ~67-69 km, 2,01 km/s (VA220)
    "eap_alt_km":    (68.0, 1.5, "Spaceflight101 ~67 km, Arianespace ~69 km"),
    "eap_v":         (2010.0, 30.0, "SFN VA220 : 2,01 km/s"),
    # Coiffe : H0+191 s, ~107 km (Arianespace) ; H0+201 s, 111 km (VA220)
    "coiffe_alt_km": (109.0, 3.0, "Arianespace 107 km / SFN VA220 111 km"),
    # Arrêt EPC : H0+541 s, ~178 km (Arianespace GTO) ; ESA : 160-210 km
    "epc_alt_km":    (178.0, 20.0, "Arianespace 178 km, ESA 160-210 km"),
    # Arrêt EPC Herschel/Planck : 15 730 mph = 7,03 km/s (SFN). La valeur
    # VA229 (5 758 m/s) est écartée : incompatible avec l'énergie d'une GTO
    # pour un ESC de 14,7 t (voir README).
    "epc_v":         (7030.0, 300.0, "SFN Herschel/Planck : 15 730 mph"),
    # Vol de référence VA230 (EchoStar 18 + BRIsat, 10 731 kg) : combustion
    # ESC de 16 min 27 s après l'allumage à H0+540 s -> extinction ~1 520 s ;
    # orbite visée 250 x 35 766 km, i = 6° (Spaceflight Now)
    "esc_t":         (1519.7, 10.0, "SFN VA230 : ESC 987 s"),
    # Altitude d'extinction : profil GTO générique (H0+1487 s, ~640 km)
    "esc_alt_km":    (640.0, 60.0, "Arianespace : ~640 km (profil générique)"),
    "perigee_km":    (250.0, 15.0, "SFN VA230 / flyer Arianespace"),
    "apogee_km":     (35766.0, 600.0, "SFN VA230 (GTO standard : 35 943 km)"),
    # Poussée totale au décollage : ~1 340 t (Arianespace)
    "poussee_0_MN":  (13.14, 0.25, "Arianespace : 1 340 t"),
}
