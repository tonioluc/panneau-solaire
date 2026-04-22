from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from .reusable_widgets import add_labeled_entry, configure_treeview_columns


class EntreesMixin:
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

        add_labeled_entry(
            form_card,
            row=1,
            label_col=0,
            entry_col=1,
            label_text="Materiel",
            variable=self.var_materiel,
            width=22,
        )
        add_labeled_entry(
            form_card,
            row=1,
            label_col=2,
            entry_col=3,
            label_text="Puissance (W)",
            variable=self.var_puissance,
            width=10,
        )
        add_labeled_entry(
            form_card,
            row=1,
            label_col=4,
            entry_col=5,
            label_text="Heure debut (HH:MM)",
            variable=self.var_heure_debut,
            width=10,
        )
        add_labeled_entry(
            form_card,
            row=1,
            label_col=6,
            entry_col=7,
            label_text="Heure fin (HH:MM)",
            variable=self.var_heure_fin,
            width=10,
        )

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
        configure_treeview_columns(
            self.tree_entrees,
            [
                ("id", 70),
                ("materiel", 350),
                ("puissance_w", 150),
                ("heure_debut", 130),
                ("heure_fin", 130),
            ],
        )

        self.tree_entrees.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_entrees.bind("<Double-1>", self.charger_pour_edition)

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

    def _validate_hhmm(self, text: str):
        try:
            datetime.strptime(text, "%H:%M")
        except ValueError as exc:
            raise ValueError("Heure invalide. Utiliser le format HH:MM") from exc
