from modeles import EntreeSimulation, ResultatSimulation


class ServiceDimensionnement:
    def calculer(
        self,
        entrees: list[EntreeSimulation],
        parametres: dict[str, float] | None = None,
    ) -> ResultatSimulation:
        if not entrees:
            raise ValueError("Aucune entree dans la simulation")

        p = {
            "FACTEUR_PANNEAU_PRATIQUE": 0.4,
            "FACTEUR_PANNEAU_SOIR": 0.5,
            "FACTEUR_MARGE_BATTERIE": 1.5,
            "DUREE_MATIN_H": 11.0,
            "RATIO_COUVERTURE_PANNEAU_40": 0.4,
            "RATIO_COUVERTURE_PANNEAU_30": 0.3,
        }
        if parametres:
            p.update(parametres)

        energie = {"MATIN": 0.0, "SOIR": 0.0, "NUIT": 0.0}
        puissance = {"MATIN": 0.0, "SOIR": 0.0, "NUIT": 0.0}

        for entree in entrees:
            tranche = entree.tranche.upper().strip()
            if tranche not in energie:
                raise ValueError("Tranche invalide. Utiliser MATIN, SOIR ou NUIT")
            if entree.puissance_w <= 0 or entree.duree_h <= 0:
                raise ValueError("La puissance et la duree doivent etre > 0")

            energie[tranche] += entree.puissance_w * entree.duree_h
            puissance[tranche] += entree.puissance_w

        batterie_theorique_wh = energie["NUIT"]
        duree_matin_h = p["DUREE_MATIN_H"]
        facteur_soir = p["FACTEUR_PANNEAU_SOIR"]
        facteur_panneau_pratique = p["FACTEUR_PANNEAU_PRATIQUE"]
        facteur_marge_batterie = p["FACTEUR_MARGE_BATTERIE"]
        ratio_couverture_40 = p["RATIO_COUVERTURE_PANNEAU_40"]
        ratio_couverture_30 = p["RATIO_COUVERTURE_PANNEAU_30"]

        if (
            duree_matin_h <= 0
            or facteur_soir <= 0
            or facteur_panneau_pratique <= 0
            or facteur_marge_batterie <= 0
            or ratio_couverture_40 <= 0
            or ratio_couverture_30 <= 0
        ):
            raise ValueError("Parametres invalides dans la table parametre")

        puissance_charge_batterie_w = batterie_theorique_wh / duree_matin_h if batterie_theorique_wh > 0 else 0.0

        panneau_matin_theorique_w = puissance["MATIN"] + puissance_charge_batterie_w
        panneau_soir_theorique_w = puissance["SOIR"] / facteur_soir if puissance["SOIR"] > 0 else 0.0
        panneau_theorique_w = max(panneau_matin_theorique_w, panneau_soir_theorique_w)

        panneau_pratique_achat_w = panneau_theorique_w / facteur_panneau_pratique
        batterie_pratique_achat_wh = batterie_theorique_wh * facteur_marge_batterie
        panneau_proposition_40_w = panneau_theorique_w / ratio_couverture_40
        panneau_proposition_30_w = panneau_theorique_w / ratio_couverture_30

        return ResultatSimulation(
            energie_matin_wh=energie["MATIN"],
            energie_soir_wh=energie["SOIR"],
            energie_nuit_wh=energie["NUIT"],
            puissance_matin_w=puissance["MATIN"],
            puissance_soir_w=puissance["SOIR"],
            puissance_nuit_w=puissance["NUIT"],
            batterie_theorique_wh=batterie_theorique_wh,
            puissance_charge_batterie_w=puissance_charge_batterie_w,
            panneau_matin_theorique_w=panneau_matin_theorique_w,
            panneau_soir_theorique_w=panneau_soir_theorique_w,
            panneau_theorique_w=panneau_theorique_w,
            panneau_pratique_achat_w=panneau_pratique_achat_w,
            batterie_pratique_achat_wh=batterie_pratique_achat_wh,
            panneau_proposition_40_w=panneau_proposition_40_w,
            panneau_proposition_30_w=panneau_proposition_30_w,
        )
