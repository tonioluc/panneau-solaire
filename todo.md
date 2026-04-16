# TODO - Flux logique et calcul (version precise)

## 1. Regles metier a verrouiller
- [ ] Tranche matin (06:00 -> 17:00): uniquement le panneau alimente:
  - la consommation des appareils du matin
  - la charge de la batterie pour la nuit
- [ ] Tranche soir (17:00 -> 19:00): uniquement le panneau alimente les appareils,
      mais seulement 50% de la puissance du panneau est disponible
- [ ] Tranche nuit (19:00 -> 06:00): uniquement la batterie alimente les appareils
- [ ] Apres calcul theorique:
  - cas pratique panneau: 40% de rendement utile
  - cas pratique batterie: +50% de marge sur l'energie de nuit

## 2. Unites et conventions
- [ ] Puissance en W
- [ ] Energie en Wh (conversion kWh = Wh / 1000)
- [ ] Duree en heures decimales
- [ ] Toutes les formules utilisent des valeurs positives strictes

## 3. Donnees d'entree
- [ ] Appareil:
  - nom
  - puissance_w
- [ ] Utilisation:
  - appareil_id
  - date_heure_debut
  - date_heure_fin
- [ ] Validation:
  - puissance_w > 0
  - date_heure_fin > date_heure_debut

## 4. Decoupage des utilisations par tranche
- [ ] Segmenter chaque utilisation quand elle traverse une borne de tranche
- [ ] Associer chaque segment a MATIN, SOIR ou NUIT
- [ ] Calculer pour chaque segment:
  - duree_h = (fin - debut)
  - energie_segment_wh = puissance_w * duree_h

## 5. Agregation par tranche
- [ ] Calculer:
  - E_matin_wh = somme(energie_segment_wh, tranche MATIN)
  - E_soir_wh = somme(energie_segment_wh, tranche SOIR)
  - E_nuit_wh = somme(energie_segment_wh, tranche NUIT)
- [ ] Calculer les pics de puissance simultanee:
  - P_pic_matin_w
  - P_pic_soir_w

## 6. Calcul theorique batterie
- [ ] Besoin batterie theorique (nuit uniquement):
  - E_batterie_theorique_wh = E_nuit_wh

## 7. Calcul theorique panneau
- [ ] Besoin de charge batterie pendant le matin:
  - P_charge_batterie_theorique_w = E_batterie_theorique_wh / 11
    (11h disponibles sur la tranche matin)
- [ ] Contrainte matin (appareils + charge batterie):
  - P_panneau_matin_theorique_w = P_pic_matin_w + P_charge_batterie_theorique_w
- [ ] Contrainte soir (seulement 50% de panneau disponible):
  - 0.5 * P_panneau_theorique_w >= P_pic_soir_w
  - donc P_panneau_soir_theorique_w = P_pic_soir_w / 0.5
- [ ] Puissance panneau theorique finale:
  - P_panneau_theorique_w = max(P_panneau_matin_theorique_w, P_panneau_soir_theorique_w)

## 8. Passage au cas pratique
- [ ] Panneau a acheter (rendement utile 40%):
  - P_panneau_a_acheter_w = P_panneau_theorique_w / 0.4
- [ ] Batterie a acheter (+50% sur besoin nuit):
  - E_batterie_a_acheter_wh = E_batterie_theorique_wh * 1.5
  - E_batterie_a_acheter_kwh = E_batterie_a_acheter_wh / 1000

## 9. Verifications de coherence
- [ ] Verifier que la recharge theorique de la batterie est realisable le matin:
  - E_recharge_possible_matin_wh = (P_panneau_theorique_w - P_pic_matin_w) * 11
  - alerte si E_recharge_possible_matin_wh < E_batterie_theorique_wh
- [ ] Verifier la contrainte soir:
  - alerte si 0.5 * P_panneau_theorique_w < P_pic_soir_w
- [ ] Verifier que toutes les energies/tranches sont non negatives

## 10. Restitution finale
- [ ] Sorties principales:
  - puissance panneau theorique (W)
  - puissance panneau a acheter (W, kW)
  - capacite batterie theorique (Wh)
  - capacite batterie a acheter (Wh, kWh)
- [ ] Sorties de controle:
  - detail par tranche (energie + pic)
  - alertes coherence

## 11. Regles d'arrondi
- [ ] Panneau: arrondi au multiple commercial superieur (50 W ou 100 W)
- [ ] Batterie: arrondi au modele commercial superieur (ex: pas de 0.1 kWh)

## 12. Tracabilite base de donnees
- [ ] Conserver:
  - entrees (appareils, utilisations)
  - segments par tranche
  - agregations par tranche
  - resultats theoriques
  - resultats pratiques
  - hypotheses de calcul utilisees
