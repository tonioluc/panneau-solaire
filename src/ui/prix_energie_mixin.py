import tkinter as tk
from tkinter import messagebox, ttk

from .reusable_widgets import add_labeled_entry, configure_treeview_columns


class PrixEnergieMixin:
    @staticmethod
    def _normaliser_hhmm(value: str) -> str:
        text = value.strip()
        parts = text.split(":")
        if len(parts) < 2:
            raise ValueError("Heure invalide. Format attendu HH:MM")
        h = int(parts[0])
        m = int(parts[1])
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError("Heure invalide. Utiliser HH:MM entre 00:00 et 23:59")
        return f"{h:02d}:{m:02d}"

    def _create_prix_energie_scrollable_content(self) -> ttk.Frame:
        canvas_bg = (
            self.theme.get("surface_container_lowest")
            if self.personalized_layout
            else self.theme.get("surface")
        )

        root = ttk.Frame(self.tab_prix_energie, style="App.TFrame")
        root.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            root,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = ttk.Frame(canvas, style="App.TFrame")
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        content.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(window_id, width=e.width),
        )

        def _bind_wheel(_event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel_linux)
            canvas.bind_all("<Button-5>", _on_mousewheel_linux)

        def _unbind_wheel(_event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        def _on_mousewheel(event):
            delta = -1 if event.delta > 0 else 1
            canvas.yview_scroll(delta, "units")

        def _on_mousewheel_linux(event):
            delta = -1 if event.num == 4 else 1
            canvas.yview_scroll(delta, "units")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        self._prix_energie_scroll_canvas = canvas
        return content

    def _build_tab_prix_energie(self):
        content = self._create_prix_energie_scrollable_content()

        form_card = ttk.Frame(content, style="Card.TFrame")
        form_card.pack(fill="x", pady=(12, 10))

        ttk.Label(form_card, text="Configuration prix energie non utilisee", style="Section.TLabel").grid(
            row=0, column=0, columnspan=8, sticky="w", padx=14, pady=(12, 8)
        )

        self.var_prix_type_panneau = tk.StringVar()
        self.var_prix_code_jour = tk.StringVar(value="OUVRABLE")
        self.var_prix_wh = tk.StringVar()

        ttk.Label(form_card, text="Type de panneau", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        self.cmb_prix_type_panneau = ttk.Combobox(
            form_card,
            textvariable=self.var_prix_type_panneau,
            values=(),
            width=28,
            state="readonly",
            style="App.TCombobox",
        )
        self.cmb_prix_type_panneau.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(form_card, text="Type de jour", style="Muted.TLabel").grid(row=1, column=2, padx=12, pady=6, sticky="w")
        self.cmb_prix_code_jour = ttk.Combobox(
            form_card,
            textvariable=self.var_prix_code_jour,
            values=("OUVRABLE", "WEEKEND"),
            width=16,
            state="readonly",
            style="App.TCombobox",
        )
        self.cmb_prix_code_jour.grid(row=1, column=3, padx=6, pady=6, sticky="w")

        add_labeled_entry(
            form_card,
            row=1,
            label_col=4,
            entry_col=5,
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
        self.btn_ajouter_prix.grid(row=1, column=6, padx=(10, 14), pady=6, sticky="e")

        actions = ttk.Frame(content, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(actions, text="Modifier prix", command=self.modifier_prix_energie, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Annuler edition", command=self.annuler_edition_prix, style="Ghost.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Supprimer prix", command=self.supprimer_prix_energie, style="Ghost.TButton").pack(side="left")

        table_card = ttk.Frame(content, style="WhiteCard.TFrame")
        table_card.pack(fill="x", pady=(0, 12))

        self.tree_prix_energie = ttk.Treeview(
            table_card,
            columns=("id", "type_panneau", "code_jour", "prix_wh"),
            show="headings",
            height=8,
            style="App.Treeview",
        )
        configure_treeview_columns(
            self.tree_prix_energie,
            [
                ("id", 90),
                ("type_panneau", 280),
                ("code_jour", 150),
                ("prix_wh", 180),
            ],
        )

        self.tree_prix_energie.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_prix_energie.bind("<Double-1>", self.charger_prix_pour_edition)

        majoration_form_card = ttk.Frame(content, style="Card.TFrame")
        majoration_form_card.pack(fill="x", pady=(0, 10))

        ttk.Label(majoration_form_card, text="Majoration heures de pointe", style="Section.TLabel").grid(
            row=0, column=0, columnspan=10, sticky="w", padx=14, pady=(12, 8)
        )

        self.var_majoration_code_jour = tk.StringVar(value="OUVRABLE")
        self.var_majoration_heure_debut = tk.StringVar(value="12:00")
        self.var_majoration_heure_fin = tk.StringVar(value="14:00")
        self.var_majoration_taux = tk.StringVar(value="5.0")

        ttk.Label(majoration_form_card, text="Type de jour", style="Muted.TLabel").grid(row=1, column=0, padx=12, pady=6, sticky="w")
        self.cmb_majoration_code_jour = ttk.Combobox(
            majoration_form_card,
            textvariable=self.var_majoration_code_jour,
            values=("OUVRABLE", "WEEKEND"),
            width=14,
            state="readonly",
            style="App.TCombobox",
        )
        self.cmb_majoration_code_jour.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        add_labeled_entry(
            majoration_form_card,
            row=1,
            label_col=2,
            entry_col=3,
            label_text="Heure debut",
            variable=self.var_majoration_heure_debut,
            width=10,
        )
        add_labeled_entry(
            majoration_form_card,
            row=1,
            label_col=4,
            entry_col=5,
            label_text="Heure fin",
            variable=self.var_majoration_heure_fin,
            width=10,
        )
        add_labeled_entry(
            majoration_form_card,
            row=1,
            label_col=6,
            entry_col=7,
            label_text="Majoration (%)",
            variable=self.var_majoration_taux,
            width=10,
        )

        self.btn_ajouter_majoration = ttk.Button(
            majoration_form_card,
            text="Ajouter",
            command=self.ajouter_majoration_heure_pointe,
            style="Primary.TButton",
        )
        self.btn_ajouter_majoration.grid(row=1, column=8, padx=(10, 14), pady=6, sticky="e")

        majoration_actions = ttk.Frame(content, style="App.TFrame")
        majoration_actions.pack(fill="x", pady=(0, 8))

        ttk.Button(
            majoration_actions,
            text="Modifier majoration",
            command=self.modifier_majoration_heure_pointe,
            style="Ghost.TButton",
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            majoration_actions,
            text="Annuler edition",
            command=self.annuler_edition_majoration,
            style="Ghost.TButton",
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            majoration_actions,
            text="Supprimer majoration",
            command=self.supprimer_majoration_heure_pointe,
            style="Ghost.TButton",
        ).pack(side="left")

        majoration_table_card = ttk.Frame(content, style="WhiteCard.TFrame")
        majoration_table_card.pack(fill="both", expand=True)

        self.tree_majoration_heure_pointe = ttk.Treeview(
            majoration_table_card,
            columns=("id", "code_jour", "heure_debut", "heure_fin", "taux_majoration"),
            show="headings",
            height=8,
            style="App.Treeview",
        )
        configure_treeview_columns(
            self.tree_majoration_heure_pointe,
            [
                ("id", 90),
                ("code_jour", 160),
                ("heure_debut", 160),
                ("heure_fin", 160),
                ("taux_majoration", 170),
            ],
        )
        self.tree_majoration_heure_pointe.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree_majoration_heure_pointe.bind("<Double-1>", self.charger_majoration_pour_edition)

    def ajouter_prix_energie(self):
        try:
            type_label = self.var_prix_type_panneau.get().strip()
            type_panneau_id = self.map_types_panneau.get(type_label)
            code_jour = self.var_prix_code_jour.get().strip().upper()
            prix_wh = float(self.var_prix_wh.get())

            if not type_label or type_panneau_id is None:
                raise ValueError("Type de panneau requis")
            if code_jour not in {"OUVRABLE", "WEEKEND"}:
                raise ValueError("Type de jour invalide (OUVRABLE ou WEEKEND)")
            if prix_wh < 0:
                raise ValueError("Prix doit etre >= 0")

            if self.prix_energie_en_edition_id is None:
                self.repository.creer_prix_energie_non_utilisee(type_panneau_id, code_jour, prix_wh)
            else:
                self.repository.modifier_prix_energie_non_utilisee(
                    self.prix_energie_en_edition_id,
                    type_panneau_id,
                    code_jour,
                    prix_wh,
                )
                self.prix_energie_en_edition_id = None

            self.annuler_edition_prix()
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
            self.var_prix_type_panneau.set(str(values[1]))
            self.var_prix_code_jour.set(str(values[2]))
            self.var_prix_wh.set(str(values[3]))
            self.btn_ajouter_prix.config(text="Mettre a jour")
        except Exception as exc:
            messagebox.showerror("Edition Prix", str(exc))

    def annuler_edition_prix(self):
        self.prix_energie_en_edition_id = None
        if self.cmb_prix_type_panneau["values"]:
            self.var_prix_type_panneau.set(str(self.cmb_prix_type_panneau["values"][0]))
        self.var_prix_code_jour.set("OUVRABLE")
        self.var_prix_wh.set("")
        self.btn_ajouter_prix.config(text="Ajouter")
        selection = self.tree_prix_energie.selection()
        if selection:
            self.tree_prix_energie.selection_remove(selection)

    def ajouter_majoration_heure_pointe(self):
        try:
            code_jour = self.var_majoration_code_jour.get().strip().upper()
            heure_debut = self._normaliser_hhmm(self.var_majoration_heure_debut.get())
            heure_fin = self._normaliser_hhmm(self.var_majoration_heure_fin.get())
            taux_majoration = float(self.var_majoration_taux.get())

            if code_jour not in {"OUVRABLE", "WEEKEND"}:
                raise ValueError("Type de jour invalide (OUVRABLE ou WEEKEND)")
            if heure_debut == heure_fin:
                raise ValueError("Heure debut et heure fin ne peuvent pas etre identiques")
            if taux_majoration < 0:
                raise ValueError("Majoration (%) doit etre >= 0")

            if self.majoration_heure_pointe_en_edition_id is None:
                self.repository.creer_majoration_heure_pointe(
                    code_jour,
                    heure_debut,
                    heure_fin,
                    taux_majoration,
                )
            else:
                self.repository.modifier_majoration_heure_pointe(
                    self.majoration_heure_pointe_en_edition_id,
                    code_jour,
                    heure_debut,
                    heure_fin,
                    taux_majoration,
                )
                self.majoration_heure_pointe_en_edition_id = None

            self.annuler_edition_majoration()
            self.rafraichir_majorations_heure_pointe()
        except Exception as exc:
            messagebox.showerror("Majoration pointe", str(exc))

    def modifier_majoration_heure_pointe(self):
        if self.majoration_heure_pointe_en_edition_id:
            self.ajouter_majoration_heure_pointe()
        else:
            messagebox.showinfo("Modification", "Double-cliquez sur une majoration pour l'editer")

    def supprimer_majoration_heure_pointe(self):
        try:
            selection = self.tree_majoration_heure_pointe.selection()
            if not selection:
                return
            majoration_id = int(self.tree_majoration_heure_pointe.item(selection[0])["values"][0])
            self.repository.supprimer_majoration_heure_pointe(majoration_id)
            self.rafraichir_majorations_heure_pointe()
            self.annuler_edition_majoration()
        except Exception as exc:
            messagebox.showerror("Majoration pointe", str(exc))

    def charger_majoration_pour_edition(self, _event):
        try:
            selection = self.tree_majoration_heure_pointe.selection()
            if not selection:
                return
            values = self.tree_majoration_heure_pointe.item(selection[0])["values"]
            self.majoration_heure_pointe_en_edition_id = int(values[0])
            self.var_majoration_code_jour.set(str(values[1]))
            self.var_majoration_heure_debut.set(str(values[2]))
            self.var_majoration_heure_fin.set(str(values[3]))
            self.var_majoration_taux.set(str(values[4]))
            self.btn_ajouter_majoration.config(text="Mettre a jour")
        except Exception as exc:
            messagebox.showerror("Edition majoration", str(exc))

    def annuler_edition_majoration(self):
        self.majoration_heure_pointe_en_edition_id = None
        self.var_majoration_code_jour.set("OUVRABLE")
        self.var_majoration_heure_debut.set("12:00")
        self.var_majoration_heure_fin.set("14:00")
        self.var_majoration_taux.set("5.0")
        self.btn_ajouter_majoration.config(text="Ajouter")
        selection = self.tree_majoration_heure_pointe.selection()
        if selection:
            self.tree_majoration_heure_pointe.selection_remove(selection)

    def _rafraichir_types_panneau_pour_prix(self):
        self.map_types_panneau.clear()
        types = self.repository.lister_types_panneau()
        labels = []
        for tp in types:
            label = f"{tp.id} - {tp.libelle}"
            labels.append(label)
            self.map_types_panneau[label] = tp.id

        self.cmb_prix_type_panneau["values"] = labels
        if labels and self.var_prix_type_panneau.get() not in labels:
            self.var_prix_type_panneau.set(labels[0])

    def rafraichir_prix_energie(self):
        if self.repository.cnxn is None:
            return

        try:
            self._rafraichir_types_panneau_pour_prix()
        except Exception:
            self.cmb_prix_type_panneau["values"] = ()

        for item in self.tree_prix_energie.get_children():
            self.tree_prix_energie.delete(item)
        try:
            self.prix_energie_actuels = self.repository.lister_prix_energie_non_utilisee()
            for prix in self.prix_energie_actuels:
                self.tree_prix_energie.insert(
                    "",
                    "end",
                    values=(
                        prix.id,
                        f"{prix.type_panneau_id} - {prix.type_panneau_libelle}",
                        prix.code_jour,
                        f"{prix.prix_wh:.4f}",
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Prix Energie", str(exc))

    def rafraichir_majorations_heure_pointe(self):
        if self.repository.cnxn is None:
            return

        for item in self.tree_majoration_heure_pointe.get_children():
            self.tree_majoration_heure_pointe.delete(item)

        try:
            self.majorations_heure_pointe_actuelles = self.repository.lister_majorations_heure_pointe()
            for majoration in self.majorations_heure_pointe_actuelles:
                self.tree_majoration_heure_pointe.insert(
                    "",
                    "end",
                    values=(
                        majoration.id,
                        majoration.code_jour,
                        majoration.heure_debut,
                        majoration.heure_fin,
                        f"{majoration.taux_majoration:.2f}",
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Majoration pointe", str(exc))
