# Panneau Solaire - Simulation Tkinter + SQL Server

Application desktop Python pour:
- creer une simulation,
- ajouter les entrees (materiel, puissance, heure debut, heure fin),
- afficher le resultat de dimensionnement.

Le resultat n'est pas stocke en base. Seules les entrees sont stockees.

Ce guide est concu pour fonctionner sur une nouvelle machine Linux (Ubuntu/Debian) sans erreur ODBC.

---

## 1. Prerequis

- Linux Ubuntu/Debian
- Docker
- Python 3.10+
- Acces `sudo`

Verifier rapidement:

```bash
docker --version
python3 --version
```

---

## 2. Recuperer le projet

```bash
git clone <URL_DU_REPO>
cd panneau-solaire
```

---

## 3. Demarrer SQL Server avec Docker

```bash
docker pull mcr.microsoft.com/mssql/server:2022-latest

docker run -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=admin@12345" \
  -p 1433:1433 \
  --name sqlserver-solaire \
  -d mcr.microsoft.com/mssql/server:2022-latest
```

Verifier que le conteneur est actif:

```bash
docker ps --filter "name=sqlserver-solaire"
```

---

## 4. Installer ODBC correctement (important)

`libodbc` seul ne suffit pas. Il faut aussi un driver SQL Server enregistre, par exemple `ODBC Driver 18 for SQL Server`.

### 4.1 Installer unixODBC + outils

```bash
sudo apt update
sudo apt install -y unixodbc unixodbc-dev odbcinst curl gnupg2 ca-certificates apt-transport-https
```

### 4.2 Installer le driver Microsoft ODBC 18

Utiliser le fichier de depot officiel Microsoft pour eviter les erreurs de suite (ex: `22.04` au lieu de `jammy`).

```bash
sudo rm /usr/share/keyrings/microsoft-prod.gpg
# 1. Nettoyage
sudo rm -f /usr/share/keyrings/microsoft-prod.gpg
sudo rm -f /etc/apt/sources.list.d/microsoft-prod.list

# 2. Installer correctement la clé (SANS sudo dans gpg)
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
| gpg --dearmor \
| sudo tee /usr/share/keyrings/microsoft-prod.gpg > /dev/null

# 3. Ajouter le dépôt proprement (sans sed compliqué)
UBU_VER=$(lsb_release -rs)
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/${UBU_VER}/prod $(lsb_release -cs) main" \
| sudo tee /etc/apt/sources.list.d/microsoft-prod.list > /dev/null

# 4. Update
sudo apt update

# 5. Installation
sudo ACCEPT_EULA=Y apt install -y msodbcsql18
```

### 4.3 Verifier que le driver est visible

```bash
odbcinst -q -d
python3 -c "import pyodbc; print(pyodbc.drivers())"
```

Tu dois voir au moins:
- `ODBC Driver 18 for SQL Server`

Si la liste Python est vide, le driver n'est pas correctement installe/enregistre.

---

## 5. Installer Python et dependances du projet

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Le projet utilise:
- `pyodbc` (voir [requirements.txt](requirements.txt))

---

## 6. Initialiser la base SQL Server

Creer la base puis executer les scripts SQL:

```bash
docker exec -it sqlserver-solaire /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "admin@12345" -C -Q "IF DB_ID('solaire_db') IS NULL CREATE DATABASE solaire_db;"

docker cp database/table_sqlserver.sql sqlserver-solaire:/tmp/table_sqlserver.sql
docker exec -it sqlserver-solaire /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "admin@12345" -C -d solaire_db -i /tmp/table_sqlserver.sql

docker cp database/data.sql sqlserver-solaire:/tmp/data.sql
docker exec -it sqlserver-solaire /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "admin@12345" -C -d solaire_db -i /tmp/data.sql
```

Scripts utilises:
- [database/table_sqlserver.sql](database/table_sqlserver.sql)
- [database/data.sql](database/data.sql)

---

## 7. Variables d'environnement (optionnel)

Valeurs par defaut utilisees par l'application:

- `DB_SERVER=localhost`
- `DB_PORT=1433`
- `DB_NAME=solaire_db`
- `DB_USER=sa`
- `DB_PASSWORD=admin@12345`
- `DB_DRIVER` vide (auto-detection)

Si besoin, forcer explicitement le driver:

```bash
export DB_DRIVER="ODBC Driver 18 for SQL Server"
```

---

## 8. Lancer l'application

```bash
source .venv/bin/activate
python src/app_tkinter.py
```

Point d'entree:
- [src/app_tkinter.py](src/app_tkinter.py)

---

## 9. Test rapide de connexion avant UI (recommande)

```bash
source .venv/bin/activate
python -c "import pyodbc; print(pyodbc.drivers())"
```

Si la liste contient `ODBC Driver 18 for SQL Server`, l'erreur "Aucun driver ODBC SQL Server detecte" ne doit plus apparaitre.

---

## 10. Depannage

### Erreur: "Aucun driver ODBC SQL Server detecte"

Cause probable:
- `msodbcsql18` non installe ou non enregistre.

Checks:

```bash
odbcinst -q -d
python -c "import pyodbc; print(pyodbc.drivers())"
```

Correction:
- refaire l'etape 4.1 et 4.2,
- puis forcer temporairement:

```bash
export DB_DRIVER="ODBC Driver 18 for SQL Server"
```

### Erreur apt: "404 Not Found" sur packages.microsoft.com ou "Impossible de trouver le paquet msodbcsql18"

Cause probable:
- ligne invalide dans `/etc/apt/sources.list.d/microsoft-prod.list` (suite `22.04` au lieu de `jammy`).

Correction:

```bash
UBU_VER=$(lsb_release -rs)
sudo rm -f /etc/apt/sources.list.d/microsoft-prod.list
curl -fsSL https://packages.microsoft.com/config/ubuntu/${UBU_VER}/prod.list \
  | sudo tee /etc/apt/sources.list.d/microsoft-prod.list
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql18
```

### Erreur: Login failed for user 'sa'

Cause probable:
- mot de passe `SA` incorrect.

Correction:
- recreer le conteneur avec le bon mot de passe,
- ou aligner `DB_PASSWORD` avec le mot de passe du conteneur.

### Erreur: Cannot open database "solaire_db" requested by the login

Cause probable:
- base non creee.

Correction:
- refaire l'etape 6.

### Erreur: Connection refused / timeout

Cause probable:
- conteneur SQL Server non demarre,
- port 1433 non expose.

Checks:

```bash
docker ps --filter "name=sqlserver-solaire"
ss -ltnp | grep 1433
```

---

## 11. Reset complet (si installation casse)

```bash
docker rm -f sqlserver-solaire
docker run -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=admin@12345" \
  -p 1433:1433 \
  --name sqlserver-solaire \
  -d mcr.microsoft.com/mssql/server:2022-latest
```

Puis reprendre depuis l'etape 6.
