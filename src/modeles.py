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
class TypePanneau:
    id: int
    libelle: str
    ratio_couverture: float
    energie_unitaire_wh: float
    prix_unitaire: float


@dataclass(frozen=True)
class PropositionPanneau:
    id_type_panneau: int
    libelle_type: str
    ratio_couverture: float
    puissance_propose_w: float
    quantite_require: float
    prix_unitaire: float
    prix_total: float
    est_recommande: bool


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
    propositions_panneau: list['PropositionPanneau']
