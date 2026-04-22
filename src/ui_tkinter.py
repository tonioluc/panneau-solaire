import tkinter as tk
from datetime import datetime
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
        self.tranches_disponibles: list[str] = ["MATIN", "SOIR", "NUIT"]

        self.entree_en_edition_id: int | None = None
        self.result_labels: dict[str, tk.Label] = {}

        self.type_panneau_en_edition_id: int | None = None
        self.types_panneau_actuels: list = []

        self.prix_energie_en_edition_id: int | None = None
        self.prix_energie_actuels: list = []

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
        self.tab_types_panneau = ttk.Frame(tabs, style="App.TFrame")
        self.tab_prix_energie = ttk.Frame(tabs, style="App.TFrame")

        tabs.add(self.tab_entrees, text="Entrees")
        tabs.add(self.tab_resultat, text="Resultats")
        tabs.add(self.tab_types_panneau, text="Types Panneau")
        tabs.add(self.tab_prix_energie, text="Prix Energie")

        self._build_tab_entrees()
        self._build_tab_resultat()
        self._build_tab_types_panneau()
        self._build_tab_prix_energie()

    def _build_ui_personalized(self):
        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        hero = tk.Frame(shell, bg=self.theme.get("primary"))
        hero.pack(fill="x", padx=18, pady=(14, 10))

        tk.Label(
            hero,
            text= "Projet panneau solaire",
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

        body = ttk.PanedWindow(shell, orient="horizontal")
        body.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        left = ttk.Frame(body, style="Card.TFrame")
        body.add(left, weight=1)

        right = ttk.Frame(body, style="WhiteCard.TFrame")
        body.add(right, weight=1)

        controls = ttk.Frame(left, style="Card.TFrame")
        controls.pack(fill="x", padx=10, pady=10)
        self._build_simulation_controls(controls)

        left_tabs = ttk.Notebook(left)
        left_tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_entrees = ttk.Frame(left_tabs, style="Card.TFrame")
        self.tab_types_panneau = ttk.Frame(left_tabs, style="App.TFrame")
        self.tab_prix_energie = ttk.Frame(left_tabs, style="App.TFrame")

        left_tabs.add(self.tab_entrees, text="Entrees")
        left_tabs.add(self.tab_types_panneau, text="Types Panneau")
        left_tabs.add(self.tab_prix_energie, text="Prix Energie")

        self.tab_resultat = ttk.Frame(right, style="WhiteCard.TFrame")
        self.tab_resultat.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_tab_entrees()
        self._build_tab_types_panneau()
        self._build_tab_prix_energie()
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
        self.var_heure_debut = tk.StringVar()
        self.var_heure_fin = tk.StringVar()

        ttk.Label(form_card, text="Materiel", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_materiel, width=22, style="App.TEntry").grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Puissance (W)", style="Muted.TLabel").grid(row=1, column=2, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_puissance, width=10, style="App.TEntry").grid(row=1, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Heure debut (HH:MM)", style="Muted.TLabel").grid(row=1, column=4, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_heure_debut, width=10, style="App.TEntry").grid(row=1, column=5, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Heure fin (HH:MM)", style="Muted.TLabel").grid(row=1, column=6, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_heure_fin, width=10, style="App.TEntry").grid(row=1, column=7, padx=6, pady=6, sticky="w")

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
            columns=("id", "materiel", "puissance_w", "heure_debut", "heure_fin"),
            show="headings",
            height=16,
            style="App.Treeview",
        )

        for col, width in [
            ("id", 70),
            ("materiel", 350),
            ("puissance_w", 150),
            ("heure_debut", 130),
            ("heure_fin", 130),
        ]:
            self.tree_entrees.heading(col, text=col)
            self.tree_entrees.column(col, width=width, anchor="w")

        self.tree_entrees.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_entrees.bind("<Double-1>", self.charger_pour_edition)

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

        self._hero_metric(practical_values, "VALEUR JOUR OUVRABLE", "prix_total_ouvrable_ar", "Ar", 0, 1)
        self._hero_metric(practical_values, "VALEUR WEEK-END", "prix_total_weekend_ar", "Ar", 1, 1)
        self._hero_metric(practical_values, "MEILLEUR PRIX PANNEAU", "meilleur_panneau_prix_ar", "Ar", 2, 1)

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

        # Container pour les propositions panneaux dynamiques
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

    def _build_tab_types_panneau(self):
        """Onglet de gestion des types de panneaux (CRUD)"""
        form_card = ttk.Frame(self.tab_types_panneau, style="Card.TFrame")
        form_card.pack(fill="x", pady=(12, 10))

        ttk.Label(form_card, text="Gestion des types de panneaux", style="Section.TLabel").grid(
            row=0, column=0, columnspan=7, sticky="w", padx=14, pady=(12, 8)
        )

        self.var_type_libelle = tk.StringVar()
        self.var_type_ratio = tk.StringVar()
        self.var_type_energie = tk.StringVar()
        self.var_type_prix = tk.StringVar()

        ttk.Label(form_card, text="Libelle", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_type_libelle, width=20, style="App.TEntry").grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Ratio (0-1)", style="Muted.TLabel").grid(row=1, column=2, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_type_ratio, width=10, style="App.TEntry").grid(row=1, column=3, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Energie W(Wh)", style="Muted.TLabel").grid(row=1, column=4, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_type_energie, width=10, style="App.TEntry").grid(row=1, column=5, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Prix ( Ar)", style="Muted.TLabel").grid(row=1, column=6, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_type_prix, width=10, style="App.TEntry").grid(row=1, column=7, padx=6, pady=6, sticky="w")

        ttk.Button(form_card, text="Ajouter", command=self.ajouter_type_panneau, style="Primary.TButton").grid(
            row=1, column=8, padx=(10, 14), pady=6, sticky="e"
        )

        actions = ttk.Frame(self.tab_types_panneau, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(actions, text="Modifier type", command=self.modifier_type_panneau, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Annuler edition", command=self.annuler_edition_type, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Supprimer type", command=self.supprimer_type_panneau, style="Ghost.TButton").pack(side="left")

        table_card = ttk.Frame(self.tab_types_panneau, style="WhiteCard.TFrame")
        table_card.pack(fill="both", expand=True)

        self.tree_types_panneau = ttk.Treeview(
            table_card,
            columns=("id", "libelle", "ratio", "energie", "prix"),
            show="headings",
            height=16,
            style="App.Treeview",
        )

        for col, width in [
            ("id", 70),
            ("libelle", 200),
            ("ratio", 120),
            ("energie", 120),
            ("prix", 120),
        ]:
            self.tree_types_panneau.heading(col, text=col)
            self.tree_types_panneau.column(col, width=width, anchor="w")

        self.tree_types_panneau.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_types_panneau.bind("<Double-1>", self.charger_type_pour_edition)

    def _build_tab_prix_energie(self):
        """Onglet de gestion des prix de vente de l'energie non utilisee (CRUD)"""
        form_card = ttk.Frame(self.tab_prix_energie, style="Card.TFrame")
        form_card.pack(fill="x", pady=(12, 10))

        ttk.Label(form_card, text="Configuration prix energie non utilisee", style="Section.TLabel").grid(
            row=0, column=0, columnspan=6, sticky="w", padx=14, pady=(12, 8)
        )

        self.var_prix_code_jour = tk.StringVar(value="OUVRABLE")
        self.var_prix_wh = tk.StringVar()

        ttk.Label(form_card, text="Type de jour", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        self.cmb_prix_code_jour = ttk.Combobox(
            form_card,
            textvariable=self.var_prix_code_jour,
            values=("OUVRABLE", "WEEKEND"),
            width=16,
            state="readonly",
            style="App.TCombobox",
        )
        self.cmb_prix_code_jour.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Prix (Ar/Wh)", style="Muted.TLabel").grid(row=1, column=2, padx=12, pady=6, sticky="w")
        ttk.Entry(form_card, textvariable=self.var_prix_wh, width=14, style="App.TEntry").grid(row=1, column=3, padx=6, pady=6, sticky="w")

        self.btn_ajouter_prix = ttk.Button(
            form_card,
            text="Ajouter",
            command=self.ajouter_prix_energie,
            style="Primary.TButton",
        )
        self.btn_ajouter_prix.grid(row=1, column=4, padx=(10, 14), pady=6, sticky="e")

        actions = ttk.Frame(self.tab_prix_energie, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(actions, text="Modifier prix", command=self.modifier_prix_energie, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Annuler edition", command=self.annuler_edition_prix, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Supprimer prix", command=self.supprimer_prix_energie, style="Ghost.TButton").pack(side="left")

        table_card = ttk.Frame(self.tab_prix_energie, style="WhiteCard.TFrame")
        table_card.pack(fill="both", expand=True)

        self.tree_prix_energie = ttk.Treeview(
            table_card,
            columns=("id", "code_jour", "prix_wh"),
            show="headings",
            height=16,
            style="App.Treeview",
        )

        for col, width in [
            ("id", 90),
            ("code_jour", 200),
            ("prix_wh", 180),
        ]:
            self.tree_prix_energie.heading(col, text=col)
            self.tree_prix_energie.column(col, width=width, anchor="w")

        self.tree_prix_energie.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_prix_energie.bind("<Double-1>", self.charger_prix_pour_edition)

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

    def _hero_metric(self, parent: tk.Frame, title: str, key: str, unit: str, col: int, row: int = 0):
        section = tk.Frame(parent, bg=self.theme.get("primary"))
        section.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=(0 if col == 0 else 16, 0),
            pady=(0, 12 if row == 0 else 0),
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

    def _proposal_metric(self, parent: tk.Frame, title: str, key: str, unit: str, col: int):
        section = tk.Frame(
            parent,
            bg=self.theme.get("primary_container"),
            highlightthickness=1,
            highlightbackground=self.theme.get("primary"),
        )
        section.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 12, 0))

        tk.Label(
            section,
            text=title,
            bg=self.theme.get("primary_container"),
            fg=self.theme.get("on_primary_container"),
            font=(self.theme.get("font_body"), 10, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 6))

        value_line = tk.Frame(section, bg=self.theme.get("primary_container"))
        value_line.pack(fill="x", padx=12)

        val = tk.Label(
            value_line,
            text="0.000",
            bg=self.theme.get("primary_container"),
            fg=self.theme.get("primary"),
            font=(self.theme.get("font_display"), 20, "bold"),
        )
        val.pack(side="left")

        tk.Label(
            value_line,
            text=unit,
            bg=self.theme.get("primary_container"),
            fg=self.theme.get("on_primary_container"),
            font=(self.theme.get("font_body"), 12),
        ).pack(side="left", padx=(6, 0), pady=(6, 0))

        tk.Frame(section, bg=self.theme.get("primary_container"), height=8).pack(fill="x")

        self.result_labels[key] = val
        parent.columnconfigure(col, weight=1)

    def _connect_db(self):
        try:
            self.repository.connecter()
            self._charger_tranches()
            self.rafraichir_simulations()
            self.rafraichir_types_panneau()
            self.rafraichir_prix_energie()
        except Exception as exc:
            messagebox.showerror(
                "Base de donnees",
                "Connexion impossible. Cree manuellement la base et les tables puis relance l'application.\n\n"
                f"Detail: {exc}",
            )

    def _charger_tranches(self):
        tranches = self.repository.lister_tranches()
        if tranches:
            self.tranches_disponibles = [libelle for _id, libelle in tranches]

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
                    entree.heure_debut,
                    entree.heure_fin,
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
        self.var_heure_debut.set(values[3])
        self.var_heure_fin.set(values[4])
        maj_text = "Actualiser" if self.personalized_layout else "Mettre a jour"
        self.btn_ajouter.config(text=maj_text)

    def annuler_edition(self):
        self.entree_en_edition_id = None
        self.var_materiel.set("")
        self.var_puissance.set("")
        self.var_heure_debut.set("")
        self.var_heure_fin.set("")
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
            heure_debut = self.var_heure_debut.get().strip()
            heure_fin = self.var_heure_fin.get().strip()

            if not materiel:
                raise ValueError("Materiel obligatoire")
            if puissance_w <= 0:
                raise ValueError("Puissance doit etre > 0")

            self._validate_hhmm(heure_debut)
            self._validate_hhmm(heure_fin)
            if heure_debut == heure_fin:
                raise ValueError("Heure debut et heure fin ne peuvent pas etre identiques")

            if self.entree_en_edition_id:
                self.repository.modifier_entree(
                    entree_id=self.entree_en_edition_id,
                    materiel=materiel,
                    puissance_w=puissance_w,
                    heure_debut=heure_debut,
                    heure_fin=heure_fin,
                )
                self.annuler_edition()
            else:
                self.repository.ajouter_entree(
                    simulation_id=self.simulation_active_id,
                    materiel=materiel,
                    puissance_w=puissance_w,
                    heure_debut=heure_debut,
                    heure_fin=heure_fin,
                )
                self.var_materiel.set("")
                self.var_puissance.set("")
                self.var_heure_debut.set("")
                self.var_heure_fin.set("")

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

    def _validate_hhmm(self, text: str):
        try:
            datetime.strptime(text, "%H:%M")
        except ValueError as exc:
            raise ValueError("Heure invalide. Utiliser le format HH:MM") from exc

    def _reset_result_values(self):
        for key, label in self.result_labels.items():
            label.config(text="0.000" if key.endswith("kw") or key.endswith("kwh") else "0.00")

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

    def ajouter_type_panneau(self):
        try:
            libelle = self.var_type_libelle.get().strip()
            ratio = float(self.var_type_ratio.get())
            energie = float(self.var_type_energie.get())
            prix = float(self.var_type_prix.get())

            if not libelle:
                raise ValueError("Libelle requis")
            if ratio <= 0 or ratio > 1:
                raise ValueError("Ratio doit etre entre 0 et 1")
            if energie <= 0:
                raise ValueError("Energie unitaire doit etre > 0")
            if prix < 0:
                raise ValueError("Prix doit etre >= 0")

            if self.type_panneau_en_edition_id is None:
                self.repository.creer_type_panneau(libelle, ratio, energie, prix)
            else:
                self.repository.modifier_type_panneau(
                    self.type_panneau_en_edition_id, libelle, ratio, energie, prix
                )
                self.type_panneau_en_edition_id = None

            self.var_type_libelle.set("")
            self.var_type_ratio.set("")
            self.var_type_energie.set("")
            self.var_type_prix.set("")
            self.rafraichir_types_panneau()
        except Exception as exc:
            messagebox.showerror("Type Panneau", str(exc))

    def modifier_type_panneau(self):
        if self.type_panneau_en_edition_id:
            self.ajouter_type_panneau()
        else:
            messagebox.showinfo("Modification", "Double-cliquez sur un type pour l'editer")

    def supprimer_type_panneau(self):
        try:
            selection = self.tree_types_panneau.selection()
            if not selection:
                return
            type_id = int(self.tree_types_panneau.item(selection[0])["values"][0])
            self.repository.supprimer_type_panneau(type_id)
            self.rafraichir_types_panneau()
            self.annuler_edition_type()
        except Exception as exc:
            messagebox.showerror("Type Panneau", str(exc))

    def charger_type_pour_edition(self, event):
        try:
            selection = self.tree_types_panneau.selection()
            if not selection:
                return
            values = self.tree_types_panneau.item(selection[0])["values"]
            self.type_panneau_en_edition_id = int(values[0])
            self.var_type_libelle.set(values[1])
            self.var_type_ratio.set(str(values[2]))
            self.var_type_energie.set(str(values[3]))
            self.var_type_prix.set(str(values[4]))
        except Exception as exc:
            messagebox.showerror("Edition", str(exc))

    def annuler_edition_type(self):
        self.type_panneau_en_edition_id = None
        self.var_type_libelle.set("")
        self.var_type_ratio.set("")
        self.var_type_energie.set("")
        self.var_type_prix.set("")
        self.tree_types_panneau.selection_remove(self.tree_types_panneau.selection())

    def rafraichir_types_panneau(self):
        # L'UI peut être construite avant la connexion DB; on évite un popup inutile.
        if self.repository.cnxn is None:
            return

        for item in self.tree_types_panneau.get_children():
            self.tree_types_panneau.delete(item)
        try:
            self.types_panneau_actuels = self.repository.lister_types_panneau()
            for tp in self.types_panneau_actuels:
                self.tree_types_panneau.insert(
                    "",
                    "end",
                    values=(tp.id, tp.libelle, f"{tp.ratio_couverture:.2f}", f"{tp.energie_unitaire_wh:.2f}", f"{tp.prix_unitaire:.2f}"),
                )
        except Exception as exc:
            messagebox.showerror("Types Panneau", str(exc))

    def ajouter_prix_energie(self):
        try:
            code_jour = self.var_prix_code_jour.get().strip().upper()
            prix_wh = float(self.var_prix_wh.get())

            if code_jour not in {"OUVRABLE", "WEEKEND"}:
                raise ValueError("Type de jour invalide (OUVRABLE ou WEEKEND)")
            if prix_wh < 0:
                raise ValueError("Prix doit etre >= 0")

            if self.prix_energie_en_edition_id is None:
                self.repository.creer_prix_energie_non_utilisee(code_jour, prix_wh)
            else:
                self.repository.modifier_prix_energie_non_utilisee(
                    self.prix_energie_en_edition_id,
                    code_jour,
                    prix_wh,
                )
                self.prix_energie_en_edition_id = None

            self.var_prix_code_jour.set("OUVRABLE")
            self.var_prix_wh.set("")
            self.btn_ajouter_prix.config(text="Ajouter")
            self.rafraichir_prix_energie()
        except Exception as exc:
            messagebox.showerror("Prix Energie", str(exc))

    def modifier_prix_energie(self):
        if self.prix_energie_en_edition_id:
            self.ajouter_prix_energie()
        else:
            messagebox.showinfo("Modification", "Double-cliquez sur un prix pour l'editer")

    def supprimer_prix_energie(self):
        try:
            selection = self.tree_prix_energie.selection()
            if not selection:
                return
            prix_id = int(self.tree_prix_energie.item(selection[0])["values"][0])
            self.repository.supprimer_prix_energie_non_utilisee(prix_id)
            self.rafraichir_prix_energie()
            self.annuler_edition_prix()
        except Exception as exc:
            messagebox.showerror("Prix Energie", str(exc))

    def charger_prix_pour_edition(self, _event):
        try:
            selection = self.tree_prix_energie.selection()
            if not selection:
                return
            values = self.tree_prix_energie.item(selection[0])["values"]
            self.prix_energie_en_edition_id = int(values[0])
            self.var_prix_code_jour.set(str(values[1]))
            self.var_prix_wh.set(str(values[2]))
            self.btn_ajouter_prix.config(text="Mettre a jour")
        except Exception as exc:
            messagebox.showerror("Edition Prix", str(exc))

    def annuler_edition_prix(self):
        self.prix_energie_en_edition_id = None
        self.var_prix_code_jour.set("OUVRABLE")
        self.var_prix_wh.set("")
        self.btn_ajouter_prix.config(text="Ajouter")
        selection = self.tree_prix_energie.selection()
        if selection:
            self.tree_prix_energie.selection_remove(selection)

    def rafraichir_prix_energie(self):
        if self.repository.cnxn is None:
            return

        for item in self.tree_prix_energie.get_children():
            self.tree_prix_energie.delete(item)
        try:
            self.prix_energie_actuels = self.repository.lister_prix_energie_non_utilisee()
            for prix in self.prix_energie_actuels:
                self.tree_prix_energie.insert(
                    "",
                    "end",
                    values=(prix.id, prix.code_jour, f"{prix.prix_wh:.4f}"),
                )
        except Exception as exc:
            messagebox.showerror("Prix Energie", str(exc))

    def _afficher_propositions_panneaux(self, propositions: list):
        """Affiche dynamiquement les propositions de panneaux"""
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
                    titre += "  •  MEILLEUR PRIX"

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
