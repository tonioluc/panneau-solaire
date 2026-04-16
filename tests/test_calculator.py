import unittest

from panneau_solaire.calculator import calculate_recommendations
from panneau_solaire.models import ApplianceUsage, Tranche


class CalculatorTests(unittest.TestCase):
    def test_calculates_recommendations(self) -> None:
        usages = [
            ApplianceUsage("TV", 75, 2, Tranche.MORNING),
            ApplianceUsage("TV", 75, 3, Tranche.EVENING),
            ApplianceUsage("Frigo", 65, 3, Tranche.MORNING),
            ApplianceUsage("Ordi", 85, 1, Tranche.MORNING),
            ApplianceUsage("Ordi", 85, 4, Tranche.EVENING),
        ]

        result = calculate_recommendations(usages)

        self.assertAlmostEqual(result.total_energy_wh, 995.0)
        self.assertAlmostEqual(result.morning.total_power_watt, 225.0)
        self.assertAlmostEqual(result.evening.total_power_watt, 160.0)
        self.assertAlmostEqual(result.theoretical_panel_watt, 320.0)
        self.assertAlmostEqual(result.practical_panel_watt, 800.0)
        self.assertAlmostEqual(result.theoretical_battery_kwh, 0.565)
        self.assertAlmostEqual(result.practical_battery_kwh, 0.8475)


if __name__ == "__main__":
    unittest.main()
