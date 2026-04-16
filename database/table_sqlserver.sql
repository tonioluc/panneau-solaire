-- Schema SQL Server minimal (creation manuelle)
-- Stockage uniquement des informations d'entree de simulation

IF OBJECT_ID('dbo.simulation_entree', 'U') IS NOT NULL
    DROP TABLE dbo.simulation_entree;
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

CREATE TABLE dbo.simulation_entree (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    simulation_id BIGINT NOT NULL,
    materiel NVARCHAR(200) NOT NULL,
    puissance_w DECIMAL(10,2) NOT NULL,
    id_tranche_heure BIGINT NOT NULL,
    duree_h DECIMAL(10,2) NOT NULL,
    cree_le DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_simulation_entree_simulation
        FOREIGN KEY (simulation_id) REFERENCES dbo.simulation(id) ON DELETE CASCADE,
    CONSTRAINT fk_simulation_entree_tranche
        FOREIGN KEY (id_tranche_heure) REFERENCES dbo.tranche_heure(id),
    CONSTRAINT ck_simulation_entree_puissance
        CHECK (puissance_w > 0),
    CONSTRAINT ck_simulation_entree_duree
        CHECK (duree_h > 0)
);
GO

CREATE INDEX idx_simulation_entree_simulation_id
    ON dbo.simulation_entree(simulation_id);
GO

CREATE INDEX idx_simulation_entree_id_tranche_heure
    ON dbo.simulation_entree(id_tranche_heure);
GO

CREATE INDEX idx_parametre_code
    ON dbo.parametre(code);
GO
