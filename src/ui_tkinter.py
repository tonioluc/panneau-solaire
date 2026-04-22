import tkinter as tk

from repository_sqlserver import RepositorySqlServer
from service_dimensionnement import ServiceDimensionnement
from theme_loader import ThemeLoader
from ui.entrees_mixin import EntreesMixin
from ui.layout_mixin import LayoutMixin
from ui.prix_energie_mixin import PrixEnergieMixin
from ui.resultats_mixin import ResultatsMixin
from ui.simulations_mixin import SimulationsMixin
from ui.types_panneau_mixin import TypesPanneauMixin


class ApplicationTk(
    LayoutMixin,
    SimulationsMixin,
    EntreesMixin,
    ResultatsMixin,
    TypesPanneauMixin,
    PrixEnergieMixin,
    tk.Tk,
):
    def __init__(self):
        super().__init__()
        self.title("SolarSim")
        self.geometry("1180x760")
        self.minsize(1100, 700)

        self.theme = ThemeLoader()
        self.personalized_layout = self.theme.has_user_theme
        self._configure_window_theme()

        self.repository = RepositorySqlServer()
        self.service = ServiceDimensionnement()

        self.simulation_active_id: int | None = None
        self.map_simulations: dict[str, int] = {}
        self.tranches_disponibles: list[str] = ["MATIN", "SOIR", "NUIT"]

        self.entree_en_edition_id: int | None = None
        self.result_labels: dict[str, tk.Label] = {}

        self.type_panneau_en_edition_id: int | None = None
        self.types_panneau_actuels: list = []
        self.map_types_panneau: dict[str, int] = {}

        self.prix_energie_en_edition_id: int | None = None
        self.prix_energie_actuels: list = []
        self.majoration_heure_pointe_en_edition_id: int | None = None
        self.majorations_heure_pointe_actuelles: list = []

        self._build_ui()
        self._connect_db()
