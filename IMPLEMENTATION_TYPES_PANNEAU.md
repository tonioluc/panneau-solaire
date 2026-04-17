# Implémentation du Système de Gestion des Types de Panneaux

## Vue d'ensemble
Le système permet maintenant de gérer **plusieurs types de panneaux solaires** dynamiquement, avec CRUD complet et calcul automatique des propositions avec recommandation basée sur le prix.

## Architecture

### 1. Base de Données
**Table `type_panneau`** (nouvelle)
- `id` (BIGINT PK): Identifiant unique
- `libelle` (NVARCHAR): Nom du type (ex: "Panneau Premium 50%")
- `ratio_couverture` (DECIMAL): Ratio d'utilisation (0-1)
- `energie_unitaire_wh` (DECIMAL): Énergie générée par unité (Wh)
- `prix_unitaire` (DECIMAL): Prix unitaire ( Ar)
- `cree_le` (DATETIME2): Timestamp de création

#### Données initiales
- **Panneau Standard 40%**: ratio=0.4, énergie=100 Wh, prix=150 Ar
- **Panneau Economique 30%**: ratio=0.3, énergie=80 Wh, prix=100 Ar

### 2. Modèles de Données (src/modeles.py)

#### TypePanneau (frozen dataclass)
```python
@dataclass(frozen=True)
class TypePanneau:
    id: int
    libelle: str
    ratio_couverture: float      # 0-1
    energie_unitaire_wh: float
    prix_unitaire: float
```

#### PropositionPanneau (frozen dataclass)
```python
@dataclass(frozen=True)
class PropositionPanneau:
    id_type_panneau: int
    libelle_type: str
    ratio_couverture: float
    puissance_propose_w: float       # Puissance théorique calculée
    quantite_require: float          # Quantité nécessaire
    prix_unitaire: float
    prix_total: float               # Total = quantité * prix_unitaire
    est_recommande: bool            # True = meilleur prix
```

#### Modification de ResultatSimulation
- Suppression des champs: `panneau_proposition_40_w`, `panneau_proposition_30_w`
- Ajout du champ: `propositions_panneau: list[PropositionPanneau]`

### 3. Couche Repository (src/repository_sqlserver.py)

Nouvelles méthodes CRUD:

```python
def lister_types_panneau() -> list[TypePanneau]
    # Récupère tous les types triés par libelle

def creer_type_panneau(libelle, ratio, energie, prix) -> int
    # Crée un nouveau type, retourne l'ID

def modifier_type_panneau(id, libelle, ratio, energie, prix)
    # Modifie un type existant

def supprimer_type_panneau(id)
    # Supprime un type
```

### 4. Logique Métier (src/service_dimensionnement.py)

**Modification de `calculer()`**
- Signature: `calculer(entrees, parametres, tranches, types_panneau)`
- Nouveau paramètre: `types_panneau: list[TypePanneau]`

**Algorithme de calcul par type**:
```python
for type_p in types_panneau:
    quantite = panneau_theorique_w / (type_p.ratio_couverture * type_p.energie_unitaire_wh)
    prix_total = quantite * type_p.prix_unitaire
    # Créer PropositionPanneau
```

**Recommandation**:
- Identification du prix minimum
- Flag `est_recommande=True` pour le/les type(s) au prix minimum
- Retour dans `resultat.propositions_panneau`

### 5. Interface Utilisateur (src/ui_tkinter.py)

#### Nouvel Onglet "Types Panneau"
Complète gestion CRUD dans le même style que l'onglet "Entrees":

**Formulaire de saisie**:
- Libelle (texte)
- Ratio (0-1)
- Energie unitaire (Wh)
- Prix unitaire ( Ar)

**Table Treeview**:
- Affiche tous les types avec colonnes: id, libelle, ratio, energie, prix
- Double-clic = charger pour édition
- Boutons: Ajouter, Modifier, Supprimer, Annuler

#### Modification de l'Onglet "Resultats"
- **Dynamique**: Section "Propositions Panneaux" s'affiche lors du calcul
- **Un bloc par type**: Chaque type affiche:
  - Titre avec libelle + ratio + "✓ MEILLEUR PRIX" si recommandé
  - Quantité nécessaire (en unités)
  - Prix total ( Ar)
- **Styling**:
  - Blocs recommandés: fond `primary_container` + texte saillant
  - Autres blocs: fond neutre

**Workflow de calcul**:
1. Utilisateur clique "Calculer"
2. Service récupère les types_panneau
3. Service calcule propositions pour chaque type
4. UI affiche dynamiquement tous les blocs

## Utilisation

### Ajout d'un Type de Panneau
1. Aller à l'onglet "Types Panneau"
2. Remplir le formulaire:
   - Ex: "Panneau Premium 60%" | 0.6 | 120 | 200
3. Cliquer "Ajouter"

### Modification
1. Double-cliquer sur la ligne dans la table (pré-remplit le form)
2. Modifier les valeurs
3. Cliquer "Modifier"

### Suppression
1. Sélectionner la ligne
2. Cliquer "Supprimer"

### Voir les Propositions
1. Aller à l'onglet "Entrees" et entrer une charge
2. Aller à l'onglet "Resultats"
3. Cliquer "Calculer"
4. Les propositions s'affichent dynamiquement pour tous les types

## Exemple Complet

**État initial**: 2 panneaux en BD
- Panneau Standard 40% (ratio=0.4, 100 Wh, 150 Ar)
- Panneau Economique 30% (ratio=0.3, 80 Wh, 100 Ar)

**Calcul avec charge**: 1000W pendant 8h → 8000 Wh

**Résultats du calcul**:
1. Panneau Standard 40%:
   - Quantité = 8000 / (0.4 * 100) = 200 unités
   - Prix = 200 * 150 = 30000 Ar ❌

2. Panneau Economique 30% (RECOMMANDÉ ✓):
   - Quantité = 8000 / (0.3 * 80) = 333.3 unités
   - Prix = 333.3 * 100 = 33330 Ar ❌

*Note: Chiffres illustratifs, ajustez les parametres réels*

## Fichiers Modifiés

```
database/
  table_sqlserver.sql        (+30 lignes: table type_panneau + index)
  data.sql                   (+10 lignes: données initiales)
src/
  modeles.py                 (3 nouvelles classes + modification ResultatSimulation)
  repository_sqlserver.py    (import + 4 méthodes CRUD)
  service_dimensionnement.py (import + modification calculer())
  ui_tkinter.py              (+350 lignes: onglet CRUD + affichage dynamique)
```

## Validation

✅ Tous les fichiers compilent sans erreur python  
✅ Schéma SQL créé avec contraintes  
✅ Modèles étendus sans conflit de type  
✅ Service calcule pour multiple types  
✅ UI affiche dynamiquement les propositions  
✅ Recommandation par prix implémentée
