# NURU — Guide manuel : installation, lancement et test sous Windows

Ce guide s'adresse à quelqu'un qui découvre le projet. Il explique **toutes** les commandes
manuellement, sans dépendre uniquement des scripts PowerShell (`scripts/*_windows.ps1`). Les scripts
sont présentés comme méthode rapide (§Quick Start), mais chaque étape manuelle est détaillée pour
que vous compreniez ce qui se passe réellement.

Complète `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md` (qui explique *pourquoi* les fichiers ont été
modifiés) et `SPRINT2_PROJECT_TECHNICAL_ANALYSIS.md` (analyse complète du projet).

> ✅ **Corrigé depuis** : les défauts fonctionnels graves identifiés lors des tests manuels (timeout
> initial, outil mathématique déclenché sur des mots naturels, quiz avec des placeholders, quiz qui ne
> se souvenait pas de sa propre question) ont été corrigés et testés (30 nouveaux tests + batterie
> fonctionnelle complète contre l'API réelle). Voir `SPRINT2_FUNCTIONAL_AND_PEDAGOGICAL_DIAGNOSTIC.md`
> pour le détail complet.
>
> ⚠️ **Ce qui reste limité** : la qualité du contenu généré (cours/exercices) dépend encore (1) de
> l'ingestion Qdrant, relancée mais très longue à terminer sans GPU sur cette machine (voir le
> diagnostic, §5.2/§8) — tant qu'elle n'est pas finie, le RAG reste vide — et (2) des limites propres
> au modèle `llama3.2:1b` (conservé par défaut, voir la comparaison avec `llama3.1:8b` dans le
> diagnostic, §4). Ne considérez pas une réponse de cours/exercice comme mathématiquement fiable sans
> vérification tant que ces deux points ne sont pas résolus.

---

## A. Architecture simplifiée

```text
Navigateur (vous)
   │
   ▼
Gradio (interface web, port 7860) ─────────────┐
   │  requête HTTP JSON                        │  affiche la réponse
   ▼                                           │
FastAPI (API backend, port 8080) ───────────────┘
   │
   ▼
LangGraph (le "cerveau" : décide quoi faire, dans quel ordre)
   │
   ├──► Qdrant (recherche dans les documents de cours — RAG)
   ├──► Neo4j (relations entre notions — prérequis)
   └──► Ollama (le modèle de langage qui rédige la réponse, en local)
   │
   ▼
SQLite ou PostgreSQL (mémoire : qui a posé quelle question, ses résultats, sa progression)
```

**En mots simples :**
- **Gradio** = la page web que vous voyez et avec laquelle vous cliquez/tapez.
- **FastAPI** = le serveur qui reçoit les questions envoyées par Gradio et renvoie une réponse.
- **LangGraph** = l'enchaînement d'étapes internes (comprendre la question → chercher le cours
  pertinent → si c'est un calcul, le faire exactement avec SymPy → rédiger une explication → vérifier
  → enregistrer la progression).
- **Qdrant** = une base qui retrouve les passages de cours les plus proches de la question posée
  (recherche "par le sens", pas juste par mot-clé).
- **Neo4j** = une base qui connaît les liens entre les notions (ex: "il faut connaître les limites
  avant la dérivabilité").
- **Ollama** = le modèle d'IA qui tourne sur votre machine (pas sur Internet) et rédige le texte de
  la réponse.
- **SQLite/PostgreSQL** = l'endroit où sont gardées les informations sur chaque élève (questions
  posées, résultats, notions maîtrisées).

---

## B. Prérequis

Vérifiez ce qui est installé avant de commencer :

```powershell
py -3.12 --version
docker --version
docker compose version
ollama --version
ollama list
```

**Pourquoi Python 3.12 précisément (et pas 3.14 ou 3.15) ?**
Cette machine a plusieurs versions de Python installées. La commande `python` toute seule peut se
résoudre vers n'importe laquelle selon le terminal utilisé — sur cette machine, elle s'est avérée
résolue vers Python 3.14 dans un contexte, ce qui a cassé l'installation de certaines dépendances
scientifiques (roues précompilées absentes pour une version aussi récente). Python 3.12 est proche
de la version utilisée par le projet à l'origine (3.10/3.11) et dispose de roues précompilées pour
toutes les dépendances du projet. **Utilisez toujours `py -3.12` explicitement**, jamais `python`
tout seul, pour ce projet sur cette machine.

