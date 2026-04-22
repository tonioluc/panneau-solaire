import tkinter as tk
from tkinter import messagebox, ttk

from .reusable_widgets import add_labeled_entry, configure_treeview_columns


class TypesPanneauMixin:
    def _build_tab_types_panneau(self):
        form_card = ttk.Frame(self.tab_types_panneau, style="Card.TFrame")
        form_card.pack(fill="x", pady=(12, 10))

        ttk.Label(form_card, text="Gestion des types de panneaux", style="Section.TLabel").grid(
            row=0, column=0, columnspan=7, sticky="w", padx=14, pady=(12, 8)
        )

        self.var_type_libelle = tk.StringVar()
        self.var_type_ratio = tk.StringVar()
        self.var_type_energie = tk.StringVar()
        self.var_type_prix = tk.StringVar()

        add_labeled_entry(
            form_card,
            row=1,
            label_col=0,
            entry_col=1,
            label_text="Libelle",
            variable=self.var_type_libelle,
            width=20,
        )
        add_labeled_entry(
            form_card,
            row=1,
            label_col=2,
            entry_col=3,
            label_text="Ratio (0-1)",
            variable=self.var_type_ratio,
            width=10,
        )
        add_labeled_entry(
            form_card,
            row=1,
            label_col=4,
            entry_col=5,
            label_text="Energie W(Wh)",
            variable=self.var_type_energie,
            width=10,
        )
        add_labeled_entry(
            form_card,
            row=1,
            label_col=6,
            entry_col=7,
            label_text="Prix ( Ar)",
            variable=self.var_type_prix,
            width=10,
        )

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
        configure_treeview_columns(
            self.tree_types_panneau,
            [
                ("id", 70),
                ("libelle", 200),
                ("ratio", 120),
                ("energie", 120),
                ("prix", 120),
            ],
        )

        self.tree_types_panneau.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_types_panneau.bind("<Double-1>", self.charger_type_pour_edition)

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
            self.rafraichir_prix_energie()
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
            self.rafraichir_prix_energie()
            self.annuler_edition_type()
        except Exception as exc:
            messagebox.showerror("Type Panneau", str(exc))

    def charger_type_pour_edition(self, _event):
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
