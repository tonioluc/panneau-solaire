# panneau-solaire

Application desktop Python pour estimer la puissance d'un panneau solaire et la capacite d'une batterie a partir des appareils utilises par tranche horaire.

## Lancer l'application

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Lancer les tests

```bash
python -m unittest discover -s tests
```

## Base SQL Server

Le schema SQL Server est dans [sql/schema.sql](sql/schema.sql). L'application enregistre dans SQL Server si la variable d'environnement `SQLSERVER_CONNECTION_STRING` est definie.

### Docker SQL Server

Conteneur utilise:

```bash
docker ps --filter name=sqlserver-panneau --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

Commande pour le demarrer:

```bash
docker start sqlserver-panneau
```

Variable d'environnement pour l'application:

```bash
export SQLSERVER_CONNECTION_STRING='DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=master;UID=sa;PWD=Solaire@2026Db!;Encrypt=no;TrustServerCertificate=yes;'
```
