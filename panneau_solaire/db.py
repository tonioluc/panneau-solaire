from __future__ import annotations

from datetime import datetime
import os

try:
    import pyodbc
except Exception:  # pragma: no cover - optional dependency in local dev
    pyodbc = None

from panneau_solaire.models import CalculationParameters, CalculationResult, ApplianceUsage


class SqlServerRepository:
    def __init__(self, connection_string: str | None = None) -> None:
        self.connection_string = connection_string or os.getenv("SQLSERVER_CONNECTION_STRING", "")

    def is_configured(self) -> bool:
        return bool(self.connection_string) and pyodbc is not None

    def save_analysis(
        self,
        analysis_name: str,
        usages: list[ApplianceUsage],
        parameters: CalculationParameters,
        result: CalculationResult,
    ) -> int:
        if not self.is_configured():
            raise RuntimeError("SQL Server non configure.")

        assert pyodbc is not None
        with pyodbc.connect(self.connection_string) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO analyses (name, created_at)
                OUTPUT INSERTED.id
                VALUES (?, ?)
                """,
                analysis_name,
                datetime.utcnow(),
            )
            analysis_id = int(cursor.fetchone()[0])

            cursor.execute(
                """
                INSERT INTO calculation_parameters (
                    analysis_id, panel_efficiency, evening_panel_factor, battery_margin
                ) VALUES (?, ?, ?, ?)
                """,
                analysis_id,
                parameters.panel_efficiency,
                parameters.evening_panel_factor,
                parameters.battery_margin,
            )

            for usage in usages:
                cursor.execute(
                    """
                    INSERT INTO appliance_usages (
                        analysis_id, name, power_watt, duration_hours, tranche
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    analysis_id,
                    usage.name,
                    usage.power_watt,
                    usage.duration_hours,
                    usage.tranche.value,
                )

            cursor.execute(
                """
                INSERT INTO calculation_results (
                    analysis_id,
                    total_energy_wh,
                    total_energy_kwh,
                    morning_energy_wh,
                    evening_energy_wh,
                    night_energy_wh,
                    theoretical_panel_watt,
                    practical_panel_watt,
                    theoretical_battery_kwh,
                    practical_battery_kwh
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                analysis_id,
                result.total_energy_wh,
                result.total_energy_kwh,
                result.morning.total_energy_wh,
                result.evening.total_energy_wh,
                result.night.total_energy_wh,
                result.theoretical_panel_watt,
                result.practical_panel_watt,
                result.theoretical_battery_kwh,
                result.practical_battery_kwh,
            )

            connection.commit()
            return analysis_id
