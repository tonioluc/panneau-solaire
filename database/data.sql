-- Donnees initiales a lancer apres creation des tables

IF NOT EXISTS (SELECT 1 FROM dbo.tranche_heure WHERE libelle = 'MATIN')
BEGIN
    INSERT INTO dbo.tranche_heure (libelle, heure_debut, heure_fin)
    VALUES ('MATIN', '06:00:00', '17:00:00');
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.tranche_heure WHERE libelle = 'SOIR')
BEGIN
    INSERT INTO dbo.tranche_heure (libelle, heure_debut, heure_fin)
    VALUES ('SOIR', '17:00:00', '19:00:00');
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.tranche_heure WHERE libelle = 'NUIT')
BEGIN
    INSERT INTO dbo.tranche_heure (libelle, heure_debut, heure_fin)
    VALUES ('NUIT', '19:00:00', '06:00:00');
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.parametre WHERE code = 'FACTEUR_PANNEAU_PRATIQUE')
BEGIN
    INSERT INTO dbo.parametre (code, description, valeur)
    VALUES ('FACTEUR_PANNEAU_PRATIQUE', 'Rendement pratique du panneau (theorique -> pratique)', 0.4);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.parametre WHERE code = 'FACTEUR_PANNEAU_SOIR')
BEGIN
    INSERT INTO dbo.parametre (code, description, valeur)
    VALUES ('FACTEUR_PANNEAU_SOIR', 'Partie exploitable du panneau sur la tranche soir', 0.5);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.parametre WHERE code = 'FACTEUR_MARGE_BATTERIE')
BEGIN
    INSERT INTO dbo.parametre (code, description, valeur)
    VALUES ('FACTEUR_MARGE_BATTERIE', 'Marge pratique appliquee a la batterie theorique', 1.5);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.parametre WHERE code = 'DUREE_MATIN_H')
BEGIN
    INSERT INTO dbo.parametre (code, description, valeur)
    VALUES ('DUREE_MATIN_H', 'Duree de la tranche matin en heures pour la charge batterie', 11.0);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.parametre WHERE code = 'RATIO_COUVERTURE_PANNEAU_40')
BEGIN
    INSERT INTO dbo.parametre (code, description, valeur)
    VALUES ('RATIO_COUVERTURE_PANNEAU_40', 'Part exploitable du panneau pour la proposition 40%', 0.4);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.parametre WHERE code = 'RATIO_COUVERTURE_PANNEAU_30')
BEGIN
    INSERT INTO dbo.parametre (code, description, valeur)
    VALUES ('RATIO_COUVERTURE_PANNEAU_30', 'Part exploitable du panneau pour la proposition 30%', 0.3);
END;
GO

INSERT INTO dbo.majoration_heure_pointe (code_jour, heure_debut, heure_fin, taux_majoration)
SELECT v.code_jour, v.heure_debut, v.heure_fin, v.taux_majoration
FROM (
    VALUES
        ('OUVRABLE', '12:00:00', '14:00:00', 5.0),
        ('OUVRABLE', '17:00:00', '19:00:00', 5.0),
        ('WEEKEND', '12:00:00', '14:00:00', 5.0),
        ('WEEKEND', '17:00:00', '19:00:00', 5.0)
) AS v(code_jour, heure_debut, heure_fin, taux_majoration)
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.majoration_heure_pointe m
    WHERE m.code_jour = v.code_jour
      AND m.heure_debut = v.heure_debut
      AND m.heure_fin = v.heure_fin
);
GO

IF NOT EXISTS (SELECT 1 FROM dbo.type_panneau WHERE libelle = 'Panneau Standard 40%')
BEGIN
    INSERT INTO dbo.type_panneau (libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire)
    VALUES ('Panneau Standard 40%', 0.4, 110.0, 215000.0);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.type_panneau WHERE libelle = 'Panneau Economique 30%')
BEGIN
    INSERT INTO dbo.type_panneau (libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire)
    VALUES ('Panneau Economique 30%', 0.3, 130.0, 200000.0);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.simulation WHERE titre = 'Simulation Maison')
BEGIN
    INSERT INTO dbo.simulation (titre, notes)
    VALUES ('Simulation Maison', 'Jeu de donnees initial: charges domestiques');
END;
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'TV', 55.0, '08:00:00', '12:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'TV'
            AND e.puissance_w = 55.0
            AND e.heure_debut = '08:00:00'
            AND e.heure_fin = '12:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'Ventilateur', 75.0, '10:00:00', '14:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'Ventilateur'
            AND e.puissance_w = 75.0
            AND e.heure_debut = '10:00:00'
            AND e.heure_fin = '14:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'Refrigerateur', 120.0, '06:00:00', '17:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'Refrigerateur'
            AND e.puissance_w = 120.0
            AND e.heure_debut = '06:00:00'
            AND e.heure_fin = '17:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'Lampe', 10.0, '17:00:00', '19:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'Lampe'
            AND e.puissance_w = 10.0
            AND e.heure_debut = '17:00:00'
            AND e.heure_fin = '19:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'TV', 55.0, '17:00:00', '19:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'TV'
            AND e.puissance_w = 55.0
            AND e.heure_debut = '17:00:00'
            AND e.heure_fin = '19:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'Routeur Wifi', 10.0, '19:00:00', '06:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'Routeur Wifi'
            AND e.puissance_w = 10.0
            AND e.heure_debut = '19:00:00'
            AND e.heure_fin = '06:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'Refrigerateur', 120.0, '19:00:00', '06:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'Refrigerateur'
            AND e.puissance_w = 120.0
            AND e.heure_debut = '19:00:00'
            AND e.heure_fin = '06:00:00'
    );
GO

INSERT INTO dbo.simulation_entree (simulation_id, materiel, puissance_w, heure_debut, heure_fin)
SELECT s.id, 'Lampe', 10.0, '19:00:00', '23:00:00'
FROM dbo.simulation s
WHERE s.titre = 'Simulation Maison'
    AND NOT EXISTS (
        SELECT 1
        FROM dbo.simulation_entree e
        WHERE e.simulation_id = s.id
            AND e.materiel = 'Lampe'
            AND e.puissance_w = 10.0
            AND e.heure_debut = '19:00:00'
            AND e.heure_fin = '23:00:00'
    );
GO

INSERT INTO dbo.prix_energie_non_utilisee (type_panneau_id, code_jour, prix_wh)
SELECT tp.id, 'OUVRABLE', 100.0
FROM dbo.type_panneau tp
WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.prix_energie_non_utilisee p
        WHERE p.type_panneau_id = tp.id
            AND p.code_jour = 'OUVRABLE'
);
GO

INSERT INTO dbo.prix_energie_non_utilisee (type_panneau_id, code_jour, prix_wh)
SELECT tp.id, 'WEEKEND', 120.0
FROM dbo.type_panneau tp
WHERE NOT EXISTS (
        SELECT 1
        FROM dbo.prix_energie_non_utilisee p
        WHERE p.type_panneau_id = tp.id
            AND p.code_jour = 'WEEKEND'
);
GO
