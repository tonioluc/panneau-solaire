import tkinter as tk
from tkinter import messagebox, ttk

from repository_sqlserver import RepositorySqlServer
from service_dimensionnement import ServiceDimensionnement
from theme_loader import ThemeLoader


class ApplicationTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SolarSim")
        self.geometry("1180x760")
        self.minsize(1100, 700)

        self.theme = ThemeLoader()
        self.personalized_layout = self.theme.has_user_theme
        self._configure_window_theme()

        self.repository = RepositorySqlServer()
        self.service = ServiceDimensionnement()

        self.simulation_active_id: int | None = None
        self.map_simulations: dict[str, int] = {}
        self.map_tranches: dict[str, int] = {}
        self.tranches_disponibles: list[str] = ["MATIN", "SOIR", "NUIT"]

        self.entree_en_edition_id: int | None = None
        self.result_labels: dict[str, tk.Label] = {}

        self._build_ui()
        self._connect_db()

    def _configure_window_theme(self):
        self.configure(bg=self.theme.get("surface"))

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "App.TFrame",
            background=self.theme.get("surface"),
        )
        self.style.configure(
            "Card.TFrame",
            background=self.theme.get("surface_container_low"),
        )
        self.style.configure(
            "WhiteCard.TFrame",
            background=self.theme.get("surface_container_lowest"),
        )
        self.style.configure(
            "App.TLabel",
            background=self.theme.get("surface"),
            foreground=self.theme.get("on_surface"),
            font=(self.theme.get("font_body"), 11),
        )
        self.style.configure(
            "Header.TLabel",
            background=self.theme.get("surface"),
            foreground=self.theme.get("primary"),
            font=(self.theme.get("font_display"), 21, "bold"),
        )
        self.style.configure(
            "Section.TLabel",
            background=self.theme.get("surface_container_low"),
            foreground=self.theme.get("on_surface"),
            font=(self.theme.get("font_display"), 14, "bold"),
        )
        self.style.configure(
            "Muted.TLabel",
            background=self.theme.get("surface_container_low"),
            foreground=self.theme.get("on_surface_muted"),
            font=(self.theme.get("font_body"), 10),
        )
        self.style.configure(
            "Primary.TButton",
            background=self.theme.get("primary"),
            foreground=self.theme.get("on_primary"),
            padding=(18, 10),
            relief="flat",
            borderwidth=0,
            font=(self.theme.get("font_body"), 10, "bold"),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", self.theme.get("primary_container"))],
            foreground=[("active", self.theme.get("on_primary"))],
        )
        self.style.configure(
            "Ghost.TButton",
            background=self.theme.get("surface_container_low"),
            foreground=self.theme.get("on_surface"),
            padding=(14, 8),
            relief="flat",
            borderwidth=0,
            font=(self.theme.get("font_body"), 10),
        )
        self.style.map(
            "Ghost.TButton",
            background=[("active", self.theme.get("surface_dim"))],
        )
        self.style.configure(
            "App.TEntry",
            fieldbackground=self.theme.get("surface_container_lowest"),
            foreground=self.theme.get("on_surface"),
            bordercolor=self.theme.get("outline_variant"),
            lightcolor=self.theme.get("outline_variant"),
            darkcolor=self.theme.get("outline_variant"),
            borderwidth=1,
            padding=8,
            insertcolor=self.theme.get("on_surface"),
            font=(self.theme.get("font_body"), 10),
        )
        self.style.configure(
            "App.TCombobox",
            fieldbackground=self.theme.get("surface_container_lowest"),
            foreground=self.theme.get("on_surface"),
            arrowcolor=self.theme.get("primary"),
            borderwidth=1,
            padding=6,
            font=(self.theme.get("font_body"), 10),
        )
        self.style.map(
            "App.TCombobox",
            fieldbackground=[("readonly", self.theme.get("surface_container_lowest"))],
            foreground=[("readonly", self.theme.get("on_surface"))],
        )
        self.style.configure(
            "App.Treeview",
            background=self.theme.get("surface_container_lowest"),
            fieldbackground=self.theme.get("surface_container_lowest"),
            foreground=self.theme.get("on_surface"),
            borderwidth=0,
            rowheight=34,
            font=(self.theme.get("font_body"), 10),
        )
        self.style.configure(
            "App.Treeview.Heading",
            background=self.theme.get("surface_container_low"),
            foreground=self.theme.get("on_surface"),
            borderwidth=0,
            font=(self.theme.get("font_body"), 10, "bold"),
        )
        self.style.map(
            "App.Treeview",
            background=[("selected", self.theme.get("secondary_container"))],
            foreground=[("selected", self.theme.get("on_surface"))],
        )

    def _build_ui(self):
        if self.personalized_layout:
            self._build_ui_personalized()
        else:
            self._build_ui_default()

    def _build_simulation_controls(self, parent: ttk.Frame):
        self.var_titre_simulation = tk.StringVar()
        self.var_notes_simulation = tk.StringVar()

        ttk.Label(parent, text="Nouvelle simulation", style="Section.TLabel").grid(
            row=0, column=0, padx=12, pady=(12, 8), sticky="w"
        )
        ttk.Entry(parent, textvariable=self.var_titre_simulation, width=24, style="App.TEntry").grid(
            row=0, column=1, padx=6, pady=(12, 8), sticky="w"
        )
        ttk.Entry(parent, textvariable=self.var_notes_simulation, width=34, style="App.TEntry").grid(
            row=0, column=2, padx=6, pady=(12, 8), sticky="w"
        )
        ttk.Button(parent, text="Creer", command=self.creer_simulation, style="Primary.TButton").grid(
            row=0, column=3, padx=10, pady=(12, 8), sticky="e"
        )

        ttk.Label(parent, text="Simulation active", style="Muted.TLabel").grid(
            row=1, column=0, padx=12, pady=(0, 12), sticky="w"
        )
        self.cmb_simulations = ttk.Combobox(parent, width=54, state="readonly", style="App.TCombobox")
        self.cmb_simulations.grid(row=1, column=1, columnspan=2, padx=6, pady=(0, 12), sticky="w")
        self.cmb_simulations.bind("<<ComboboxSelected>>", self.selectionner_simulation)

        ttk.Button(
            parent,
            text="Supprimer",
            command=self.supprimer_simulation,
            style="Ghost.TButton",
        ).grid(row=1, column=3, padx=10, pady=(0, 12), sticky="e")

        parent.columnconfigure(2, weight=1)

    def _build_ui_default(self):
        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="App.TFrame")
        header.pack(fill="x", padx=24, pady=(14, 8))

        ttk.Label(header, text="SolarSim", style="Header.TLabel").pack(side="left")

        control_card = ttk.Frame(shell, style="Card.TFrame")
        control_card.pack(fill="x", padx=24, pady=(0, 10))
        self._build_simulation_controls(control_card)

        tabs = ttk.Notebook(shell)
        tabs.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.tab_entrees = ttk.Frame(tabs, style="App.TFrame")
        self.tab_resultat = ttk.Frame(tabs, style="App.TFrame")

        tabs.add(self.tab_entrees, text="Entrees")
        tabs.add(self.tab_resultat, text="Resultats")

        self._build_tab_entrees()
        self._build_tab_resultat()

    def _build_ui_personalized(self):
        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        hero = tk.Frame(shell, bg=self.theme.get("primary"))
        hero.pack(fill="x", padx=18, pady=(14, 10))

        tk.Label(
            hero,
            text="ENERGY STUDIO",
            bg=self.theme.get("primary"),
            fg=self.theme.get("on_primary"),
            font=(self.theme.get("font_display"), 24, "bold"),
        ).pack(anchor="w", padx=18, pady=(14, 2))

        tk.Label(
            hero,
            text="Workspace personnalise: edition des charges a gauche, synthese vivante a droite",
            bg=self.theme.get("primary"),
            fg="#d8e6ff",
            font=(self.theme.get("font_body"), 11),
        ).pack(anchor="w", padx=18, pady=(0, 12))

        body = ttk.Frame(shell, style="App.TFrame")
        body.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        left = ttk.Frame(body, style="Card.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = ttk.Frame(body, style="WhiteCard.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        controls = ttk.Frame(left, style="Card.TFrame")
        controls.pack(fill="x", padx=10, pady=10)
        self._build_simulation_controls(controls)

        self.tab_entrees = ttk.Frame(left, style="Card.TFrame")
        self.tab_entrees.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_resultat = ttk.Frame(right, style="WhiteCard.TFrame")
        self.tab_resultat.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_tab_entrees()
        self._build_tab_resultat()

    def _build_tab_entrees(self):
        title_entrees = "Atelier des charges" if self.personalized_layout else "Donnees d'entree"
        action_add = "Injecter" if self.personalized_layout else "Ajouter"

        form_card = ttk.Frame(self.tab_entrees, style="Card.TFrame")
        form_card.pack(fill="x", pady=(12, 10))

        ttk.Label(form_card, text=title_entrees, style="Section.TLabel").grid(
            row=0, column=0, columnspan=8, sticky="w", padx=14, pady=(12, 8)
        )

        self.var_materiel = tk.StringVar()
        self.var_puissance = tk.StringVar()
        self.var_tranche = tk.StringVar(value="MATIN")
        self.var_duree = tk.StringVar()

        ttk.Label(form_card, text="Materiel", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_materiel, width=22, style="App.TEntry").grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Puissance (W)", style="Muted.TLabel").grid(row=1, column=2, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_puissance, width=10, style="App.TEntry").grid(row=1, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Tranche", style="Muted.TLabel").grid(row=1, column=4, padx=12, pady=6, sticky="w")
        self.cmb_tranches = ttk.Combobox(
            form_card,
            textvariable=self.var_tranche,
            values=self.tranches_disponibles,
            width=10,
            state="readonly",
            style="App.TCombobox",
        )
        self.cmb_tranches.grid(row=1, column=5, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Duree (h)", style="Muted.TLabel").grid(row=1, column=6, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_duree, width=10, style="App.TEntry").grid(row=1, column=7, padx=6, pady=6, sticky="w")

        self.btn_ajouter = ttk.Button(form_card, text=action_add, command=self.ajouter_entree, style="Primary.TButton")
        self.btn_ajouter.grid(row=1, column=8, padx=(10, 14), pady=6, sticky="e")

        actions = ttk.Frame(self.tab_entrees, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(actions, text="Modifier entree", command=self.modifier_entree, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Annuler edition", command=self.annuler_edition, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Supprimer entree", command=self.supprimer_entree, style="Ghost.TButton").pack(side="left")

        table_card = ttk.Frame(self.tab_entrees, style="WhiteCard.TFrame")
        table_card.pack(fill="both", expand=True)

        self.tree_entrees = ttk.Treeview(
            table_card,
            columns=("id", "materiel", "puissance_w", "tranche", "duree_h"),
            show="headings",
            height=16,
            style="App.Treeview",
        )

        for col, width in [
            ("id", 70),
            ("materiel", 350),
            ("puissance_w", 150),
            ("tranche", 130),
            ("duree_h", 130),
        ]:
            self.tree_entrees.heading(col, text=col)
            self.tree_entrees.column(col, width=width, anchor="w")

        self.tree_entrees.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_entrees.bind("<Double-1>", self.charger_pour_edition)

    def _build_tab_resultat(self):
        calculer_text = "Propulser calcul" if self.personalized_layout else "Calculer"
        consommation_title = "Flux energie par tranche" if self.personalized_layout else "Consommation par tranche"
        puissance_title = "Charge instantanee" if self.personalized_layout else "Puissance par tranche"
        theorique_title = "Modele theorique" if self.personalized_layout else "Theorique"
        pratique_title = "Projection d'achat" if self.personalized_layout else "Recommandations Pratiques"

        top = ttk.Frame(self.tab_resultat, style="App.TFrame")
        top.pack(fill="x", pady=(12, 10))

        ttk.Button(top, text=calculer_text, command=self.calculer, style="Primary.TButton").pack(side="right")

        grid = ttk.Frame(self.tab_resultat, style="App.TFrame")
        grid.pack(fill="both", expand=True)

        left_card = self._metric_card(grid, consommation_title)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        right_card = self._metric_card(grid, puissance_title)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        self._pair_row(left_card, "Matin", "energie_matin_wh", "Wh", 1)
        self._pair_row(left_card, "Soir", "energie_soir_wh", "Wh", 2)
        self._pair_row(left_card, "Nuit", "energie_nuit_wh", "Wh", 3)

        self._pair_row(right_card, "Matin", "puissance_matin_w", "W", 1)
        self._pair_row(right_card, "Soir", "puissance_soir_w", "W", 2)
        self._pair_row(right_card, "Nuit", "puissance_nuit_w", "W", 3)

        theo_card = ttk.Frame(grid, style="Card.TFrame")
        theo_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        ttk.Label(theo_card, text=theorique_title, style="Section.TLabel").pack(anchor="w", padx=14, pady=(12, 8))

        theo_metrics = ttk.Frame(theo_card, style="Card.TFrame")
        theo_metrics.pack(fill="x", padx=12, pady=(0, 12))

        self._mini_card(theo_metrics, "Batterie", "batterie_theorique_wh", "Wh", 0)
        self._mini_card(theo_metrics, "Charge batterie", "puissance_charge_batterie_w", "W", 1)
        self._mini_card(theo_metrics, "Panneau final", "panneau_theorique_w", "W", 2)

        practical_bg = tk.Frame(grid, bg=self.theme.get("primary"))
        practical_bg.grid(row=2, column=0, columnspan=2, sticky="nsew")

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
        practical_values.pack(fill="x", padx=20, pady=(0, 18))

        self._hero_metric(practical_values, "PANNEAU A ACHETER", "panneau_pratique_kw", "kW", 0)
        self._hero_metric(practical_values, "BATTERIE A ACHETER", "batterie_pratique_kwh", "kWh", 1)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        grid.rowconfigure(3, weight=1)

    def _metric_card(self, parent: ttk.Frame, title: str) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Card.TFrame")
        ttk.Label(frame, text=title, style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(12, 8))
        return frame

    def _pair_row(self, card: ttk.Frame, label: str, key: str, unit: str, row: int):
        ttk.Label(card, text=label, style="Muted.TLabel").grid(row=row, column=0, sticky="w", padx=14, pady=8)
        val = tk.Label(
            card,
            text="0.00",
            bg=self.theme.get("surface_container_low"),
            fg=self.theme.get("on_surface"),
            font=(self.theme.get("font_display"), 15, "bold"),
        )
        val.grid(row=row, column=1, sticky="e", padx=(8, 4), pady=8)
        unit_lbl = ttk.Label(card, text=unit, style="Muted.TLabel")
        unit_lbl.grid(row=row, column=2, sticky="w", padx=(0, 14), pady=8)
        self.result_labels[key] = val

    def _mini_card(self, parent: ttk.Frame, title: str, key: str, unit: str, col: int):
        card = tk.Frame(parent, bg=self.theme.get("surface_container_lowest"))
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=4)

        t = tk.Label(
            card,
            text=title,
            bg=self.theme.get("surface_container_lowest"),
            fg=self.theme.get("on_surface_muted"),
            font=(self.theme.get("font_body"), 10),
            anchor="w",
        )
        t.pack(fill="x", padx=12, pady=(10, 4))

        value_row = tk.Frame(card, bg=self.theme.get("surface_container_lowest"))
        value_row.pack(fill="x", padx=12, pady=(0, 12))

        val = tk.Label(
            value_row,
            text="0.00",
            bg=self.theme.get("surface_container_lowest"),
            fg=self.theme.get("primary"),
            font=(self.theme.get("font_display"), 18, "bold"),
        )
        val.pack(side="left")

        tk.Label(
            value_row,
            text=unit,
            bg=self.theme.get("surface_container_lowest"),
            fg=self.theme.get("on_surface_muted"),
            font=(self.theme.get("font_body"), 10),
        ).pack(side="left", padx=(4, 0), pady=(6, 0))

        self.result_labels[key] = val
        parent.columnconfigure(col, weight=1)

    def _hero_metric(self, parent: tk.Frame, title: str, key: str, unit: str, col: int):
        section = tk.Frame(parent, bg=self.theme.get("primary"))
        section.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 16, 0))

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

    def _connect_db(self):
        try:
            self.repository.connecter()
            self._charger_tranches()
            self.rafraichir_simulations()
        except Exception as exc:
            messagebox.showerror(
                "Base de donnees",
                "Connexion impossible. Cree manuellement la base et les tables puis relance l'application.\n\n"
                f"Detail: {exc}",
            )

    def _charger_tranches(self):
        tranches = self.repository.lister_tranches()
        if tranches:
            self.map_tranches = {libelle: tranche_id for tranche_id, libelle in tranches}
            self.tranches_disponibles = [libelle for _id, libelle in tranches]
            self.cmb_tranches["values"] = self.tranches_disponibles
            self.var_tranche.set(self.tranches_disponibles[0])

    def rafraichir_simulations(self):
        self.map_simulations.clear()
        rows = self.repository.lister_simulations()

        labels = []
        for sim in rows:
            label = f"{sim.id} - {sim.titre}"
            labels.append(label)
            self.map_simulations[label] = sim.id

        self.cmb_simulations["values"] = labels
        if labels:
            self.cmb_simulations.current(0)
            self.selectionner_simulation()

    def creer_simulation(self):
        try:
            titre = self.var_titre_simulation.get().strip()
            notes = self.var_notes_simulation.get().strip() or None
            if not titre:
                raise ValueError("Titre simulation obligatoire")

            self.repository.creer_simulation(titre, notes)
            self.var_titre_simulation.set("")
            self.var_notes_simulation.set("")
            self.rafraichir_simulations()
        except Exception as exc:
            messagebox.showerror("Simulation", str(exc))

    def supprimer_simulation(self):
        try:
            if self.simulation_active_id is None:
                return
            self.repository.supprimer_simulation(self.simulation_active_id)
            self.simulation_active_id = None
            self.tree_entrees.delete(*self.tree_entrees.get_children())
            self.rafraichir_simulations()
            self._reset_result_values()
        except Exception as exc:
            messagebox.showerror("Simulation", str(exc))

    def selectionner_simulation(self, _event=None):
        label = self.cmb_simulations.get().strip()
        self.simulation_active_id = self.map_simulations.get(label)
        self.rafraichir_entrees()

    def rafraichir_entrees(self):
        self.tree_entrees.delete(*self.tree_entrees.get_children())
        if self.simulation_active_id is None:
            return

        for entree in self.repository.lister_entrees(self.simulation_active_id):
            self.tree_entrees.insert(
                "",
                "end",
                values=(
                    entree.id,
                    entree.materiel,
                    f"{entree.puissance_w:.2f}",
                    entree.tranche,
                    f"{entree.duree_h:.2f}",
                ),
            )

    def charger_pour_edition(self, _event):
        selection = self.tree_entrees.selection()
        if not selection:
            return
        values = self.tree_entrees.item(selection[0])["values"]
        self.entree_en_edition_id = int(values[0])
        self.var_materiel.set(values[1])
        self.var_puissance.set(values[2])
        self.var_tranche.set(values[3])
        self.var_duree.set(values[4])
        maj_text = "Actualiser" if self.personalized_layout else "Mettre a jour"
        self.btn_ajouter.config(text=maj_text)

    def annuler_edition(self):
        self.entree_en_edition_id = None
        self.var_materiel.set("")
        self.var_puissance.set("")
        self.var_tranche.set("MATIN")
        self.var_duree.set("")
        reset_text = "Injecter" if self.personalized_layout else "Ajouter"
        self.btn_ajouter.config(text=reset_text)
        selection = self.tree_entrees.selection()
        if selection:
            self.tree_entrees.selection_remove(selection)

    def ajouter_entree(self):
        try:
            if self.simulation_active_id is None:
                raise ValueError("Selectionnez d'abord une simulation")

            materiel = self.var_materiel.get().strip()
            puissance_w = float(self.var_puissance.get())
            tranche = self.var_tranche.get().strip().upper()
            duree_h = float(self.var_duree.get())

            if not materiel:
                raise ValueError("Materiel obligatoire")
            if tranche not in self.map_tranches:
                raise ValueError("Tranche invalide")
            if puissance_w <= 0 or duree_h <= 0:
                raise ValueError("Puissance et duree doivent etre > 0")

            if self.entree_en_edition_id:
                self.repository.modifier_entree(
                    entree_id=self.entree_en_edition_id,
                    materiel=materiel,
                    puissance_w=puissance_w,
                    id_tranche_heure=self.map_tranches[tranche],
                    duree_h=duree_h,
                )
                self.annuler_edition()
            else:
                self.repository.ajouter_entree(
                    simulation_id=self.simulation_active_id,
                    materiel=materiel,
                    puissance_w=puissance_w,
                    id_tranche_heure=self.map_tranches[tranche],
                    duree_h=duree_h,
                )
                self.var_materiel.set("")
                self.var_puissance.set("")
                self.var_duree.set("")

            self.rafraichir_entrees()
        except Exception as exc:
            messagebox.showerror("Entree", str(exc))

    def modifier_entree(self):
        if self.entree_en_edition_id:
            self.ajouter_entree()
        else:
            messagebox.showinfo("Modification", "Double-cliquez sur une entree pour l'editer")

    def supprimer_entree(self):
        try:
            selection = self.tree_entrees.selection()
            if not selection:
                return
            entree_id = int(self.tree_entrees.item(selection[0])["values"][0])
            self.repository.supprimer_entree(entree_id)
            self.rafraichir_entrees()
            self.annuler_edition()
        except Exception as exc:
            messagebox.showerror("Entree", str(exc))

    def _set_result_value(self, key: str, value: float, decimals: int = 2):
        if key in self.result_labels:
            self.result_labels[key].config(text=f"{value:.{decimals}f}")

    def _reset_result_values(self):
        for key, label in self.result_labels.items():
            label.config(text="0.000" if key.endswith("kw") or key.endswith("kwh") else "0.00")

    def calculer(self):
        try:
            if self.simulation_active_id is None:
                raise ValueError("Selectionnez d'abord une simulation")

            entrees = self.repository.lister_entrees(self.simulation_active_id)
            parametres = self.repository.charger_parametres()
            resultat = self.service.calculer(entrees, parametres)

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
        except Exception as exc:
            messagebox.showerror("Calcul", str(exc))