---

## C. Installation manuelle de Python (environnement virtuel)

```powershell
Set-Location "c:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
py -3.12 -m venv venv_win
.\venv_win\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- **Comment savoir que le venv est activé ?** Le prompt PowerShell affiche `(venv_win)` au début de
  la ligne après `Activate.ps1`. Vous pouvez aussi taper `Get-Command python | Select Source` — le
  chemin doit contenir `venv_win\Scripts\python.exe`.
- **Comment le désactiver ?** Tapez simplement `deactivate` dans le même terminal.
- **Comment vérifier la version Python du venv ?** Une fois activé : `python --version` doit afficher
  `Python 3.12.x`.
- **Comment vérifier les dépendances installées ?** `pip list` (toutes), ou cibler une dépendance
  précise : `pip show fastapi`.

Vérification rapide que tout s'est bien installé :
```powershell
python -c "import fastapi, langgraph, sqlalchemy, sympy, gradio, qdrant_client, neo4j, ollama; print('OK')"
```

---

## D. Démarrage des services Docker

```powershell
docker compose config
docker compose up -d postgres qdrant neo4j
docker compose ps
```

- `docker compose config` : valide et affiche la configuration finale (avec les variables `${...}`
  remplacées) — utile pour repérer une erreur de syntaxe avant de lancer quoi que ce soit.
- `docker compose up -d postgres qdrant neo4j` : démarre uniquement ces trois services, **pas**
  `backend`/`frontend`/`ollama` (le service `ollama` est de toute façon désactivé par défaut — voir
  §F).
- `docker compose ps` : affiche l'état de chaque conteneur.

**Colonnes de `docker compose ps` :**

| Colonne | Signification |
| --- | --- |
| `NAME` | Nom du conteneur (préfixé par le nom du projet, ex. `nuru_agent_nbn-postgres-1`) |
| `IMAGE` | Image Docker utilisée |
| `COMMAND` | Commande lancée à l'intérieur du conteneur |
| `SERVICE` | Nom du service tel que défini dans `docker-compose.yml` |
| `CREATED` | Depuis combien de temps le conteneur existe |
| `STATUS` | `Up` = en cours d'exécution ; `Up (healthy)` = en plus, le health check passe ; `Exited` = arrêté/planté |
| `PORTS` | Mapping `hôte->conteneur` (ex. `0.0.0.0:5433->5432/tcp` = le port 5433 de votre PC redirige vers le port 5432 du conteneur) |

Logs de démarrage :
```powershell
docker compose logs --tail=100 postgres
docker compose logs --tail=100 qdrant
docker compose logs --tail=100 neo4j
```

**Messages qui confirment que chaque service est prêt :**

| Service | Message à chercher dans les logs |
| --- | --- |
| Postgres | `database system is ready to accept connections` |
| Qdrant | `Qdrant HTTP listening on 6333` |
| Neo4j | `Bolt enabled on 0.0.0.0:7687.` puis `Started.` |

---

## E. Vérification des ports

```powershell
Get-NetTCPConnection -LocalPort 5433 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 6333 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 7474 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 7687 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 7860 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue
```

Si une commande ne renvoie **rien**, le port n'est pas encore utilisé (normal avant d'avoir tout
lancé, anormal une fois tout démarré). Si elle renvoie une ligne avec `State: Listen`, le port est
occupé par le processus indiqué dans `OwningProcess` (croisez avec `Get-Process -Id <PID>`).

---

## F. Ollama (natif, pas dans Docker)

```powershell
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

`ollama list` doit afficher `llama3.2:1b` (entre autres modèles déjà installés).
`Invoke-RestMethod` doit renvoyer un JSON listant ce même modèle — cela confirme que le serveur
Ollama répond sur le port 11434.

**Tester directement le modèle en ligne de commande (hors NURU) :**
```powershell
ollama run llama3.2:1b
```
Ceci ouvre une session de discussion interactive directement avec le modèle. Tapez votre question,
appuyez sur Entrée. **Pour quitter** cette session interactive : tapez `/bye` (ou `Ctrl+D`).

