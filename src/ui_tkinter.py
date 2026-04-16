import tkinter as tk
from tkinter import ttk, messagebox

from repository_sqlserver import RepositorySqlServer
from service_dimensionnement import ServiceDimensionnement


class ApplicationTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulation Panneau Solaire")
        self.geometry("1050x700")

        self.repository = RepositorySqlServer()
        self.service = ServiceDimensionnement()

        self.simulation_active_id: int | None = None
        self.map_simulations: dict[str, int] = {}
        self.map_tranches: dict[str, int] = {}
        self.tranches_disponibles: list[str] = ["MATIN", "SOIR", "NUIT"]

        self._build_ui()
        self._connect_db()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=10, pady=8)

        self.var_titre_simulation = tk.StringVar()
        self.var_notes_simulation = tk.StringVar()

        ttk.Label(header, text="Nouvelle simulation").grid(row=0, column=0, padx=4, pady=4)
        ttk.Entry(header, textvariable=self.var_titre_simulation, width=26).grid(row=0, column=1, padx=4, pady=4)
        ttk.Entry(header, textvariable=self.var_notes_simulation, width=32).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(header, text="Creer", command=self.creer_simulation).grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(header, text="Simulation active").grid(row=1, column=0, padx=4, pady=4)
        self.cmb_simulations = ttk.Combobox(header, width=60, state="readonly")
        self.cmb_simulations.grid(row=1, column=1, columnspan=2, padx=4, pady=4, sticky="w")
        self.cmb_simulations.bind("<<ComboboxSelected>>", self.selectionner_simulation)
        ttk.Button(header, text="Supprimer", command=self.supprimer_simulation).grid(row=1, column=3, padx=4, pady=4)

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=8)

        self.tab_entrees = ttk.Frame(tabs)
        self.tab_resultat = ttk.Frame(tabs)
        tabs.add(self.tab_entrees, text="Entrees")
        tabs.add(self.tab_resultat, text="Resultat")

        self._build_tab_entrees()
        self._build_tab_resultat()

    def _build_tab_entrees(self):
        form = ttk.LabelFrame(self.tab_entrees, text="Ajouter une entree")
        form.pack(fill="x", padx=8, pady=8)

        self.var_materiel = tk.StringVar()
        self.var_puissance = tk.StringVar()
        self.var_tranche = tk.StringVar(value="MATIN")
        self.var_duree = tk.StringVar()

        ttk.Label(form, text="Materiel").grid(row=0, column=0, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.var_materiel, width=22).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(form, text="Puissance (W)").grid(row=0, column=2, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.var_puissance, width=12).grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(form, text="Tranche").grid(row=0, column=4, padx=4, pady=4)
        self.cmb_tranches = ttk.Combobox(form, textvariable=self.var_tranche, values=self.tranches_disponibles, width=10, state="readonly")
        self.cmb_tranches.grid(row=0, column=5, padx=4, pady=4)
        ttk.Label(form, text="Duree (h)").grid(row=0, column=6, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.var_duree, width=10).grid(row=0, column=7, padx=4, pady=4)
        ttk.Button(form, text="Ajouter", command=self.ajouter_entree).grid(row=0, column=8, padx=6, pady=4)

        actions = ttk.Frame(self.tab_entrees)
        actions.pack(fill="x", padx=8, pady=4)
        ttk.Button(actions, text="Supprimer entree", command=self.supprimer_entree).pack(side="left")

        self.tree_entrees = ttk.Treeview(
            self.tab_entrees,
            columns=("id", "materiel", "puissance_w", "tranche", "duree_h"),
            show="headings",
            height=16,
        )
        for col, width in [
            ("id", 80),
            ("materiel", 300),
            ("puissance_w", 130),
            ("tranche", 110),
            ("duree_h", 110),
        ]:
            self.tree_entrees.heading(col, text=col)
            self.tree_entrees.column(col, width=width)
        self.tree_entrees.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_tab_resultat(self):
        top = ttk.Frame(self.tab_resultat)
        top.pack(fill="x", padx=8, pady=8)

        self.var_pas_panneau = tk.StringVar(value="50")
        self.var_pas_batterie = tk.StringVar(value="100")

        ttk.Label(top, text="Arrondi panneau (W)").grid(row=0, column=0, padx=4, pady=4)
        ttk.Entry(top, textvariable=self.var_pas_panneau, width=10).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(top, text="Arrondi batterie (Wh)").grid(row=0, column=2, padx=4, pady=4)
        ttk.Entry(top, textvariable=self.var_pas_batterie, width=10).grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(top, text="Calculer", command=self.calculer).grid(row=0, column=4, padx=8, pady=4)

        self.txt_resultat = tk.Text(self.tab_resultat, wrap="word", height=28)
        self.txt_resultat.pack(fill="both", expand=True, padx=8, pady=8)

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
            self.txt_resultat.delete("1.0", tk.END)
            self.rafraichir_simulations()
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

    def supprimer_entree(self):
        try:
            selection = self.tree_entrees.selection()
            if not selection:
                return
            entree_id = int(self.tree_entrees.item(selection[0])["values"][0])
            self.repository.supprimer_entree(entree_id)
            self.rafraichir_entrees()
        except Exception as exc:
            messagebox.showerror("Entree", str(exc))

    def calculer(self):
        try:
            if self.simulation_active_id is None:
                raise ValueError("Selectionnez d'abord une simulation")

            entrees = self.repository.lister_entrees(self.simulation_active_id)
            pas_panneau = float(self.var_pas_panneau.get())
            pas_batterie = float(self.var_pas_batterie.get())
            parametres = self.repository.charger_parametres()

            resultat = self.service.calculer(entrees, pas_panneau, pas_batterie, parametres)

            lignes = [
                "RESULTAT SIMULATION\n",
                "\nConsommation par tranche\n",
                f"- Matin: {resultat.energie_matin_wh:.2f} Wh\n",
                f"- Soir : {resultat.energie_soir_wh:.2f} Wh\n",
                f"- Nuit : {resultat.energie_nuit_wh:.2f} Wh\n",
                "\nPuissance par tranche\n",
                f"- Matin: {resultat.puissance_matin_w:.2f} W\n",
                f"- Soir : {resultat.puissance_soir_w:.2f} W\n",
                f"- Nuit : {resultat.puissance_nuit_w:.2f} W\n",
                "\nTheorique\n",
                f"- Batterie theorique (nuit): {resultat.batterie_theorique_wh:.2f} Wh\n",
                f"- Puissance charge batterie (matin): {resultat.puissance_charge_batterie_w:.2f} W\n",
                f"- Panneau theorique contrainte matin: {resultat.panneau_matin_theorique_w:.2f} W\n",
                f"- Panneau theorique contrainte soir : {resultat.panneau_soir_theorique_w:.2f} W\n",
                f"- Panneau theorique final          : {resultat.panneau_theorique_w:.2f} W\n",
                "\nPratique\n",
                f"- Panneau a acheter: {resultat.panneau_pratique_achat_w:.2f} W ({resultat.panneau_pratique_achat_w / 1000:.3f} kW)\n",
                f"- Batterie a acheter: {resultat.batterie_pratique_achat_wh:.2f} Wh ({resultat.batterie_pratique_achat_wh / 1000:.3f} kWh)\n",
            ]
            self.txt_resultat.delete("1.0", tk.END)
            self.txt_resultat.insert(tk.END, "".join(lignes))

        except Exception as exc:
            messagebox.showerror("Calcul", str(exc))
