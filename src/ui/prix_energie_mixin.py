import tkinter as tk
from tkinter import messagebox, ttk

from .reusable_widgets import add_labeled_entry, configure_treeview_columns


class PrixEnergieMixin:
    def _build_tab_prix_energie(self):
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

        add_labeled_entry(
            form_card,
            row=1,
            label_col=2,
            entry_col=3,
            label_text="Prix (Ar/Wh)",
            variable=self.var_prix_wh,
            width=14,
        )

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
        configure_treeview_columns(
            self.tree_prix_energie,
            [
                ("id", 90),
                ("code_jour", 200),
                ("prix_wh", 180),
            ],
        )

        self.tree_prix_energie.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_prix_energie.bind("<Double-1>", self.charger_prix_pour_edition)

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