Rappel : ne relancez pas `ollama pull llama3.2:1b`, le modèle est déjà présent.

---

## G. Lancement manuel du backend

Dans un terminal PowerShell, à la racine du projet, avec le venv activé (`.\venv_win\Scripts\Activate.ps1`) :

```powershell
$env:PYTHONUTF8 = "1"
$env:PORT = "8080"
python -m backend.app.api.main
```

**Pourquoi `PYTHONUTF8 = "1"` ?** Le code affiche des emojis dans la console ; sans ce réglage,
Windows plante avec une erreur d'encodage (`UnicodeEncodeError`) au démarrage.

**Variables supplémentaires selon votre configuration** (normalement déjà dans `.env`, chargé
automatiquement si vous utilisez `run_backend_windows.ps1` — sinon, à définir manuellement avec
`$env:NOM = "valeur"` avant de lancer `python -m backend.app.api.main`) :

| Besoin | Variable(s) | Valeur actuelle (mode par défaut) |
| --- | --- | --- |
| Neo4j local | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` | `bolt://localhost:7687`, `neo4j`, *(mot de passe défini dans `.env`, non reproduit ici)*, `neo4j` |
| Ollama natif | `OLLAMA_MODEL` | `llama3.2:1b` (pas besoin de `OLLAMA_HOST` en natif, le client Ollama Python cible `localhost:11434` par défaut) |
| Qdrant Cloud (actuel) | `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION` | *(valeurs réelles dans `.env`, jamais affichées ici — voir `.env` directement sur votre machine)* |
| SQLite (par défaut) | `DATABASE_URL` | **laisser vide/absent** → SQLite automatique (`nuru_student_memory.db`) |
| PostgreSQL (optionnel) | `DATABASE_URL` | `postgresql+psycopg://nuru:nuru_password@localhost:5433/nuru` (voir §Mode PostgreSQL ci-dessous) |

### Mode simple recommandé pour comprendre le projet (par défaut)

```text
Backend local + frontend local + SQLite + Qdrant Cloud + Neo4j local + Ollama natif
```
C'est le mode qui a été testé et validé pendant cette phase. Ne définissez **pas** `DATABASE_URL` :
le backend utilisera automatiquement SQLite (`nuru_student_memory.db`, déjà présent, jamais
supprimé). Vous verrez ce message dans les logs : `DATABASE_URL non défini, utilisation de SQLite
local`.

### Mode avec PostgreSQL (optionnel, à choisir volontairement)

