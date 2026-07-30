# Commandes de lancement NURU sous Windows

Le mode actuellement le mieux validé est :

```text
Bases Docker + Ollama natif + backend natif Windows + frontend natif Windows
```

## 1. Se placer dans le projet

Dans PowerShell :

```powershell
Set-Location "C:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
```

## 2. Préparer l'environnement Python — une seule fois

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
```

Ce script crée ou réutilise `venv_win`, installe les dépendances et vérifie les imports principaux.

## 3. Lancer les services Docker nécessaires

```powershell
docker compose up -d postgres qdrant
docker compose ps
```

Vérifications sans afficher de secret :

```powershell
Test-NetConnection localhost -Port 5433
Invoke-RestMethod http://localhost:6333/collections
```

Pour que le backend Windows utilise réellement PostgreSQL au lieu du repli SQLite,
ajouter dans `.env` :

```dotenv
DATABASE_URL=postgresql+psycopg://nuru:nuru_password@localhost:5433/nuru
```

Laisser cette variable absente ou vide conserve volontairement
`nuru_student_memory.db`.

## 4. Vérifier ou lancer Ollama nativement

Vérifier si Ollama et le modèle sont disponibles :

```powershell
ollama list
```

Si le serveur Ollama n'est pas déjà actif :

```powershell
ollama serve
```

Garder ce terminal ouvert lorsque `ollama serve` est lancé manuellement.

Vérification Ollama :

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

## 5. Lancer le backend

### Méthode recommandée

Dans un nouveau terminal PowerShell, à la racine du projet :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_backend_windows.ps1
```

### Méthode manuelle

```powershell
.\venv_win\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
$env:PORT = "8080"
python -m backend.app.api.main
```

Adresses du backend :

- API : `http://localhost:8080`
- documentation Swagger : `http://localhost:8080/docs`
- endpoint de santé : `http://localhost:8080/health`

Vérification rapide :

```powershell
Invoke-RestMethod http://localhost:8080/health
```

## 6. Lancer le frontend

Dans un autre terminal PowerShell :

```powershell
Set-Location "C:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
powershell -ExecutionPolicy Bypass -File scripts\run_frontend_windows.ps1
```

### Méthode manuelle

```powershell
.\venv_win\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
$env:API_URL = "http://localhost:8080"
$env:GRADIO_PORT = "7860"
python -m frontend.gradio_app
```

Ouvrir ensuite l'interface :

```text
http://localhost:7860
```

Vérification HTTP du frontend :

```powershell
(Invoke-WebRequest http://localhost:7860 -UseBasicParsing).StatusCode
```

## 7. Ordre recommandé des terminaux

| Terminal | Commande ou service | Doit rester ouvert |
|---|---|---|
| Terminal 1 | `docker compose up -d postgres qdrant` | Non, une fois les conteneurs démarrés |
| Terminal 2 | `ollama serve`, seulement si Ollama n'est pas déjà actif | Oui |
| Terminal 3 | Backend FastAPI | Oui |
| Terminal 4 | Frontend Gradio | Oui |

## 8. Lancement entièrement avec Docker

La commande théorique est :

```powershell
docker compose up -d --build
docker compose ps
```

L'instruction obsolète `COPY config/ ./config/` a été retirée du `Dockerfile`, car
ce dossier n'existe pas et aucun code actif ne l'utilise. La configuration Compose est
valide, mais le build complet n'a pas été exécuté pendant cet audit.

Le risque fonctionnel restant est que le backend Docker utilise le Qdrant local, qui
peut être vide alors que les données validées se trouvent sur Qdrant Cloud.

Pour le moment, utiliser de préférence le mode hybride : services de données dans Docker, puis backend et frontend natifs Windows.

## 9. Consulter les logs Docker

```powershell
docker compose logs --tail=100 postgres
docker compose logs --tail=100 qdrant
```

Pour suivre les logs en continu :

```powershell
docker compose logs -f qdrant postgres
```

Utiliser `Ctrl+C` pour quitter l'affichage des logs sans arrêter les conteneurs.

## 10. Arrêter les services

### Backend et frontend

Dans leurs terminaux respectifs, utiliser :

```text
Ctrl+C
```

### Ollama natif

Si `ollama serve` a été lancé manuellement dans un terminal, utiliser également
`Ctrl+C` dans ce terminal. Si Ollama fonctionne comme service Windows, le laisser
actif ou l'arrêter depuis le gestionnaire de services selon le besoin.

### Services Docker

Arrêter sans supprimer les données :

```powershell
docker compose stop postgres qdrant
```

Les redémarrer plus tard :

```powershell
docker compose start postgres qdrant
```

Arrêter et supprimer les conteneurs tout en conservant les volumes :

```powershell
docker compose down
```

## 11. Avertissement important

Ne pas exécuter la commande suivante sans vouloir supprimer les données locales des volumes Docker :

```powershell
docker compose down -v
```

L'option `-v` supprime les volumes Qdrant et PostgreSQL associés au projet.

## 12. Démarrage rapide recommandé

### Terminal 1 — infrastructures

```powershell
Set-Location "C:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
docker compose up -d postgres qdrant
docker compose ps
ollama list
```

### Terminal 2 — backend

```powershell
Set-Location "C:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
powershell -ExecutionPolicy Bypass -File scripts\run_backend_windows.ps1
```

### Terminal 3 — frontend

```powershell
Set-Location "C:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
powershell -ExecutionPolicy Bypass -File scripts\run_frontend_windows.ps1
```

### Navigateur

```text
Frontend : http://localhost:7860
Swagger  : http://localhost:8080/docs
Santé    : http://localhost:8080/health
```
