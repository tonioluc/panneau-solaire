from dataclasses import dataclass


@dataclass(frozen=True)
class Simulation:
    id: int
    titre: str
    notes: str


@dataclass(frozen=True)
class EntreeSimulation:
    id: int
    simulation_id: int
    materiel: str
    puissance_w: float
    heure_debut: str
    heure_fin: str


@dataclass(frozen=True)
class TrancheHoraire:
    id: int
    libelle: str
    heure_debut: str
    heure_fin: str


@dataclass(frozen=True)
class ResultatSimulation:
    energie_matin_wh: float
    energie_soir_wh: float
    energie_nuit_wh: float
    puissance_matin_w: float
    puissance_soir_w: float
    puissance_nuit_w: float
    batterie_theorique_wh: float
    puissance_charge_batterie_w: float
    panneau_matin_theorique_w: float
    panneau_soir_theorique_w: float
    panneau_theorique_w: float
    panneau_pratique_achat_w: float
    batterie_pratique_achat_wh: float
    convertisseur_propose_w: float
    panneau_proposition_40_w: float
    panneau_proposition_30_w: float
