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
