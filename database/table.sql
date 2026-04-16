-- Schema PostgreSQL en francais pour le dimensionnement solaire
-- Logique metier:
-- MATIN 06:00-17:00: panneau seul (appareils + charge batterie)
-- SOIR 17:00-19:00: panneau seul, avec 50% de puissance disponible
-- NUIT 19:00-06:00: batterie seule
-- Cas pratique: panneau utile = 40% theorique, batterie = +50% sur besoin nuit

BEGIN;

CREATE TABLE parametre_calcul (
    id BIGSERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    facteur_panneau_pratique NUMERIC(5,4) NOT NULL DEFAULT 0.4000 CHECK (facteur_panneau_pratique > 0 AND facteur_panneau_pratique <= 1),
    facteur_panneau_soir NUMERIC(5,4) NOT NULL DEFAULT 0.5000 CHECK (facteur_panneau_soir > 0 AND facteur_panneau_soir <= 1),
    facteur_marge_batterie NUMERIC(5,4) NOT NULL DEFAULT 1.5000 CHECK (facteur_marge_batterie >= 1),
    duree_matin_h NUMERIC(6,2) NOT NULL DEFAULT 11.00 CHECK (duree_matin_h > 0),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tranche_horaire (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    facteur_disponibilite_panneau NUMERIC(5,4) NOT NULL CHECK (facteur_disponibilite_panneau >= 0 AND facteur_disponibilite_panneau <= 1),
    source_energie TEXT NOT NULL CHECK (source_energie IN ('PANNEAU', 'BATTERIE')),
    ordre_affichage SMALLINT NOT NULL CHECK (ordre_affichage > 0),
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE appareil (
    id BIGSERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    puissance_nominale_w NUMERIC(10,2) NOT NULL CHECK (puissance_nominale_w > 0),
    description TEXT,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (nom, puissance_nominale_w)
);

CREATE TABLE session_dimensionnement (
    id BIGSERIAL PRIMARY KEY,
    titre TEXT NOT NULL,
    parametre_calcul_id BIGINT NOT NULL REFERENCES parametre_calcul(id),
    notes TEXT,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE utilisation_appareil (
    id BIGSERIAL PRIMARY KEY,
    session_dimensionnement_id BIGINT NOT NULL REFERENCES session_dimensionnement(id) ON DELETE CASCADE,
    appareil_id BIGINT NOT NULL REFERENCES appareil(id),
    date_heure_debut TIMESTAMPTZ NOT NULL,
    date_heure_fin TIMESTAMPTZ NOT NULL,
    duree_h NUMERIC(10,4) GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (date_heure_fin - date_heure_debut)) / 3600.0) STORED,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (date_heure_fin > date_heure_debut)
);

CREATE TABLE segment_utilisation (
    id BIGSERIAL PRIMARY KEY,
    session_dimensionnement_id BIGINT NOT NULL REFERENCES session_dimensionnement(id) ON DELETE CASCADE,
    utilisation_appareil_id BIGINT NOT NULL REFERENCES utilisation_appareil(id) ON DELETE CASCADE,
    tranche_horaire_id BIGINT NOT NULL REFERENCES tranche_horaire(id),
    date_heure_debut_segment TIMESTAMPTZ NOT NULL,
    date_heure_fin_segment TIMESTAMPTZ NOT NULL,
    duree_h NUMERIC(10,4) GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (date_heure_fin_segment - date_heure_debut_segment)) / 3600.0) STORED,
    puissance_w NUMERIC(10,2) NOT NULL CHECK (puissance_w > 0),
    energie_wh NUMERIC(14,3) GENERATED ALWAYS AS (puissance_w * duree_h) STORED,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (date_heure_fin_segment > date_heure_debut_segment)
);

