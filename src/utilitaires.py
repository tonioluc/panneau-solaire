import math


def arrondir_superieur(valeur: float, pas: float) -> float:
    if pas <= 0:
        raise ValueError("Le pas d'arrondi doit etre strictement positif")
    if valeur <= 0:
        return 0.0
    return math.ceil(valeur / pas) * pas
