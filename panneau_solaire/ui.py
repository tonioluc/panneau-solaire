from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from panneau_solaire.calculator import calculate_recommendations, validate_usage
from panneau_solaire.db import SqlServerRepository
from panneau_solaire.models import ApplianceUsage, CalculationParameters, Tranche, TRANCHE_LABELS


class SolarApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Panneau solaire - dimensionnement")
        self.root.geometry("1050x700")
        self.root.minsize(980, 640)

        self.repository = SqlServerRepository()
        self.usages: list[ApplianceUsage] = []
        self.last_result = None

        self._build_ui()

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        title = ttk.Label(self.root, text="Dimensionnement panneau solaire", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=18, pady=(14, 8))

        main = ttk.Frame(self.root, padding=16)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = ttk.LabelFrame(main, text="Saisie")
        right = ttk.LabelFrame(main, text="Resultats")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=4)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=4)

        self._build_input_panel(left)
        self._build_result_panel(right)

    def _build_input_panel(self, parent: ttk.LabelFrame) -> None:
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Nom analyse").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
        self.analysis_name_var = tk.StringVar(value="Analyse 1")
        ttk.Entry(parent, textvariable=self.analysis_name_var).grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 6))

        ttk.Label(parent, text="Appareil").grid(row=1, column=0, sticky="w", padx=12, pady=6)
        self.device_name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.device_name_var).grid(row=1, column=1, sticky="ew", padx=12, pady=6)

        ttk.Label(parent, text="Puissance (W)").grid(row=2, column=0, sticky="w", padx=12, pady=6)
        self.power_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.power_var).grid(row=2, column=1, sticky="ew", padx=12, pady=6)

        ttk.Label(parent, text="Duree (h)").grid(row=3, column=0, sticky="w", padx=12, pady=6)
        self.duration_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.duration_var).grid(row=3, column=1, sticky="ew", padx=12, pady=6)

        ttk.Label(parent, text="Tranche").grid(row=4, column=0, sticky="w", padx=12, pady=6)
        self.tranche_var = tk.StringVar(value=Tranche.MORNING.value)
        self.tranche_combo = ttk.Combobox(
            parent,
            textvariable=self.tranche_var,
            values=[Tranche.MORNING.value, Tranche.EVENING.value, Tranche.NIGHT.value],
            state="readonly",
        )
        self.tranche_combo.grid(row=4, column=1, sticky="ew", padx=12, pady=6)
        self.tranche_combo.bind("<<ComboboxSelected>>", self._refresh_tranche_hint)

        self.tranche_hint_var = tk.StringVar(value=TRANCHE_LABELS[Tranche.MORNING])
        ttk.Label(parent, textvariable=self.tranche_hint_var, foreground="#555").grid(
            row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 8)
        )

        buttons = ttk.Frame(parent)
        buttons.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 10))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        buttons.columnconfigure(2, weight=1)
        ttk.Button(buttons, text="Ajouter", command=self.add_usage).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(buttons, text="Supprimer", command=self.remove_usage).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(buttons, text="Calculer", command=self.calculate).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        columns = ("name", "power", "duration", "tranche", "energy")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="Appareil")
        self.tree.heading("power", text="Puissance W")
        self.tree.heading("duration", text="Duree h")
        self.tree.heading("tranche", text="Tranche")
        self.tree.heading("energy", text="Energie Wh")
        self.tree.column("name", width=150)
        self.tree.column("power", width=95, anchor="e")
        self.tree.column("duration", width=80, anchor="e")
        self.tree.column("tranche", width=120)
        self.tree.column("energy", width=100, anchor="e")
        self.tree.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=12, pady=(6, 12))
        parent.rowconfigure(7, weight=1)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=7, column=2, sticky="ns", pady=(6, 12))

    def _build_result_panel(self, parent: ttk.LabelFrame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        self.summary_var = tk.StringVar(value="Ajoute au moins un appareil puis lance le calcul.")
        ttk.Label(parent, textvariable=self.summary_var, wraplength=420, justify="left").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 8)
        )

        self.result_text = tk.Text(parent, height=24, wrap="word")
        self.result_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.result_text.insert("1.0", "Les resultats s'afficheront ici.")
        self.result_text.configure(state="disabled")

        footer = ttk.Frame(parent)
        footer.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        footer.columnconfigure(0, weight=1)
        ttk.Button(footer, text="Enregistrer SQL Server", command=self.save_to_database).grid(row=0, column=0, sticky="e")

    def _refresh_tranche_hint(self, _event: object | None = None) -> None:
        tranche_value = Tranche(self.tranche_var.get())
        self.tranche_hint_var.set(TRANCHE_LABELS[tranche_value])

    def add_usage(self) -> None:
        try:
            name = self.device_name_var.get().strip()
            power_watt = float(self.power_var.get())
            duration_hours = float(self.duration_var.get())
            tranche = Tranche(self.tranche_var.get())

            usage = ApplianceUsage(
                name=name,
                power_watt=power_watt,
                duration_hours=duration_hours,
                tranche=tranche,
            )
            validate_usage(usage)
            self.usages.append(usage)
            self._refresh_tree()
            self.device_name_var.set("")
            self.power_var.set("")
            self.duration_var.set("")
        except ValueError as error:
            messagebox.showerror("Validation", str(error))

    def remove_usage(self) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            return
        index = self.tree.index(selected_item[0])
        del self.usages[index]
        self._refresh_tree()

    def _refresh_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for usage in self.usages:
            self.tree.insert(
                "",
                "end",
                values=(
                    usage.name,
                    f"{usage.power_watt:.2f}",
                    f"{usage.duration_hours:.2f}",
                    TRANCHE_LABELS[usage.tranche],
                    f"{usage.energy_wh:.2f}",
                ),
            )

    def calculate(self) -> None:
        if not self.usages:
            messagebox.showwarning("Calcul", "Ajoute au moins un appareil avant de calculer.")
            return

        try:
            result = calculate_recommendations(self.usages, CalculationParameters())
            self.last_result = result
            self._render_result(result)
        except ValueError as error:
            messagebox.showerror("Calcul", str(error))

    def _render_result(self, result) -> None:
        lines = [
            f"Energie totale: {result.total_energy_wh:.2f} Wh ({result.total_energy_kwh:.2f} kWh)",
            "",
            f"Maraina: {result.morning.total_power_watt:.2f} W, {result.morning.total_energy_wh:.2f} Wh",
            f"Hariva: {result.evening.total_power_watt:.2f} W, {result.evening.total_energy_wh:.2f} Wh",
            f"Alina: {result.night.total_power_watt:.2f} W, {result.night.total_energy_wh:.2f} Wh",
            "",
            f"Panneau theorique: {result.theoretical_panel_watt:.2f} W",
            f"Panneau pratique: {result.practical_panel_watt:.2f} W",
            f"Batterie theorique: {result.theoretical_battery_kwh:.2f} kWh",
            f"Batterie pratique: {result.practical_battery_kwh:.2f} kWh",
        ]
        self.summary_var.set("Calcul termine. Les valeurs pratiques appliquent les coefficients du projet.")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(lines))
        self.result_text.configure(state="disabled")

    def save_to_database(self) -> None:
        if self.last_result is None:
            messagebox.showwarning("Enregistrement", "Lance d'abord un calcul.")
            return

        try:
            analysis_id = self.repository.save_analysis(
                analysis_name=self.analysis_name_var.get().strip() or "Analyse sans nom",
                usages=self.usages,
                parameters=CalculationParameters(),
                result=self.last_result,
            )
            messagebox.showinfo("Enregistrement", f"Analyse enregistree avec l'id {analysis_id}.")
        except Exception as error:
            messagebox.showerror("SQL Server", str(error))
