import tkinter as tk
from tkinter import messagebox, ttk


class ResultatsMixin:
    def _build_tab_resultat(self):
        calculer_text = "Propulser calcul" if self.personalized_layout else "Calculer"
        pratique_title = "Resultats principaux"
        details_title = "Details techniques"

        top = ttk.Frame(self.tab_resultat, style="App.TFrame")
        top.pack(fill="x", pady=(12, 10))

        ttk.Button(top, text=calculer_text, command=self.calculer, style="Primary.TButton").pack(side="right")

        practical_bg = tk.Frame(self.tab_resultat, bg=self.theme.get("primary"))
        practical_bg.pack(fill="x", pady=(0, 10))

        title = tk.Label(
            practical_bg,
            text=pratique_title,
            bg=self.theme.get("primary"),
            fg=self.theme.get("on_primary"),
            font=(self.theme.get("font_display"), 17, "bold"),
            anchor="w",
        )
        title.pack(fill="x", padx=20, pady=(16, 12))

        practical_values = tk.Frame(practical_bg, bg=self.theme.get("primary"))
        practical_values.pack(fill="x", padx=20, pady=(0, 10))

        self._hero_metric(practical_values, "BATTERIE A ACHETER", "batterie_pratique_kwh", "kWh", 0, 0)
        self._hero_metric(practical_values, "CONVERTISSEUR PROPOSE", "convertisseur_propose_kw", "kW", 1, 0)
        self._hero_metric(practical_values, "ENERGIE NON UTILISEE", "energie_non_utilisee_kwh", "kWh", 2, 0)

        self._hero_metric(
            practical_values,
            "PRIX UNITAIRE OUVRABLE",
            "prix_unitaire_ouvrable_ar_wh",
            "Ar/Wh",
            0,
            1,
        )
        self._hero_metric(
            practical_values,
            "PRIX UNITAIRE WEEK-END",
            "prix_unitaire_weekend_ar_wh",
            "Ar/Wh",
            1,
            1,
        )
        self._hero_metric(practical_values, "MEILLEUR PRIX PANNEAU", "meilleur_panneau_prix_ar", "Ar", 2, 1)

        self._hero_metric(practical_values, "TOTAL JOUR OUVRABLE", "prix_total_ouvrable_ar", "Ar", 0, 2)
        self._hero_metric(practical_values, "TOTAL WEEK-END", "prix_total_weekend_ar", "Ar", 1, 2)

        for col in range(3):
            practical_values.columnconfigure(col, weight=1)

        tk.Label(
            practical_bg,
            text="PANNEAUX ET PRIX PROPOSES",
            bg=self.theme.get("primary"),
            fg="#caefe0",
            font=(self.theme.get("font_body"), 10, "bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(6, 8))

        self.propositions_container = tk.Frame(practical_bg, bg=self.theme.get("primary"))
        self.propositions_container.pack(fill="x", padx=20, pady=(0, 18))

        details_card = ttk.Frame(self.tab_resultat, style="Card.TFrame")
        details_card.pack(fill="both", expand=True)

        ttk.Label(details_card, text=details_title, style="Section.TLabel").pack(anchor="w", padx=14, pady=(12, 8))

        details_grid = tk.Frame(details_card, bg=self.theme.get("surface_container_low"))
        details_grid.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._detail_chip(details_grid, "Energie matin", "energie_matin_wh", "Wh", 0, 0)
        self._detail_chip(details_grid, "Energie soir", "energie_soir_wh", "Wh", 0, 1)
        self._detail_chip(details_grid, "Energie nuit", "energie_nuit_wh", "Wh", 0, 2)

        self._detail_chip(details_grid, "Puissance matin", "puissance_matin_w", "W", 1, 0)
        self._detail_chip(details_grid, "Puissance soir", "puissance_soir_w", "W", 1, 1)
        self._detail_chip(details_grid, "Puissance nuit", "puissance_nuit_w", "W", 1, 2)

        self._detail_chip(details_grid, "Batterie theorique", "batterie_theorique_wh", "Wh", 2, 0)
        self._detail_chip(details_grid, "Charge batterie", "puissance_charge_batterie_w", "W", 2, 1)
        self._detail_chip(details_grid, "Panneau final", "panneau_theorique_w", "W", 2, 2)

    def _detail_chip(self, parent: tk.Frame, title: str, key: str, unit: str, row: int, col: int):
        card = tk.Frame(parent, bg=self.theme.get("surface_container_lowest"))
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        tk.Label(
            card,
            text=title,
            bg=self.theme.get("surface_container_lowest"),
            fg=self.theme.get("on_surface_muted"),
            font=(self.theme.get("font_body"), 9),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 2))

        value_line = tk.Frame(card, bg=self.theme.get("surface_container_lowest"))
        value_line.pack(fill="x", padx=10, pady=(0, 8))

        val = tk.Label(
            value_line,
            text="0.00",
            bg=self.theme.get("surface_container_lowest"),
            fg=self.theme.get("on_surface"),
            font=(self.theme.get("font_body"), 12, "bold"),
        )
        val.pack(side="left")

        tk.Label(
            value_line,
            text=unit,
            bg=self.theme.get("surface_container_lowest"),
            fg=self.theme.get("on_surface_muted"),
            font=(self.theme.get("font_body"), 9),
        ).pack(side="left", padx=(4, 0), pady=(3, 0))

        self.result_labels[key] = val
        parent.columnconfigure(col, weight=1)

    def _hero_metric(
        self,
        parent: tk.Frame,
        title: str,
        key: str,
        unit: str,
        col: int,
        row: int = 0,
    ):
        section = tk.Frame(parent, bg=self.theme.get("primary"))
        section.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=(0 if col == 0 else 16, 0),
            pady=(0, 10 if row < 2 else 0),
        )

        tk.Label(
            section,
            text=title,
            bg=self.theme.get("primary"),
            fg="#caefe0",
            font=(self.theme.get("font_body"), 10, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        value_line = tk.Frame(section, bg=self.theme.get("primary"))
        value_line.pack(fill="x")

        val = tk.Label(
            value_line,
            text="0.000",
            bg=self.theme.get("primary"),
            fg=self.theme.get("on_primary"),
            font=(self.theme.get("font_display"), 30, "bold"),
        )
        val.pack(side="left")

        tk.Label(
            value_line,
            text=unit,
            bg=self.theme.get("primary"),
            fg="#b7ebce",
            font=(self.theme.get("font_body"), 17),
        ).pack(side="left", padx=(6, 0), pady=(10, 0))

        self.result_labels[key] = val
        parent.columnconfigure(col, weight=1)

    def _set_result_value(self, key: str, value: float, decimals: int = 2):
        if key in self.result_labels:
            self.result_labels[key].config(text=f"{value:.{decimals}f}")

    def _reset_result_values(self):
        for key, label in self.result_labels.items():
            if key.endswith("kw") or key.endswith("kwh"):
                label.config(text="0.000")
            elif key.endswith("ar_wh"):
                label.config(text="0.0000")
            else:
                label.config(text="0.00")

    def calculer(self):
        try:
            if self.simulation_active_id is None:
                raise ValueError("Selectionnez d'abord une simulation")

            entrees = self.repository.lister_entrees(self.simulation_active_id)
            parametres = self.repository.charger_parametres()
            tranches = self.repository.lister_tranches_detail()
            types_panneau = self.repository.lister_types_panneau()
            prix_energie_non_utilisee = self.repository.charger_prix_energie_non_utilisee()
            resultat = self.service.calculer(
                entrees,
                parametres,
                tranches,
                types_panneau,
                prix_energie_non_utilisee,
            )

            self._set_result_value("energie_matin_wh", resultat.energie_matin_wh)
            self._set_result_value("energie_soir_wh", resultat.energie_soir_wh)
            self._set_result_value("energie_nuit_wh", resultat.energie_nuit_wh)

            self._set_result_value("puissance_matin_w", resultat.puissance_matin_w)
            self._set_result_value("puissance_soir_w", resultat.puissance_soir_w)
            self._set_result_value("puissance_nuit_w", resultat.puissance_nuit_w)

            self._set_result_value("batterie_theorique_wh", resultat.batterie_theorique_wh)
            self._set_result_value("puissance_charge_batterie_w", resultat.puissance_charge_batterie_w)
            self._set_result_value("panneau_theorique_w", resultat.panneau_theorique_w)

            self._set_result_value("panneau_pratique_kw", resultat.panneau_pratique_achat_w / 1000.0, 3)
            self._set_result_value("batterie_pratique_kwh", resultat.batterie_pratique_achat_wh / 1000.0, 3)
            self._set_result_value("convertisseur_propose_kw", resultat.convertisseur_propose_w / 1000.0, 3)
            self._set_result_value("energie_non_utilisee_kwh", resultat.energie_non_utilisee_totale_wh / 1000.0, 3)

            self._set_result_value("energie_non_utilisee_matin_wh", resultat.energie_non_utilisee_matin_wh)
            self._set_result_value("energie_non_utilisee_soir_wh", resultat.energie_non_utilisee_soir_wh)
            self._set_result_value("energie_non_utilisee_totale_wh", resultat.energie_non_utilisee_totale_wh)
            self._set_result_value("prix_unitaire_ouvrable_ar_wh", resultat.prix_unitaire_ouvrable_ar_wh, 4)
            self._set_result_value("prix_unitaire_weekend_ar_wh", resultat.prix_unitaire_weekend_ar_wh, 4)
            self._set_result_value("prix_total_ouvrable_ar", resultat.prix_total_ouvrable_ar)
            self._set_result_value("prix_total_weekend_ar", resultat.prix_total_weekend_ar)

            meilleur_prix_panneau_ar = 0.0
            if resultat.propositions_panneau:
                meilleur = next(
                    (p for p in resultat.propositions_panneau if p.est_recommande),
                    min(resultat.propositions_panneau, key=lambda p: p.prix_total),
                )
                meilleur_prix_panneau_ar = meilleur.prix_total
            self._set_result_value("meilleur_panneau_prix_ar", meilleur_prix_panneau_ar)

            self._afficher_propositions_panneaux(resultat.propositions_panneau)
        except Exception as exc:
            messagebox.showerror("Calcul", str(exc))

    def _afficher_propositions_panneaux(self, propositions: list):
        try:
            for w in self.propositions_container.winfo_children():
                w.destroy()

            if not propositions:
                tk.Label(
                    self.propositions_container,
                    text="Aucune proposition de panneau disponible.",
                    bg=self.theme.get("primary"),
                    fg="#d8e6ff",
                    font=(self.theme.get("font_body"), 10),
                    anchor="w",
                ).pack(fill="x")
                return

            for idx, prop in enumerate(propositions):
                titre = f"PANNEAU {prop.libelle_type.upper()}"
                if prop.est_recommande:
                    titre += "  -  MEILLEUR PRIX"

                section = tk.Frame(
                    self.propositions_container,
                    bg=self.theme.get("primary_container") if prop.est_recommande else self.theme.get("surface_container_lowest"),
                    highlightthickness=1,
                    highlightbackground=self.theme.get("primary") if prop.est_recommande else self.theme.get("outline_variant"),
                )
                section.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 14, 0), pady=(0, 4))

                tk.Label(
                    section,
                    text=titre,
                    bg=section.cget("bg"),
                    fg=self.theme.get("on_primary_container") if prop.est_recommande else self.theme.get("on_surface"),
                    font=(self.theme.get("font_body"), 10, "bold"),
                    anchor="w",
                    wraplength=260,
                ).pack(fill="x", padx=14, pady=(12, 4))

                value_line = tk.Frame(section, bg=section.cget("bg"))
                value_line.pack(fill="x", padx=14, pady=(0, 6))

                val = tk.Label(
                    value_line,
                    text=f"{prop.quantite_require:.0f}",
                    bg=section.cget("bg"),
                    fg=self.theme.get("primary") if prop.est_recommande else self.theme.get("on_surface"),
                    font=(self.theme.get("font_display"), 24, "bold"),
                )
                val.pack(side="left")

                tk.Label(
                    value_line,
                    text="unites",
                    bg=section.cget("bg"),
                    fg=self.theme.get("on_primary_container") if prop.est_recommande else self.theme.get("on_surface"),
                    font=(self.theme.get("font_body"), 11),
                ).pack(side="left", padx=(4, 0))

                tk.Label(
                    section,
                    text=f"Prix total: {prop.prix_total:.2f} Ar",
                    bg=section.cget("bg"),
                    fg=self.theme.get("primary") if prop.est_recommande else self.theme.get("on_surface"),
                    font=(self.theme.get("font_display"), 17, "bold"),
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(0, 2))

                tk.Label(
                    section,
                    text=f"Prix unitaire: {prop.prix_unitaire:.2f} Ar  |  Ratio: {prop.ratio_couverture:.1%}",
                    bg=section.cget("bg"),
                    fg=self.theme.get("on_primary_container") if prop.est_recommande else self.theme.get("on_surface_muted"),
                    font=(self.theme.get("font_body"), 9),
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(0, 12))

                self.propositions_container.columnconfigure(idx, weight=1)

        except Exception as exc:
            messagebox.showerror("Affichage propositions", str(exc))
