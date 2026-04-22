from dataclasses import replace
from math import ceil

from modeles import EntreeSimulation, PropositionPanneau, ResultatSimulation, TrancheHoraire, TypePanneau


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

    def _duree_tranche_h(self, tranches: list[TrancheHoraire], libelle: str) -> float:
        cible = libelle.upper().strip()
        for tr in tranches:
            if tr.libelle.upper().strip() != cible:
                continue
            tr_start = self._to_minutes(tr.heure_debut)
            tr_end = self._to_minutes(tr.heure_fin)
            segments = self._expand_interval(tr_start, tr_end)
            return sum(te - ts for ts, te in segments) / 60.0
        return 0.0

    def _intervalle_tranche(self, tranches: list[TrancheHoraire], libelle: str) -> tuple[int, int] | None:
        cible = libelle.upper().strip()
        for tr in tranches:
            if tr.libelle.upper().strip() == cible:
                return (self._to_minutes(tr.heure_debut), self._to_minutes(tr.heure_fin))
        return None

    def _duree_chevauchement_h(
        self,
        start_a: int,
        end_a: int,
        start_b: int,
        end_b: int,
    ) -> float:
        segments_a = self._expand_interval(start_a, end_a)
        segments_b = self._expand_interval(start_b, end_b)

        minutes = 0
        for sa, ea in segments_a:
            for sb, eb in segments_b:
                overlap_start = max(sa, sb)
                overlap_end = min(ea, eb)
                if overlap_end > overlap_start:
                    minutes += overlap_end - overlap_start
        return minutes / 60.0

    def _energie_majoree_equivalente_wh(
        self,
        tranches: list[TrancheHoraire],
        energie_matin_wh: float,
        energie_soir_wh: float,
        majorations: list[tuple[str, str, float]] | None,
    ) -> float:
        if not majorations:
            return 0.0

        intervalle_matin = self._intervalle_tranche(tranches, "MATIN")
        intervalle_soir = self._intervalle_tranche(tranches, "SOIR")
        duree_matin_h = self._duree_tranche_h(tranches, "MATIN")
        duree_soir_h = self._duree_tranche_h(tranches, "SOIR")

        equivalent_wh = 0.0
        for heure_debut, heure_fin, taux_majoration in majorations:
            taux = float(taux_majoration) / 100.0
            if taux <= 0:
                continue

            slot_start = self._to_minutes(heure_debut)
            slot_end = self._to_minutes(heure_fin)

            if intervalle_matin and duree_matin_h > 0 and energie_matin_wh > 0:
                chevauchement_matin_h = self._duree_chevauchement_h(
                    intervalle_matin[0],
                    intervalle_matin[1],
                    slot_start,
                    slot_end,
                )
                if chevauchement_matin_h > 0:
                    equivalent_wh += energie_matin_wh * (chevauchement_matin_h / duree_matin_h) * taux

            if intervalle_soir and duree_soir_h > 0 and energie_soir_wh > 0:
                chevauchement_soir_h = self._duree_chevauchement_h(
                    intervalle_soir[0],
                    intervalle_soir[1],
                    slot_start,
                    slot_end,
                )
                if chevauchement_soir_h > 0:
                    equivalent_wh += energie_soir_wh * (chevauchement_soir_h / duree_soir_h) * taux

        return equivalent_wh

    def calculer(
        self,
        entrees: list[EntreeSimulation],
        parametres: dict[str, float] | None = None,
        tranches: list[TrancheHoraire] | None = None,
        types_panneau: list[TypePanneau] | None = None,
        prix_energie_non_utilisee: dict[int, dict[str, float]] | None = None,
        majorations_heure_pointe: dict[str, list[tuple[str, str, float]]] | None = None,
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
        prix_unitaire_ouvrable_ar_wh = 0.0
        prix_unitaire_weekend_ar_wh = 0.0

        if (
            duree_matin_h <= 0
            or facteur_soir <= 0
            or facteur_panneau_pratique <= 0
            or facteur_marge_batterie <= 0
            or ratio_couverture_40 <= 0
            or ratio_couverture_30 <= 0
        ):
            raise ValueError("Parametres ou tarifs invalides en base de donnees")

        puissance_charge_batterie_w = batterie_theorique_wh / duree_matin_h if batterie_theorique_wh > 0 else 0.0

        panneau_matin_theorique_w = puissance["MATIN"] + puissance_charge_batterie_w
        panneau_soir_theorique_w = puissance["SOIR"] / facteur_soir if puissance["SOIR"] > 0 else 0.0
        panneau_theorique_w = max(panneau_matin_theorique_w, panneau_soir_theorique_w)

        panneau_pratique_achat_w = panneau_theorique_w / facteur_panneau_pratique
        batterie_pratique_achat_wh = batterie_theorique_wh * facteur_marge_batterie
        pic_global_w = max(puissance["MATIN"] + puissance_charge_batterie_w, puissance["SOIR"])
        convertisseur_propose_w = pic_global_w * 2

        duree_soir_h = self._duree_tranche_h(tranches, "SOIR")

        energie_disponible_matin_wh = panneau_theorique_w * duree_matin_h
        energie_utilisee_matin_wh = energie["MATIN"] + batterie_theorique_wh
        energie_non_utilisee_matin_wh = max(0.0, energie_disponible_matin_wh - energie_utilisee_matin_wh)

        energie_disponible_soir_wh = panneau_theorique_w * facteur_soir * duree_soir_h
        energie_non_utilisee_soir_wh = max(0.0, energie_disponible_soir_wh - energie["SOIR"])

        energie_non_utilisee_totale_wh = energie_non_utilisee_matin_wh + energie_non_utilisee_soir_wh
        prix_total_ouvrable_ar = 0.0
        prix_total_weekend_ar = 0.0

        propositions_panneau: list[PropositionPanneau] = []
        if types_panneau:
            propositions_temporaires = []
            for type_p in types_panneau:
                quantite = ceil(panneau_theorique_w / (type_p.ratio_couverture * type_p.energie_unitaire_wh))
                puissance_installee_equivalente_w = quantite * type_p.ratio_couverture * type_p.energie_unitaire_wh

                tarif_type = {"OUVRABLE": 0.0, "WEEKEND": 0.0}
                if prix_energie_non_utilisee and type_p.id in prix_energie_non_utilisee:
                    for code_jour, prix_wh in prix_energie_non_utilisee[type_p.id].items():
                        tarif_type[str(code_jour).upper().strip()] = float(prix_wh)

                if tarif_type["OUVRABLE"] < 0 or tarif_type["WEEKEND"] < 0:
                    raise ValueError("Tarifs invalides pour le type de panneau " + type_p.libelle)

                energie_disponible_matin_type_wh = puissance_installee_equivalente_w * duree_matin_h
                energie_utilisee_matin_type_wh = energie["MATIN"] + batterie_theorique_wh
                energie_non_utilisee_matin_type_wh = max(0.0, energie_disponible_matin_type_wh - energie_utilisee_matin_type_wh)

                energie_disponible_soir_type_wh = puissance_installee_equivalente_w * facteur_soir * duree_soir_h
                energie_non_utilisee_soir_type_wh = max(0.0, energie_disponible_soir_type_wh - energie["SOIR"])
                energie_non_utilisee_totale_type_wh = energie_non_utilisee_matin_type_wh + energie_non_utilisee_soir_type_wh

                majorations_ouvrable = (
                    majorations_heure_pointe.get("OUVRABLE", [])
                    if majorations_heure_pointe
                    else []
                )
                majorations_weekend = (
                    majorations_heure_pointe.get("WEEKEND", [])
                    if majorations_heure_pointe
                    else []
                )
                energie_majoree_ouvrable_wh = self._energie_majoree_equivalente_wh(
                    tranches,
                    energie_non_utilisee_matin_type_wh,
                    energie_non_utilisee_soir_type_wh,
                    majorations_ouvrable,
                )
                energie_majoree_weekend_wh = self._energie_majoree_equivalente_wh(
                    tranches,
                    energie_non_utilisee_matin_type_wh,
                    energie_non_utilisee_soir_type_wh,
                    majorations_weekend,
                )

                prix_total = quantite * type_p.prix_unitaire
                prix_total_ouvrable_type = (energie_non_utilisee_totale_type_wh + energie_majoree_ouvrable_wh) * tarif_type["OUVRABLE"]
                prix_total_weekend_type = (energie_non_utilisee_totale_type_wh + energie_majoree_weekend_wh) * tarif_type["WEEKEND"]
                taux_majoration_effective_ouvrable_pct = (
                    (energie_majoree_ouvrable_wh / energie_non_utilisee_totale_type_wh) * 100.0
                    if energie_non_utilisee_totale_type_wh > 0
                    else 0.0
                )
                taux_majoration_effective_weekend_pct = (
                    (energie_majoree_weekend_wh / energie_non_utilisee_totale_type_wh) * 100.0
                    if energie_non_utilisee_totale_type_wh > 0
                    else 0.0
                )

                prop = PropositionPanneau(
                    id_type_panneau=type_p.id,
                    libelle_type=type_p.libelle,
                    ratio_couverture=type_p.ratio_couverture,
                    puissance_propose_w=panneau_theorique_w,
                    puissance_installee_equivalente_w=puissance_installee_equivalente_w,
                    quantite_require=quantite,
                    prix_unitaire=type_p.prix_unitaire,
                    prix_total=prix_total,
                    prix_energie_ouvrable_ar_wh=tarif_type["OUVRABLE"],
                    prix_energie_weekend_ar_wh=tarif_type["WEEKEND"],
                    energie_non_utilisee_matin_wh=energie_non_utilisee_matin_type_wh,
                    energie_non_utilisee_soir_wh=energie_non_utilisee_soir_type_wh,
                    energie_non_utilisee_totale_wh=energie_non_utilisee_totale_type_wh,
                    taux_majoration_effective_ouvrable_pct=taux_majoration_effective_ouvrable_pct,
                    taux_majoration_effective_weekend_pct=taux_majoration_effective_weekend_pct,
                    prix_total_ouvrable_ar=prix_total_ouvrable_type,
                    prix_total_weekend_ar=prix_total_weekend_type,
                    est_recommande=False,
                )
                propositions_temporaires.append(prop)

            if propositions_temporaires:
                prix_min = min(p.prix_total for p in propositions_temporaires)
                propositions_panneau = [
                    replace(p, est_recommande=(p.prix_total == prix_min))
                    for p in propositions_temporaires
                ]

                proposition_reference = next(
                    (p for p in propositions_panneau if p.est_recommande),
                    min(propositions_panneau, key=lambda p: p.prix_total),
                )
                energie_non_utilisee_matin_wh = proposition_reference.energie_non_utilisee_matin_wh
                energie_non_utilisee_soir_wh = proposition_reference.energie_non_utilisee_soir_wh
                energie_non_utilisee_totale_wh = proposition_reference.energie_non_utilisee_totale_wh
                prix_unitaire_ouvrable_ar_wh = proposition_reference.prix_energie_ouvrable_ar_wh
                prix_unitaire_weekend_ar_wh = proposition_reference.prix_energie_weekend_ar_wh
                prix_total_ouvrable_ar = proposition_reference.prix_total_ouvrable_ar
                prix_total_weekend_ar = proposition_reference.prix_total_weekend_ar

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
            convertisseur_propose_w=convertisseur_propose_w,
            energie_non_utilisee_matin_wh=energie_non_utilisee_matin_wh,
            energie_non_utilisee_soir_wh=energie_non_utilisee_soir_wh,
            energie_non_utilisee_totale_wh=energie_non_utilisee_totale_wh,
            prix_unitaire_ouvrable_ar_wh=prix_unitaire_ouvrable_ar_wh,
            prix_unitaire_weekend_ar_wh=prix_unitaire_weekend_ar_wh,
            prix_total_ouvrable_ar=prix_total_ouvrable_ar,
            prix_total_weekend_ar=prix_total_weekend_ar,
            propositions_panneau=propositions_panneau,
        )
