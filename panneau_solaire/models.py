from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Tranche(str, Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"


TRANCHE_LABELS = {
    Tranche.MORNING: "Maraina (06h-17h)",
    Tranche.EVENING: "Hariva (17h-19h)",
    Tranche.NIGHT: "Alina (19h-06h)",
}


@dataclass(frozen=True)
class ApplianceUsage:
    name: str
    power_watt: float
    duration_hours: float
    tranche: Tranche

    @property
    def energy_wh(self) -> float:
        return self.power_watt * self.duration_hours


@dataclass(frozen=True)
class CalculationParameters:
    panel_efficiency: float = 0.40
    evening_panel_factor: float = 0.50
    battery_margin: float = 0.50


@dataclass
class TrancheSummary:
    total_power_watt: float = 0.0
    total_duration_hours: float = 0.0
    total_energy_wh: float = 0.0
    usages: list[ApplianceUsage] = field(default_factory=list)


@dataclass
class CalculationResult:
    total_energy_wh: float
    total_energy_kwh: float
    morning: TrancheSummary
    evening: TrancheSummary
    night: TrancheSummary
    theoretical_panel_watt: float
    practical_panel_watt: float
    theoretical_battery_kwh: float
    practical_battery_kwh: float
