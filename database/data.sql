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

IF NOT EXISTS (SELECT 1 FROM dbo.type_panneau WHERE libelle = 'Panneau Standard 40%')
BEGIN
    INSERT INTO dbo.type_panneau (libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire)
    VALUES ('Panneau Standard 40%', 0.4, 100.0, 150.0);
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.type_panneau WHERE libelle = 'Panneau Economique 30%')
BEGIN
    INSERT INTO dbo.type_panneau (libelle, ratio_couverture, energie_unitaire_wh, prix_unitaire)
    VALUES ('Panneau Economique 30%', 0.3, 80.0, 100.0);
END;
GO
