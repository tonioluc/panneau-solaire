from __future__ import annotations

from panneau_solaire.models import (
    ApplianceUsage,
    CalculationParameters,
    CalculationResult,
    Tranche,
    TrancheSummary,
)


def validate_usage(usage: ApplianceUsage) -> None:
    if not usage.name.strip():
        raise ValueError("Le nom de l'appareil est obligatoire.")
    if usage.power_watt <= 0:
        raise ValueError("La puissance doit etre superieure a zero.")
    if usage.duration_hours <= 0:
        raise ValueError("La duree doit etre superieure a zero.")


def summarize_by_tranche(usages: list[ApplianceUsage]) -> dict[Tranche, TrancheSummary]:
    summaries = {
        Tranche.MORNING: TrancheSummary(),
        Tranche.EVENING: TrancheSummary(),
        Tranche.NIGHT: TrancheSummary(),
    }

    for usage in usages:
        validate_usage(usage)
        summary = summaries[usage.tranche]
        summary.total_power_watt += usage.power_watt
        summary.total_duration_hours += usage.duration_hours
        summary.total_energy_wh += usage.energy_wh
        summary.usages.append(usage)

    return summaries


def calculate_recommendations(
    usages: list[ApplianceUsage],
    params: CalculationParameters | None = None,
) -> CalculationResult:
    params = params or CalculationParameters()
    summaries = summarize_by_tranche(usages)

    morning = summaries[Tranche.MORNING]
    evening = summaries[Tranche.EVENING]
    night = summaries[Tranche.NIGHT]

    total_energy_wh = morning.total_energy_wh + evening.total_energy_wh + night.total_energy_wh
    total_energy_kwh = total_energy_wh / 1000.0

    theoretical_panel_watt = max(
        morning.total_power_watt,
        evening.total_power_watt / params.evening_panel_factor if evening.total_power_watt else 0.0,
    )
    practical_panel_watt = theoretical_panel_watt / params.panel_efficiency if theoretical_panel_watt else 0.0

    theoretical_battery_kwh = (evening.total_energy_wh + night.total_energy_wh) / 1000.0
    practical_battery_kwh = theoretical_battery_kwh * (1.0 + params.battery_margin)

    return CalculationResult(
        total_energy_wh=total_energy_wh,
        total_energy_kwh=total_energy_kwh,
        morning=morning,
        evening=evening,
        night=night,
        theoretical_panel_watt=theoretical_panel_watt,
        practical_panel_watt=practical_panel_watt,
        theoretical_battery_kwh=theoretical_battery_kwh,
        practical_battery_kwh=practical_battery_kwh,
    )