CREATE TABLE bilan_tranche_session (
    id BIGSERIAL PRIMARY KEY,
    session_dimensionnement_id BIGINT NOT NULL REFERENCES session_dimensionnement(id) ON DELETE CASCADE,
    tranche_horaire_id BIGINT NOT NULL REFERENCES tranche_horaire(id),
    energie_consommation_wh NUMERIC(14,3) NOT NULL CHECK (energie_consommation_wh >= 0),
    puissance_pic_w NUMERIC(12,3) NOT NULL CHECK (puissance_pic_w >= 0),
    energie_fournie_panneau_wh NUMERIC(14,3) NOT NULL CHECK (energie_fournie_panneau_wh >= 0),
    energie_fournie_batterie_wh NUMERIC(14,3) NOT NULL CHECK (energie_fournie_batterie_wh >= 0),
    energie_charge_batterie_wh NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (energie_charge_batterie_wh >= 0),
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (session_dimensionnement_id, tranche_horaire_id)
);

CREATE TABLE resultat_theorique (
    id BIGSERIAL PRIMARY KEY,
    session_dimensionnement_id BIGINT NOT NULL UNIQUE REFERENCES session_dimensionnement(id) ON DELETE CASCADE,
    energie_batterie_theorique_wh NUMERIC(14,3) NOT NULL CHECK (energie_batterie_theorique_wh >= 0),
    puissance_charge_batterie_theorique_w NUMERIC(12,3) NOT NULL CHECK (puissance_charge_batterie_theorique_w >= 0),
    puissance_panneau_matin_theorique_w NUMERIC(12,3) NOT NULL CHECK (puissance_panneau_matin_theorique_w >= 0),
    puissance_panneau_soir_theorique_w NUMERIC(12,3) NOT NULL CHECK (puissance_panneau_soir_theorique_w >= 0),
    puissance_panneau_theorique_w NUMERIC(12,3) NOT NULL CHECK (puissance_panneau_theorique_w > 0),
    energie_totale_journaliere_wh NUMERIC(14,3) NOT NULL CHECK (energie_totale_journaliere_wh >= 0),
    alerte_recharge_matin_insuffisante BOOLEAN NOT NULL DEFAULT FALSE,
    alerte_couverture_soir_insuffisante BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE resultat_pratique (
    id BIGSERIAL PRIMARY KEY,
    session_dimensionnement_id BIGINT NOT NULL UNIQUE REFERENCES session_dimensionnement(id) ON DELETE CASCADE,
    puissance_panneau_achat_w NUMERIC(12,3) NOT NULL CHECK (puissance_panneau_achat_w > 0),
    puissance_panneau_achat_kw NUMERIC(12,4) GENERATED ALWAYS AS (puissance_panneau_achat_w / 1000.0) STORED,
    capacite_batterie_achat_wh NUMERIC(14,3) NOT NULL CHECK (capacite_batterie_achat_wh >= 0),
    capacite_batterie_achat_kwh NUMERIC(14,4) GENERATED ALWAYS AS (capacite_batterie_achat_wh / 1000.0) STORED,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_session_dimensionnement_parametre ON session_dimensionnement(parametre_calcul_id);
CREATE INDEX idx_utilisation_appareil_session ON utilisation_appareil(session_dimensionnement_id);
CREATE INDEX idx_utilisation_appareil_appareil ON utilisation_appareil(appareil_id);
CREATE INDEX idx_segment_utilisation_session ON segment_utilisation(session_dimensionnement_id);
CREATE INDEX idx_segment_utilisation_utilisation ON segment_utilisation(utilisation_appareil_id);
CREATE INDEX idx_segment_utilisation_tranche ON segment_utilisation(tranche_horaire_id);
CREATE INDEX idx_bilan_tranche_session_session ON bilan_tranche_session(session_dimensionnement_id);

-- Initialisation des tranches fixes
INSERT INTO tranche_horaire (code, nom, heure_debut, heure_fin, facteur_disponibilite_panneau, source_energie, ordre_affichage)
VALUES
    ('MATIN', 'Matin', '06:00', '17:00', 1.0000, 'PANNEAU', 1),
    ('SOIR',  'Soir',  '17:00', '19:00', 0.5000, 'PANNEAU', 2),
    ('NUIT',  'Nuit',  '19:00', '06:00', 0.0000, 'BATTERIE', 3)
ON CONFLICT (code) DO NOTHING;

COMMIT;
