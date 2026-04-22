from tkinter import messagebox


class SimulationsMixin:
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
