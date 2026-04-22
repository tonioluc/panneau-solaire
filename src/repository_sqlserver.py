import os
from datetime import time

import pyodbc

from modeles import EntreeSimulation, MajorationHeurePointe, PrixEnergieNonUtilisee, Simulation, TrancheHoraire, TypePanneau


class RepositorySqlServer:
    def __init__(self):
        self.serveur = os.getenv("DB_SERVER", "localhost")
        self.port = os.getenv("DB_PORT", "1433")
        self.base = os.getenv("DB_NAME", "solaire_db")
        self.utilisateur = os.getenv("DB_USER", "sa")
        self.mot_de_passe = os.getenv("DB_PASSWORD", "admin@12345")
        self.driver_force = os.getenv("DB_DRIVER", "")
        self.cnxn: pyodbc.Connection | None = None

    def _driver_sql_server(self) -> str:
        drivers = pyodbc.drivers()
        if self.driver_force and self.driver_force in drivers:
            return self.driver_force

        for candidat in ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]:
            if candidat in drivers:
                return candidat

        for driver in drivers:
            if "SQL Server" in driver:
                return driver

        raise RuntimeError("Aucun driver ODBC SQL Server detecte")

    def _chaine_connexion(self, base: str) -> str:
        driver = self._driver_sql_server()
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.serveur},{self.port};"
            f"DATABASE={base};"
            f"UID={self.utilisateur};"
            f"PWD={self.mot_de_passe};"
            "Encrypt=no;TrustServerCertificate=yes;"
        )

    def connecter(self):
        self.cnxn = pyodbc.connect(self._chaine_connexion(self.base), timeout=5)
        self.cnxn.autocommit = False

    def fermer(self):
        if self.cnxn is not None:
            self.cnxn.close()
            self.cnxn = None

    def _executer(self, sql: str, params=None):
        if self.cnxn is None:
            raise RuntimeError("La connexion SQL Server n'est pas active")
        cur = self.cnxn.cursor()
        cur.execute(sql, params or [])
        return cur

    def lister_simulations(self) -> list[Simulation]:
        cur = self._executer(
            "SELECT id, titre, ISNULL(notes, '') FROM dbo.simulation ORDER BY id DESC"
        )
        return [Simulation(int(r[0]), str(r[1]), str(r[2])) for r in cur.fetchall()]

    def lister_tranches(self) -> list[tuple[int, str]]:
        cur = self._executer("SELECT id, libelle FROM dbo.tranche_heure ORDER BY id")
        return [(int(r[0]), str(r[1])) for r in cur.fetchall()]

    def lister_tranches_detail(self) -> list[TrancheHoraire]:
        cur = self._executer(
            "SELECT id, libelle, heure_debut, heure_fin FROM dbo.tranche_heure ORDER BY id"
        )
        return [
            TrancheHoraire(
                id=int(r[0]),
                libelle=str(r[1]),
                heure_debut=self._format_time(r[2]),
                heure_fin=self._format_time(r[3]),
            )
            for r in cur.fetchall()
        ]

    def _format_time(self, value) -> str:
        if isinstance(value, time):
            return value.strftime("%H:%M")
        text = str(value)
        return text[:5] if len(text) >= 5 else text

    def charger_parametres(self) -> dict[str, float]:
        cur = self._executer("SELECT code, valeur FROM dbo.parametre")
        base = {
            "FACTEUR_PANNEAU_PRATIQUE": 0.4,
            "FACTEUR_PANNEAU_SOIR": 0.5,
            "FACTEUR_MARGE_BATTERIE": 1.5,
            "DUREE_MATIN_H": 11.0,
            "RATIO_COUVERTURE_PANNEAU_40": 0.4,
            "RATIO_COUVERTURE_PANNEAU_30": 0.3,
        }
        for code, valeur in cur.fetchall():
            base[str(code)] = float(valeur)
        return base

    def charger_prix_energie_non_utilisee(self) -> dict[int, dict[str, float]]:
        cur = self._executer(
            """
            SELECT type_panneau_id, code_jour, prix_wh
            FROM dbo.prix_energie_non_utilisee
            """
        )
        base: dict[int, dict[str, float]] = {}
        for type_panneau_id, code_jour, prix_wh in cur.fetchall():
            type_id = int(type_panneau_id)
            if type_id not in base:
                base[type_id] = {"OUVRABLE": 0.0, "WEEKEND": 0.0}
            base[type_id][str(code_jour).upper().strip()] = float(prix_wh)
        return base

    def charger_majorations_heure_pointe(self) -> dict[str, list[tuple[str, str, float]]]:
        cur = self._executer(
            """
            SELECT code_jour, heure_debut, heure_fin, taux_majoration
            FROM dbo.majoration_heure_pointe
            """
        )
        base: dict[str, list[tuple[str, str, float]]] = {
            "OUVRABLE": [],
            "WEEKEND": [],
        }
        for code_jour, heure_debut, heure_fin, taux_majoration in cur.fetchall():
            key = str(code_jour).upper().strip()
            if key not in base:
                base[key] = []
            base[key].append(
                (
                    self._format_time(heure_debut),
                    self._format_time(heure_fin),
                    float(taux_majoration),
                )
            )
        return base

    def lister_prix_energie_non_utilisee(self) -> list[PrixEnergieNonUtilisee]:
        cur = self._executer(
            """
            SELECT p.id, p.type_panneau_id, t.libelle, p.code_jour, p.prix_wh
            FROM dbo.prix_energie_non_utilisee p
            INNER JOIN dbo.type_panneau t ON t.id = p.type_panneau_id
            ORDER BY t.libelle, p.code_jour
            """
        )
        return [
            PrixEnergieNonUtilisee(
                id=int(r[0]),
                type_panneau_id=int(r[1]),
                type_panneau_libelle=str(r[2]),
                code_jour=str(r[3]),
                prix_wh=float(r[4]),
            )
            for r in cur.fetchall()
        ]

    def creer_prix_energie_non_utilisee(self, type_panneau_id: int, code_jour: str, prix_wh: float) -> int:
        cur = self._executer(
            """
            INSERT INTO dbo.prix_energie_non_utilisee (type_panneau_id, code_jour, prix_wh)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
            """,
            [type_panneau_id, code_jour.upper().strip(), prix_wh],
        )
        prix_id = int(cur.fetchone()[0])
        self.cnxn.commit()
        return prix_id

    def modifier_prix_energie_non_utilisee(self, prix_id: int, type_panneau_id: int, code_jour: str, prix_wh: float):
        self._executer(
            """
            UPDATE dbo.prix_energie_non_utilisee
            SET type_panneau_id = ?, code_jour = ?, prix_wh = ?
            WHERE id = ?
            """,
            [type_panneau_id, code_jour.upper().strip(), prix_wh, prix_id],
        )
        self.cnxn.commit()

    def supprimer_prix_energie_non_utilisee(self, prix_id: int):
        self._executer("DELETE FROM dbo.prix_energie_non_utilisee WHERE id = ?", [prix_id])
        self.cnxn.commit()

    def lister_majorations_heure_pointe(self) -> list[MajorationHeurePointe]:
        cur = self._executer(
            """
            SELECT id, code_jour, heure_debut, heure_fin, taux_majoration
            FROM dbo.majoration_heure_pointe
            ORDER BY code_jour, heure_debut
            """
        )
        return [
            MajorationHeurePointe(
                id=int(r[0]),
                code_jour=str(r[1]),
                heure_debut=self._format_time(r[2]),
                heure_fin=self._format_time(r[3]),
                taux_majoration=float(r[4]),
            )
            for r in cur.fetchall()
        ]

    def creer_majoration_heure_pointe(
        self,
        code_jour: str,
        heure_debut: str,
        heure_fin: str,
        taux_majoration: float,
    ) -> int:
        cur = self._executer(
            """
            INSERT INTO dbo.majoration_heure_pointe (code_jour, heure_debut, heure_fin, taux_majoration)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
            """,
            [code_jour.upper().strip(), heure_debut, heure_fin, taux_majoration],
        )
        majoration_id = int(cur.fetchone()[0])
        self.cnxn.commit()
        return majoration_id

    def modifier_majoration_heure_pointe(
        self,
        majoration_id: int,
        code_jour: str,
        heure_debut: str,
        heure_fin: str,
        taux_majoration: float,
    ):
        self._executer(
            """
            UPDATE dbo.majoration_heure_pointe
            SET code_jour = ?, heure_debut = ?, heure_fin = ?, taux_majoration = ?
            WHERE id = ?
            """,
            [code_jour.upper().strip(), heure_debut, heure_fin, taux_majoration, majoration_id],
        )
        self.cnxn.commit()

    def supprimer_majoration_heure_pointe(self, majoration_id: int):
        self._executer("DELETE FROM dbo.majoration_heure_pointe WHERE id = ?", [majoration_id])
        self.cnxn.commit()

    def creer_simulation(self, titre: str, notes: str | None) -> int:
        cur = self._executer(
            """
            INSERT INTO dbo.simulation (titre, notes)
            OUTPUT INSERTED.id
            VALUES (?, ?)
            """,
            [titre, notes],
        )
        simulation_id = int(cur.fetchone()[0])
        self.cnxn.commit()
        return simulation_id

    def supprimer_simulation(self, simulation_id: int):
        self._executer("DELETE FROM dbo.simulation_entree WHERE simulation_id = ?", [simulation_id])
        self._executer("DELETE FROM dbo.simulation WHERE id = ?", [simulation_id])
        self.cnxn.commit()

    def lister_entrees(self, simulation_id: int) -> list[EntreeSimulation]:
        cur = self._executer(
            """
            SELECT se.id, se.simulation_id, se.materiel, se.puissance_w, se.heure_debut, se.heure_fin
            FROM dbo.simulation_entree se
            WHERE se.simulation_id = ?
            ORDER BY se.id
            """,
            [simulation_id],
        )
        return [
            EntreeSimulation(
                id=int(r[0]),
                simulation_id=int(r[1]),
                materiel=str(r[2]),
                puissance_w=float(r[3]),
                heure_debut=self._format_time(r[4]),
                heure_fin=self._format_time(r[5]),
            )
            for r in cur.fetchall()
        ]

    def ajouter_entree(
        self,
        simulation_id: int,
        materiel: str,
        puissance_w: float,
        heure_debut: str,
        heure_fin: str,
    ):
        self._executer(
            """
            INSERT INTO dbo.simulation_entree
            (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
            VALUES (?, ?, ?, ?, ?)
            """,
            [simulation_id, materiel, puissance_w, heure_debut, heure_fin],
        )
        self.cnxn.commit()

    def modifier_entree(
        self,
        entree_id: int,
        materiel: str,
        puissance_w: float,
        heure_debut: str,
        heure_fin: str,
    ):
        self._executer(
            """
            UPDATE dbo.simulation_entree
            SET materiel = ?, puissance_w = ?, heure_debut = ?, heure_fin = ?
            WHERE id = ?
            """,
            [materiel, puissance_w, heure_debut, heure_fin, entree_id],
        )
        self.cnxn.commit()

    def supprimer_entree(self, entree_id: int):
        self._executer("DELETE FROM dbo.simulation_entree WHERE id = ?", [entree_id])
        self.cnxn.commit()

    def commit(self):
        if self.cnxn is not None:
            self.cnxn.commit()

    def rollback(self):
        if self.cnxn is not None:
            self.cnxn.rollback()

    def lister_types_panneau(self) -> list[TypePanneau]:
        """Récupère tous les types de panneaux."""
        cur = self._executer(
            """
            SELECT id, libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire
            FROM dbo.type_panneau
            ORDER BY libelle
            """
        )
        return [
            TypePanneau(
                id=int(r[0]),
                libelle=str(r[1]),
                ratio_couverture=float(r[2]),
                energie_unitaire_wh=float(r[3]),
                prix_unitaire=float(r[4]),
            )
            for r in cur.fetchall()
        ]

    def creer_type_panneau(
        self,
        libelle: str,
        ratio_couverture: float,
        energie_unitaire_wh: float,
        prix_unitaire: float,
    ) -> int:
        """Crée un nouveau type de panneau."""
        cur = self._executer(
            """
            INSERT INTO dbo.type_panneau
            (libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
            """,
            [libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire],
        )
        type_id = int(cur.fetchone()[0])
        self.cnxn.commit()
        return type_id

    def modifier_type_panneau(
        self,
        type_id: int,
        libelle: str,
        ratio_couverture: float,
        energie_unitaire_wh: float,
        prix_unitaire: float,
    ):
        """Modifie un type de panneau existant."""
        self._executer(
            """
            UPDATE dbo.type_panneau
            SET libelle = ?, ratio_couverture = ?, energie_unitaire_wh = ?, prix_unitaire = ?
            WHERE id = ?
            """,
            [libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire, type_id],
        )
        self.cnxn.commit()

    def supprimer_type_panneau(self, type_id: int):
        """Supprime un type de panneau."""
        self._executer("DELETE FROM dbo.type_panneau WHERE id = ?", [type_id])
        self.cnxn.commit()