```text
Backend local + frontend local + PostgreSQL Docker + Qdrant Cloud + Neo4j local + Ollama natif
```
Avant de lancer le backend, définissez :
```powershell
$env:DATABASE_URL = "postgresql+psycopg://nuru:nuru_password@localhost:5433/nuru"
```
**Attention à ne pas confondre deux URL différentes** qui se ressemblent :
- `postgresql+psycopg://nuru:nuru_password@localhost:5433/nuru` → à utiliser quand le backend
  tourne **en natif sur Windows** et que PostgreSQL tourne **dans Docker** (port hôte `5433`, car
  c'est le port exposé sur votre machine — voir §6 du rapport de changements).
- `postgresql+psycopg://nuru:nuru_password@postgres:5432/nuru` → utilisée uniquement **entre
  conteneurs Docker** (dans `docker-compose.yml`, quand le backend tourne lui-même dans un
  conteneur) : `postgres` est le nom du service Docker, résolu uniquement à l'intérieur du réseau
  Docker, `5432` est le port **interne** du conteneur. **Cette URL ne fonctionnera pas** si vous la
  copiez dans un terminal PowerShell natif.

**Comment vérifier quelle base est réellement utilisée à un instant donné ?**
Regardez la ligne de log affichée au démarrage du backend :
```
INFO:backend.app.memory.db:✅ Base de données mémoire élève initialisée (sqlite)
```
ou
```
INFO:backend.app.memory.db:✅ Base de données mémoire élève initialisée (postgresql)
```
Le mot entre parenthèses (`sqlite` ou `postgresql`) est déduit directement de `DATABASE_URL` — sans
ambiguïté possible.

### Messages de logs qui indiquent que le backend est prêt

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```
Avant cela, vous verrez normalement, dans l'ordre : le message SQLite/PostgreSQL, puis le
chargement du modèle d'embeddings (`✅ Modèle chargé avec succès`), la connexion à Qdrant
(`✅ Connexion à Qdrant: ...`), la connexion à Neo4j (`✅ Connecté à Neo4j: ...`), puis
`✅ Orchestrateur (LangGraph) initialisé`. Si l'un de ces `✅` est remplacé par un `⚠️`, le service
concerné n'a pas pu être contacté — le backend continue quand même (dégradation gracieuse), mais la
fonctionnalité associée sera limitée.

---

## H. Tests du backend

```powershell
Invoke-RestMethod http://localhost:8080/health
```

Puis un vrai message de chat :
```powershell
$body = @{
    message = "Explique-moi les nombres complexes"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8080/chat/" `
    -ContentType "application/json; charset=utf-8" `
    -Body $body
```

> **Remarque sur les accents** : `Invoke-RestMethod` sous Windows PowerShell 5.1 peut afficher les
> accents français de façon incorrecte à l'écran (ex. `Ã©` au lieu de `é`) alors que la réponse de
> l'API est en réalité parfaitement correcte en UTF-8 — c'est un défaut d'affichage de PowerShell
> 5.1, pas un bug de l'API (vérifié en inspectant les octets bruts avec `curl.exe`). Ne vous inquiétez
> pas si vous voyez ce genre de caractères bizarres dans ce terminal ; l'interface Gradio et un
> navigateur les afficheront correctement.

**Signification des champs de la réponse :**

| Champ | Signification |
| --- | --- |
| `response` | Le texte de réponse généré (l'explication, l'exercice, le quiz...) |
| `intent` | Ce que le Planner a détecté comme intention : `cours`, `exercice`, `quiz`, ou `general` |
| `level` | Niveau d'aide pédagogique actuel : `reformulation`, `rappel`, `indice`, `solution_guidee`, `solution_complete` |
| `confidence` | Score de cohérence calculé par l'agent Vérificateur (0 à 1) |
| `session_id` | Identifiant qui regroupe tous les échanges d'une même conversation |
| `progression_summary` | Résumé de la progression de l'élève (maîtrise par notion, notions faibles, dernières interactions) — vide si aucun `user_id` n'a été fourni |

### Swagger (documentation interactive de l'API)

Ouvrez dans votre navigateur :
```text
http://localhost:8080/docs
```
Pour tester une route directement : cliquez sur la route voulue (ex. `POST /chat/`), cliquez sur
**"Try it out"**, modifiez le corps JSON de l'exemple, puis cliquez sur **"Execute"**. La réponse
s'affiche en dessous, avec le code HTTP et le corps complet.

---

## I. Lancement manuel du frontend

Dans un **nouveau** terminal (laissez le précédent avec le backend ouvert) :

```powershell
Set-Location "c:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
.\venv_win\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
$env:API_URL = "http://localhost:8080"
$env:GRADIO_PORT = "7860"
python -m frontend.gradio_app
```

Ouvrez ensuite :
```text
http://localhost:7860
```

**Comment tester :**
- **Espace Élève** : onglet visible par défaut. Allez dans l'onglet **📚 Cours**, tapez une question
  (ex. *"Explique-moi la dérivabilité"*), cliquez **Envoyer**.
- **Chat** : la réponse doit apparaître dans la bulle de conversation, pas de message jaune "mode
  hors-ligne".
- **Espace Enseignant** : onglet séparé — testez la création de compte (**Créer un compte**) avec un
  email et un mot de passe de test, puis **Se connecter**.
- **Communication frontend → backend** : gardez un œil sur le terminal du backend pendant que vous
  utilisez l'interface — chaque action doit faire apparaître une ligne
  `INFO:     127.0.0.1:... - "POST /chat/ HTTP/1.1" 200 OK` (ou une autre route `/teacher/...`,
  `/chat/progression/...`, etc. selon l'action).

> ✅ **Corrigé** : un bug d'affichage empêchait auparavant la réponse d'apparaître dans les onglets
> Cours/Exercices/Quiz (*"Data incompatible with messages format..."*), même si le backend répondait
> correctement. Corrigé en adaptant `frontend/gradio_app.py` au format de messages de Gradio 6.x et
> en épinglant `gradio==6.20.0` dans `requirements.txt`. Voir
> `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md` section 27 pour le détail complet (diagnostic, options
> comparées, validation). Si vous avez installé l'environnement **avant** cette correction,
> réinstallez simplement les dépendances (`pip install -r requirements.txt`, ou au minimum
> `pip install gradio==6.20.0`) puis redémarrez le frontend.

---

## J. Ordre exact des terminaux

| Terminal | Commande/service | Doit rester ouvert |
| --- | --- | --- |
| Terminal 1 | `docker compose up -d postgres qdrant neo4j` puis vérifications (`docker compose ps`, logs) | Non — une fois les services `Up`, ce terminal peut être fermé (les conteneurs continuent de tourner en arrière-plan) |
| Terminal 2 | Backend FastAPI (`run_backend_windows.ps1` ou commandes manuelles §G) | **Oui**, tant que vous voulez utiliser l'API |
| Terminal 3 | Frontend Gradio (`run_frontend_windows.ps1` ou commandes manuelles §I) | **Oui**, tant que vous voulez utiliser l'interface |
| Navigateur | `http://localhost:7860` (interface), `http://localhost:8080/docs` (Swagger) | — |

---

## K. Arrêt propre

- **Backend** : dans le Terminal 2, appuyez sur `Ctrl+C` (attendez le message d'arrêt propre
  d'Uvicorn).
- **Frontend** : dans le Terminal 3, appuyez sur `Ctrl+C`.
- **Arrêter uniquement les services Docker du projet** (sans supprimer les données) :
  ```powershell
  docker compose stop postgres qdrant neo4j
  ```
- **Les redémarrer plus tard** (les données/volumes sont conservés) :
  ```powershell
  docker compose start postgres qdrant neo4j
  ```

**Différence entre `stop`, `down` et `down -v` :**

| Commande | Effet |
| --- | --- |
| `docker compose stop <services>` | Arrête les conteneurs, garde tout (conteneurs, volumes/données) — reprise instantanée avec `start` |
| `docker compose down` | Arrête **et supprime** les conteneurs (mais garde les volumes/données) — il faudra refaire `up` pour recréer les conteneurs, mais les données restent |
| `docker compose down -v` | Supprime **aussi les volumes** → **perte définitive** des données Postgres/Qdrant/Neo4j locales |

> ⚠️ **Ne lancez pas `docker compose down -v`** sans avoir bien comprendre que cela supprime
> définitivement les données des conteneurs locaux (pas `nuru_student_memory.db`, qui est un fichier
> du projet, pas un volume Docker — celui-là n'est jamais concerné par cette commande).

---

## L. Dépannage

| Symptôme | Cause probable | Commande de diagnostic | Solution |
| --- | --- | --- | --- |
| `bind: address already in use` au `docker compose up` | Port déjà utilisé par un autre programme | `Get-NetTCPConnection -LocalPort <port>` | Identifier le processus en conflit (`Get-Process -Id <PID>`), l'arrêter, ou changer le port hôte dans `docker-compose.yml` |
| Le backend reste bloqué longtemps sans nouveau log après "Base de données... initialisée" | Téléchargement/chargement du modèle d'embeddings `BAAI/bge-m3` (premier lancement) | `Get-Process python \| Select CPU,WorkingSet` (le process doit consommer du CPU, pas être figé à 0) | Patienter (peut prendre 1-2 min la première fois selon la connexion) ; si figé à 0% CPU longtemps, redémarrer |
| `curl http://localhost:11434/api/tags` ne répond pas | Ollama natif non lancé | `Get-NetTCPConnection -LocalPort 11434` | Lancer `ollama serve` (ou vérifier le service Ollama dans les applications démarrées automatiquement) |
| Modèle `llama3.2:1b` absent de `ollama list` | Modèle non téléchargé sur cette machine | `ollama list` | `ollama pull llama3.2:1b` (à faire une seule fois si vraiment absent — ce n'était pas le cas ici) |
| `⚠️ Connexion à Neo4j` en erreur dans les logs backend | Conteneur Neo4j non démarré, ou pas encore prêt | `docker compose ps`, `docker compose logs neo4j` | Attendre que le log affiche `Started.`, sinon `docker compose up -d neo4j` |
| `⚠️ Connexion à Qdrant Cloud` en erreur | Pas de connexion Internet, ou clé API expirée/invalide | Vérifier votre connexion Internet ; ne jamais afficher la clé pour diagnostiquer, juste tester `curl https://<votre-cluster>.cloud.qdrant.io:6333/collections` (nécessite la clé en en-tête, à faire prudemment) | Vérifier la connexion réseau ; en dernier recours, contacter Binta pour confirmer la validité de la clé Qdrant Cloud |
| Erreur `NativeCommandError` avec des accents bizarres dans PowerShell | Windows PowerShell 5.1 encode mal certains flux natifs redirigés (`*>&1`) | Comparer avec `curl.exe` sur la même requête | Ignorer si le contenu réel (vérifié via `curl.exe`) est correct ; ne pas rediriger `*>&1` inutilement |
| Mauvais Python sélectionné (ex. 3.14 au lieu de 3.12) | Plusieurs Python installés, `python` ambigu | `py -0p` puis `py -3.12 --version` | Toujours utiliser `py -3.12` explicitement pour ce projet sur cette machine |
| `ImportError` après activation du venv | Environnement virtuel non activé, ou mauvais venv | `Get-Command python \| Select Source` doit pointer vers `venv_win\Scripts\python.exe` | Réactiver : `.\venv_win\Scripts\Activate.ps1` |
| Frontend affiche "🤖 NURU (Mode hors-ligne)" | L'appel réseau vers l'API a échoué (backend non lancé, mauvais port) | `Invoke-RestMethod http://localhost:8080/health` | Vérifier que le backend tourne ; vérifier `$env:API_URL` du terminal frontend |
| `API_URL` incorrecte | Variable d'environnement non définie ou héritée d'un ancien terminal | `echo $env:API_URL` avant de lancer le frontend | Toujours redéfinir `$env:API_URL = "http://localhost:8080"` avant `python -m frontend.gradio_app` |
| Frontend accessible mais backend indisponible | Backend arrêté/planté alors que le frontend tourne encore | `Invoke-RestMethod http://localhost:8080/health` échoue | Relancer le backend (Terminal 2) ; le frontend se reconnectera automatiquement au prochain message envoyé |
| Erreur Gradio "Data incompatible with messages format" en envoyant un message | Ancienne version de `frontend/gradio_app.py` ou `gradio` non réinstallé après la correction | `pip show gradio` doit afficher `Version: 6.20.0` | `pip install -r requirements.txt` (ou `pip install gradio==6.20.0`) puis redémarrer le frontend — voir `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md` §27 |

---

## Quick Start

### Méthode rapide avec les scripts

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
docker compose up -d postgres qdrant neo4j
powershell -ExecutionPolicy Bypass -File scripts\run_backend_windows.ps1
```
Dans un **second terminal** :
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_frontend_windows.ps1
```

### Méthode entièrement manuelle

```powershell
# --- Terminal 1 : services Docker ---
Set-Location "c:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"
docker compose config
docker compose up -d postgres qdrant neo4j
docker compose ps

# --- Verification Ollama natif (deja installe, ne rien telecharger) ---
ollama list
Invoke-RestMethod http://localhost:11434/api/tags

# --- Environnement Python (une seule fois) ---
py -3.12 -m venv venv_win
.\venv_win\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# --- Terminal 2 : backend ---
.\venv_win\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
$env:PORT = "8080"
python -m backend.app.api.main

# --- Terminal 3 : frontend ---
.\venv_win\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
$env:API_URL = "http://localhost:8080"
$env:GRADIO_PORT = "7860"
python -m frontend.gradio_app

# --- Navigateur ---
# http://localhost:7860   (interface)
# http://localhost:8080/docs (Swagger)
```
