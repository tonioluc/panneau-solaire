from modeles import EntreeSimulation, ResultatSimulation, TrancheHoraire


class ServiceDimensionnement:
    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        text = hhmm.strip()
        parts = text.split(":")
        if len(parts) < 2:
            raise ValueError("Heure invalide. Format attendu HH:MM")
        h = int(parts[0])
        m = int(parts[1])
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError("Heure invalide. Utiliser HH:MM entre 00:00 et 23:59")
        return h * 60 + m

    @staticmethod
    def _expand_interval(start_min: int, end_min: int) -> list[tuple[int, int]]:
        if end_min > start_min:
            return [(start_min, end_min)]
        if end_min < start_min:
            return [(start_min, 1440), (0, end_min)]
        raise ValueError("Heure debut et heure fin ne peuvent pas etre identiques")

    def _split_minutes_by_tranche(
        self,
        usage_start: int,
        usage_end: int,
        tranches: list[TrancheHoraire],
    ) -> dict[str, float]:
        usage_segments = self._expand_interval(usage_start, usage_end)
        result: dict[str, float] = {tr.libelle.upper().strip(): 0.0 for tr in tranches}

        for tr in tranches:
            libelle = tr.libelle.upper().strip()
            tr_start = self._to_minutes(tr.heure_debut)
            tr_end = self._to_minutes(tr.heure_fin)
            tranche_segments = self._expand_interval(tr_start, tr_end)

            minutes = 0
            for us, ue in usage_segments:
                for ts, te in tranche_segments:
                    overlap_start = max(us, ts)
                    overlap_end = min(ue, te)
                    if overlap_end > overlap_start:
                        minutes += overlap_end - overlap_start
            result[libelle] = minutes / 60.0

        return result

    def calculer(
        self,
        entrees: list[EntreeSimulation],
        parametres: dict[str, float] | None = None,
        tranches: list[TrancheHoraire] | None = None,
    ) -> ResultatSimulation:
        if not entrees:
            raise ValueError("Aucune entree dans la simulation")

        if not tranches:
            raise ValueError("Aucune tranche horaire configuree")

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
            if entree.puissance_w <= 0:
                raise ValueError("La puissance doit etre > 0")

            start_min = self._to_minutes(entree.heure_debut)
            end_min = self._to_minutes(entree.heure_fin)
            usage_by_tranche = self._split_minutes_by_tranche(start_min, end_min, tranches)

            for tranche, duree_h in usage_by_tranche.items():
                if duree_h <= 0:
                    continue
                if tranche not in energie:
                    continue
                energie[tranche] += entree.puissance_w * duree_h
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
