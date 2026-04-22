import tkinter as tk
from tkinter import ttk


class LayoutMixin:
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
            text="Projet panneau solaire",
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
