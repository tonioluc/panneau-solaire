-- Schema SQL Server minimal (creation manuelle)
-- Stockage uniquement des informations d'entree de simulation

-- effacer les tables si elles existent deja
drop table if exists dbo.simulation_entree;
drop table if exists dbo.type_panneau;
drop table if exists dbo.prix_energie_non_utilisee;
drop table if exists dbo.parametre;
drop table if exists dbo.tranche_heure;
drop table if exists dbo.simulation;
GO

IF OBJECT_ID('dbo.simulation_entree', 'U') IS NOT NULL
    DROP TABLE dbo.simulation_entree;
GO

IF OBJECT_ID('dbo.type_panneau', 'U') IS NOT NULL
    DROP TABLE dbo.type_panneau;
GO

IF OBJECT_ID('dbo.prix_energie_non_utilisee', 'U') IS NOT NULL
    DROP TABLE dbo.prix_energie_non_utilisee;
GO

IF OBJECT_ID('dbo.parametre', 'U') IS NOT NULL
    DROP TABLE dbo.parametre;
GO

IF OBJECT_ID('dbo.tranche_heure', 'U') IS NOT NULL
    DROP TABLE dbo.tranche_heure;
GO

IF OBJECT_ID('dbo.simulation', 'U') IS NOT NULL
    DROP TABLE dbo.simulation;
GO

CREATE TABLE dbo.simulation (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    titre NVARCHAR(200) NOT NULL,
    notes NVARCHAR(500) NULL,
    cree_le DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE dbo.tranche_heure (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    libelle NVARCHAR(20) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    CONSTRAINT uq_tranche_heure_libelle UNIQUE (libelle)
);
GO

CREATE TABLE dbo.parametre (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    code NVARCHAR(100) NOT NULL,
    description NVARCHAR(300) NULL,
    valeur DECIMAL(18,6) NOT NULL,
    CONSTRAINT uq_parametre_code UNIQUE (code)
);
GO

CREATE TABLE dbo.prix_energie_non_utilisee (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    code_jour NVARCHAR(20) NOT NULL,
    prix_wh DECIMAL(18,6) NOT NULL,
    cree_le DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_prix_energie_non_utilisee_code_jour UNIQUE (code_jour),
    CONSTRAINT ck_prix_energie_non_utilisee_code_jour CHECK (code_jour IN ('OUVRABLE', 'WEEKEND')),
    CONSTRAINT ck_prix_energie_non_utilisee_prix CHECK (prix_wh >= 0)
);
GO

CREATE TABLE dbo.simulation_entree (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    simulation_id BIGINT NOT NULL,
    materiel NVARCHAR(200) NOT NULL,
    puissance_w DECIMAL(10,2) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    cree_le DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_simulation_entree_simulation
        FOREIGN KEY (simulation_id) REFERENCES dbo.simulation(id) ON DELETE CASCADE,
    CONSTRAINT ck_simulation_entree_puissance
        CHECK (puissance_w > 0),
    CONSTRAINT ck_simulation_entree_heure_diff
        CHECK (heure_debut <> heure_fin)
);
GO

CREATE INDEX idx_simulation_entree_simulation_id
    ON dbo.simulation_entree(simulation_id);
GO

CREATE TABLE dbo.type_panneau (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    libelle NVARCHAR(100) NOT NULL,
    ratio_couverture DECIMAL(5,3) NOT NULL,
    energie_unitaire_wh DECIMAL(10,2) NOT NULL,
    prix_unitaire DECIMAL(10,2) NOT NULL,
    cree_le DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_type_panneau_libelle UNIQUE (libelle),
    CONSTRAINT ck_type_panneau_ratio CHECK (ratio_couverture > 0 AND ratio_couverture <= 1),
    CONSTRAINT ck_type_panneau_energie CHECK (energie_unitaire_wh > 0),
    CONSTRAINT ck_type_panneau_prix CHECK (prix_unitaire >= 0)
);
GO

CREATE INDEX idx_type_panneau_libelle
    ON dbo.type_panneau(libelle);
GO

CREATE INDEX idx_prix_energie_non_utilisee_code_jour
    ON dbo.prix_energie_non_utilisee(code_jour);
GO

CREATE INDEX idx_parametre_code
    ON dbo.parametre(code);
GO
