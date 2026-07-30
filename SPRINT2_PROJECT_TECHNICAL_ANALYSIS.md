# NURU — Analyse technique du projet (Sprint 2, Binta)

Analyse en lecture seule du dépôt reçu sous forme de ZIP. Aucune modification de code, de port, de configuration ou de dépendance n'a été effectuée. Chaque affirmation renvoie à un fichier précis du dépôt. Quand une information n'a pas pu être confirmée dans le code, c'est indiqué explicitement.

Répertoire analysé : `c:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn`
Date de l'analyse : 2026-07-15.

---

## 1. Résumé exécutif

NURU est un tuteur IA multi-agents (LangGraph) pour les mathématiques de Terminale S1/S2 (programme sénégalais), avec une API FastAPI, une interface Gradio, une base vectorielle Qdrant, un Knowledge Graph Neo4j, une mémoire élève PostgreSQL/SQLite, et un LLM local (Ollama, `llama3.2:1b`). Le pipeline d'ingestion documentaire est déjà exécuté au moins une fois avec un vrai corpus (~100 PDF de cours/exercices, voir `data/raw/` et les rapports dans `data/processed/`).

**Points bloquants majeurs identifiés :**

1. **Secrets réels exposés en clair** dans `.env` et surtout codés en dur dans `docker-compose.yml` (clé API Qdrant Cloud, identifiants Neo4j Aura). Aucun `.gitignore` n'existe dans le projet → si ce dossier est poussé sur Git tel quel, ces secrets partiraient dans l'historique. **Critique, à traiter avant tout partage/versioning.**
2. **Le fichier `docker-compose.yml` connecte le backend au Neo4j Aura (cloud) de Binta, pas au conteneur `neo4j` local pourtant démarré dans le même stack** — incohérence fonctionnelle en plus du problème de sécurité ci-dessus.
3. **Conflits de ports confirmés sur cette machine** : le port `5432` (Postgres) et le port `11434` (Ollama) sont déjà occupés par d'autres processus/projets. Le stack Docker de NURU échouera tel quel si lancé maintenant.
4. **Aucune dépendance Python n'est installée sur l'environnement Windows actuel**, et le dossier `venv/` livré dans le ZIP est un environnement **Linux** (structure `venv/bin/...`), donc inutilisable sur Windows. Le projet ne peut pas démarrer en l'état sans recréer un environnement virtuel.
5. Incohérences de port entre la documentation/`.env` (`8000`) et le code réel (`8080`) — cause probable du bug "Mode hors-ligne" déjà documenté dans le README.
6. Fichiers frontend redondants/morts (`frontend/app.py` Flask, `frontend/components/chat.py`, `frontend/utils/api_client.py`) non utilisés par le flux principal (Gradio), source de confusion.

Le reste du document détaille l'architecture, les preuves, et des recommandations classées par priorité.

---

## 2. Architecture générale

Projet **100 % Python** (pas de Node.js/npm côté frontend — l'interface est un serveur Gradio, pas une SPA JS). Aucun `package.json` applicatif trouvé (seuls ceux embarqués par la dépendance `gradio` elle-même, dans `venv/lib/python3.10/site-packages/gradio/...`).

```
Élève / Enseignant (navigateur)
        │
        ▼
Frontend Gradio (frontend/gradio_app.py) — port 7860
        │  requests HTTP (JSON)
        ▼
API FastAPI (backend/app/api/main.py) — port 8080
        │
        ▼
Orchestrateur LangGraph (backend/app/agents/graph.py)
   planner → retriever → [outil math SymPy] → cours|exercices|quiz → verifier → progression
        │                        │                                        │
        ▼                        ▼                                        ▼
  Qdrant (RAG vecteurs)   Neo4j (Knowledge Graph)         PostgreSQL/SQLite (mémoire élève)
        │                        │
        └───────────┬────────────┘
                     ▼
          Ollama (LLM local, llama3.2:1b) — génération de contenu pédagogique
```

Séparément, un **pipeline d'ingestion** (`scripts/ingest_pipeline.py`) traite les PDF de `data/raw/` → parsing → chunking pédagogique → métadonnées → embeddings → indexation Qdrant + Neo4j. Il tourne indépendamment de l'API (exécution manuelle via `run_ingest.sh`).

---

## 3. Structure du projet

```
nuru_agent_nbn/
├── backend/
│   ├── app/
│   │   ├── agents/         # Agents LangGraph (planner, retriever, cours, exercices, quiz,
│   │   │                   #  verifier, evaluation, progression) + graph.py (StateGraph) + orchestrator.py
│   │   ├── api/            # FastAPI : main.py, routes/{chat,evaluation,health,teacher}.py,
│   │   │                   #  models/{requests,responses}.py, middleware/logging.py,
│   │   │                   #  dependencies/containers.py (injection de dépendances / singletons)
│   │   ├── llm/             # ollama_client.py — client LLM local
│   │   ├── memory/          # db.py (SQLAlchemy), models.py, student_profile.py, teacher_profile.py
│   │   ├── rag/              # document_parser/, chunker/, metadata_extractor/, vector_indexer/ (Qdrant),
│   │   │                     #  knowledge_graph/ (Neo4j)
│   │   └── tools/            # math_tools.py (SymPy), sandbox.py (exécution Python restreinte)
│   ├── data/                 # raw/processed (dossiers secondaires, quasi vides — voir §8)
│   ├── tests/                # test_document_parser.py
│   └── utils/env_loader.py   # charge .env via python-dotenv
├── frontend/
│   ├── gradio_app.py         # interface Gradio réelle (Espace Élève / Espace Enseignant) — point d'entrée actif
│   ├── app.py                 # prototype Flask indépendant (legacy, non utilisé par Docker/README)
│   ├── components/chat.py     # composant Gradio non câblé dans gradio_app.py (code mort)
│   └── utils/api_client.py    # client HTTP alternatif, non utilisé par gradio_app.py (code mort)
├── scripts/                   # ingestion, checks d'environnement, tests manuels
├── tests/                     # tests unitaires/intégration (pytest)
├── data/raw/{cours,exercices}/ # ~100 PDF réels (programme sénégalais Terminale S1/S2)
├── data/processed/             # chunks + rapports d'ingestion déjà générés (preuve d'exécution réelle)
├── model/                      # cache Ollama local (manifests + blobs, ~1,3 Go) — voir §8
├── venv/                       # environnement virtuel Linux livré dans le ZIP (~445 Mo) — voir §8
├── docker-compose.yml          # stack complet (qdrant, neo4j, postgres, ollama, backend, frontend)
├── Dockerfile / frontend/Dockerfile
├── requirements.txt
├── run_api.sh / run_frontend.sh / run_all.sh / run_ingest.sh / run_tests.sh
├── README.md                   # guide d'exécution à jour (le plus fiable)
├── readme (2).md               # ancien README générique, en contradiction avec le code actuel — voir §8
├── CHANGELOG_UPDATE.md         # changelog détaillé des 3 dernières étapes livrées
├── nuru_student_memory.db      # base SQLite déjà créée localement par Binta (preuve du mode SQLite)
└── .env                        # variables réelles (contient des secrets, voir §8)
```

**Rôle des dossiers clés :**
- `backend/app/agents/` : cerveau du système — un vrai graphe LangGraph (`graph.py`), pas un simple enchaînement de fonctions.
- `backend/app/rag/` : la chaîne RAG complète, de l'extraction PDF à l'indexation vectorielle/graphe.
- `backend/app/memory/` : persistance élève/enseignant (SQLAlchemy, Postgres ou SQLite selon `DATABASE_URL`).
- `scripts/` : utilitaires opérationnels (ingestion, vérification d'environnement, tests manuels hors pytest).
- `data/` : corpus source (`raw/`) et artefacts générés (`processed/`, `ingestion_logs/`).

---

## 4. Technologies utilisées

| Composant | Technologie | Source |
|---|---|---|
| Langage | Python | Tout le dépôt (`.py`), aucun JS applicatif |
| API | FastAPI + Uvicorn | `backend/app/api/main.py`, `requirements.txt:33-34` |
| Orchestration agents | LangGraph + LangChain-core | `requirements.txt:21,26-27`, `backend/app/agents/graph.py` |
| Interface | Gradio (principal) | `frontend/gradio_app.py`, `frontend/Dockerfile` |
| Interface (legacy) | Flask | `frontend/app.py` — **dépendance `flask` absente de `requirements.txt`** |
| Base vectorielle | Qdrant (cloud ou local) | `backend/app/rag/vector_indexer/qdrant_client.py`, `docker-compose.yml` |
| Embeddings | sentence-transformers (`BAAI/bge-m3`) | `backend/app/rag/vector_indexer/config.py:20` |
| Knowledge Graph | Neo4j 5.x | `backend/app/rag/knowledge_graph/neo4j_client.py`, `docker-compose.yml` |
| Mémoire élève | SQLAlchemy 2 + PostgreSQL/psycopg3, repli SQLite | `backend/app/memory/db.py` |
| LLM local | Ollama (`llama3.2:1b`) | `backend/app/llm/ollama_client.py` |
| Calcul formel | SymPy | `backend/app/tools/math_tools.py` |
| Parsing PDF | PyMuPDF, PyPDF2, pytesseract, python-docx, Nougat (optionnel) | `backend/app/rag/document_parser/` |
| Tests | pytest | `tests/`, `backend/tests/`, `run_tests.sh` |
| Conteneurisation | Docker + Docker Compose | `Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` |

Gestionnaire de dépendances : **pip + `requirements.txt` uniquement**. Aucun `poetry.lock`, `uv.lock`, `Pipfile`, `pyproject.toml` trouvé. Le `requirements.txt` racine contient des blocs dupliqués (ex. `qdrant-client`, `python-dotenv`, `langgraph` apparaissent deux fois — traces de fusions successives par étapes de développement, sans impact fonctionnel mais à nettoyer).

---

## 5. Fonctionnement du frontend

**Point d'entrée réel : `frontend/gradio_app.py`**, lancé via `python -m frontend.gradio_app` (`run_frontend.sh`, `frontend/Dockerfile:16`). L'instance `demo` est créée au niveau module (`gradio_app.py:316-317`) pour compatibilité hot-reload/Hugging Face Spaces.

- `API_URL = os.getenv("API_URL", "http://localhost:8080")` (`gradio_app.py:23`).
- Deux espaces dans des onglets Gradio :
  - **Espace Élève** : Tableau de bord, Cours, Exercices, Quiz (un chatbot Gradio par section, mais **un seul `session_id` partagé** entre les trois), Progression, Carte des compétences, Badges, Profil (l'élève saisit lui-même un `user_id` libre, sans mot de passe).
  - **Espace Enseignant** : connexion/inscription, liaison d'élèves, statistiques de classe, génération de cours.
- Toutes les actions passent par de simples appels `requests.post/get` vers l'API (fonctions `_post`/`_get`, `gradio_app.py:29-44`), sans SDK ni websocket.
- En cas d'échec réseau, message d'erreur affiché dans le chat (`gradio_app.py:50`), pas d'écran "mode hors-ligne" dédié (celui-ci existe dans le prototype Flask, voir plus bas).

**Fichiers frontend non utilisés par ce flux (code mort, à confirmer avec Binta) :**
- `frontend/app.py` : prototype Flask indépendant, sert des pages HTML côté serveur (`/`, `/eleve`, `/prof`) avec du JS vanille qui appelle `/api/chat` (proxy local vers l'API FastAPI). Affiche un message "🤖 NURU (Mode hors-ligne)" si l'API ne répond pas (`app.py:648-650`). Port **5000 codé en dur** (`app.py:660`), non exposé dans `docker-compose.yml`/`Dockerfile`, ne semble plus être le frontend officiel (le README et les deux Dockerfiles pointent vers Gradio).
- `frontend/components/chat.py` + `frontend/utils/api_client.py` : implémentent un composant de chat Gradio alternatif (classe `ChatComponent` + `APIClient`), mais ne sont importés nulle part dans `gradio_app.py`. `api_client.py` pointe par défaut vers `http://localhost:8000` (`api_client.py:18`), incohérent avec le port réel `8080`.

---

## 6. Fonctionnement du backend

**Point d'entrée : `backend/app/api/main.py`**, lancé via `python -m backend.app.api.main` (`run_api.sh`) ou `uvicorn.run(app, host="0.0.0.0", port=port)` où `port = int(os.getenv("PORT", 8080))` (`main.py:107`).

- CORS : `allow_origins=["*"]`, `allow_credentials=True` (`main.py:29-35`) — voir §8 pour le risque associé.
- Au démarrage (`@app.on_event("startup")`, `main.py:49-65`) : initialise la mémoire élève (crée les tables SQL si besoin) et précharge l'orchestrateur LangGraph pour détecter tôt les erreurs de configuration (Qdrant/Neo4j indisponibles → avertissement, pas de crash : dégradation gracieuse).
- Routers montés : `chat` (`/chat/...`), `health` (`/health`), `evaluation` (`/evaluation/...`), `teacher` (`/teacher/...`).
- Route de secours `/chat/simple` : contourne le graphe LangGraph, fait un RAG + appel LLM direct, utile pour tester Qdrant/Ollama isolément (`main.py:80-103`).

**Injection de dépendances (`dependencies/containers.py`)** : singletons process-global pour `HybridRetriever` (Qdrant), `GraphQueries` (Neo4j), `OrchestratorAgent` (graphe LangGraph complet), et un `SimpleSessionManager` en mémoire RAM (dict Python) — le commentaire du code indique explicitement *"à remplacer par Redis en production"* (`containers.py:70`), mais **aucun Redis n'est configuré ni utilisé actuellement** (aucune variable `REDIS_URL` trouvée dans tout le dépôt).

**Graphe multi-agents (`backend/app/agents/graph.py`)**, construit avec `langgraph.graph.StateGraph` :

```
START → planner → retriever → [math_tool ?] → dispatch → {cours | exercices | quiz} → verifier → progression → END
```

- **Planner** (`planner.py`) : détection d'intention par mots-clés français (cours/exercice/quiz/calcul/général), niveau d'aide pédagogique façon Khanmigo (`reformulation → rappel → indice → solution_guidée → solution_complète`) avec escalade automatique selon le nombre d'itérations, extraction naïve du concept par regex.
- **Retriever** (`retriever_agent.py`) : interroge Qdrant (recherche hybride dense + pondération façon BM25) et Neo4j (prérequis/relations), construit le contexte injecté au LLM.
- **Outil math** (`tools/math_tools.py`) : calcul exact via SymPy (dérivée, primitive/intégrale définie, résolution d'équation, simplification, factorisation, limite, étude de fonction) — jamais délégué au LLM, appelé conditionnellement si le Planner détecte une demande de calcul (`graph.py:169-170`).
- **Cours / Exercices / Quiz** : génèrent le contenu via Ollama (`llm/ollama_client.py`), avec repli sur des gabarits texte si Ollama est indisponible (dégradation gracieuse, testée sans LLM selon `CHANGELOG_UPDATE.md:87-96`).
- **Verifier** : score de cohérence par réponse d'agent, moyenne = `confidence_score` renvoyé au frontend.
- **Progression** : journalise l'échange (`Interaction`), met à jour la maîtrise par notion (`ConceptMastery`, moyenne mobile exponentielle — "mastery learning"), suggère la prochaine étape pédagogique, calcule badges et carte de compétences (fusion mémoire élève + Knowledge Graph si disponible).

**Outil sandbox (`tools/sandbox.py`)** : exécution Python restreinte dans un **processus séparé** avec timeout de 5 s, builtins strictement whitelistés, aucun `import` arbitraire (seuls `math`/`numpy`/`matplotlib` injectés) — testé pour bloquer `import os; os.system(...)` selon le changelog. Sert à tracer des fonctions (image base64).

**Authentification / autorisation :**
- **Enseignant** (`memory/teacher_profile.py`) : mot de passe haché avec **PBKDF2-HMAC-SHA256 salé, 260 000 itérations** (pas de dépendance externe type bcrypt/passlib). `POST /teacher/login` renvoie directement `{id, email, name}` **sans jeton de session** — le frontend Gradio stocke cet `id` en clair dans un état de session côté navigateur (`gradio_app.py:203`) et l'envoie tel quel à chaque appel (`teacher_id` dans le corps JSON). **N'importe quel client connaissant/devinant un `teacher_id` (UUID) peut appeler les routes `/teacher/students/{id}`, `/teacher/class-stats/{id}`, `/teacher/link-student` sans re-prouver son identité** — pas de vérification d'appartenance dans `routes/teacher.py`. Le code source le documente lui-même comme volontairement simplifié (`teacher_profile.py:6-9`, *"à durcir avant une mise en production à plus grande échelle"*).
- **Élève** : aucune authentification — `user_id` est une chaîne libre saisie dans l'onglet Profil (`gradio_app.py:162`), utilisée pour retrouver/créer un `Student` en base (`_get_student_id`, `chat.py:24-35`). Usurpation triviale (deviner/réutiliser l'identifiant d'un autre élève donne accès à sa progression).

**Chargement des variables d'environnement :** `backend/utils/env_loader.py` charge `.env` via `python-dotenv` (chemin recalculé relatif au fichier). **Attention** : ce loader n'est importé nulle part dans les modules `backend/app/...` qui lisent réellement les variables (`os.getenv` direct dans `config.py`, `main.py`, etc.) — ce sont les scripts (`run_api.sh` via `export $(cat .env ...)`, ou un `.env` chargé par un outil externe type `docker compose --env-file`) qui rendent ces variables disponibles. **Non confirmé dans le code** : que `backend/app/api/main.py` charge lui-même `.env` s'il est lancé directement sans passer par `run_api.sh` — à vérifier en pratique (voir §9).

---

## 7. Base de données et services externes

| Service | Rôle | Mode configuré | Preuve |
|---|---|---|---|
| **PostgreSQL** (ou SQLite en repli) | Mémoire élève/enseignant : profils, interactions, résultats, maîtrise, badges | Postgres si `DATABASE_URL` défini, sinon SQLite auto (`sqlite:///./nuru_student_memory.db`) | `backend/app/memory/db.py:21-32` ; le fichier `nuru_student_memory.db` (98 Ko) existe déjà à la racine → preuve que Binta a fait tourner le système en mode SQLite localement |
| **Qdrant** | Base vectorielle RAG (recherche sémantique hybride) | Cloud (`.env`) en local direct, conteneur local si lancé via Docker Compose (override d'env) | `.env:5-6`, `docker-compose.yml:2-7,44` |
| **Neo4j** | Knowledge Graph (prérequis/relations entre concepts) | **Cloud Aura, y compris en mode Docker Compose** (voir incohérence §8) | `.env:10-13`, `docker-compose.yml:45-48` |
| **Ollama** | LLM local (`llama3.2:1b`) pour génération de contenu pédagogique | Local natif (déjà installé et actif sur cette machine, modèle déjà téléchargé — voir `model/manifests/...`) ou conteneur Docker | `backend/app/llm/ollama_client.py`, `docker-compose.yml:30-35` |
| Gemini API | Mentionnée en variable optionnelle, **non intégrée dans le code actuel** | Placeholder uniquement | `.env:16` (`GEMINI_API_KEY=your-gemini-api-key-here`) ; aucune référence à `gemini`/`google.generativeai` trouvée dans `backend/` |
| Redis | Mentionné en commentaire comme cible future pour les sessions | **Non implémenté** | `containers.py:70` (commentaire), aucune variable `REDIS_URL` ni import `redis` nulle part |
| Nougat OCR | Extraction avancée de formules mathématiques (optionnelle) | Repli automatique sur PyMuPDF si absent | `backend/app/rag/document_parser/nougat_adapter.py:17-25`, `requirements.txt:37` |

---

## 8. Flux de données

```text
Élève / Enseignant (navigateur)
   → Frontend Gradio (port 7860, frontend/gradio_app.py)
   → requête HTTP JSON (requests.post) vers l'API backend
   → API FastAPI (port 8080, backend/app/api/routes/chat.py "POST /chat/")
   → OrchestratorAgent.process() → NuruGraph.invoke() (backend/app/agents/graph.py)
        → Planner (intention + niveau d'aide)
        → Retriever (Qdrant + Neo4j) — contexte documentaire et graphe
        → [Outil SymPy si demande de calcul détectée]
        → Agent de contenu (Cours | Exercices | Quiz) — génération via Ollama + contexte RAG
        → Verifier (score de cohérence)
        → Progression (écrit dans PostgreSQL/SQLite, calcule maîtrise/badges)
   → Réponse JSON (response, intent, level, confidence, progression_summary, math_tool_result)
   → Frontend Gradio affiche la réponse dans le chatbot et peut rafraîchir Progression/Badges/Carte des compétences
```

Chaîne séparée, exécutée manuellement (pas déclenchée par l'API) :

```text
PDF (data/raw/cours|exercices)
   → scripts/ingest_pipeline.py
   → document_parser (PyMuPDF, + Nougat en option)
   → chunker (chunking pédagogique)
   → metadata_extractor (classe/série/chapitre/difficulté)
   → vector_indexer (embeddings BGE-M3 → Qdrant)
   → knowledge_graph (extraction de concepts → Neo4j)
   → rapports dans data/processed/reports/ + logs dans data/ingestion_logs/pipeline.log
```

Preuve que cette chaîne a déjà tourné avec succès : `data/processed/ingestion_report_20260710_020450.json`, `ingestion_report_20260710_110421.json`, `data/processed/chunks/*.json`, `data/ingestion_logs/pipeline.log`.

---

## 9. Inventaire des ports

| Composant | Port actuel | Fichier source | Variable/config | Obligatoire ou modifiable | Risque de conflit sur cette machine |
|---|---:|---|---|---|---|
| API Backend (FastAPI) | **8080** | `backend/app/api/main.py:107` ; `Dockerfile:28` ; `docker-compose.yml:42` ; `run_all.sh:9` | `PORT` (env, défaut 8080) | Modifiable via `PORT` | **Libre actuellement** (vérifié) |
| Frontend Gradio | **7860** | `frontend/gradio_app.py:320` ; `frontend/Dockerfile:14` ; `docker-compose.yml:65` | `GRADIO_PORT` (env, défaut 7860) | Modifiable via `GRADIO_PORT` | **Libre actuellement** |
| Frontend Flask (legacy) | **5000** | `frontend/app.py:660` | **codé en dur**, aucune variable d'env | Non modifiable sans éditer le code | Libre actuellement, mais fichier probablement obsolète |
| Qdrant (conteneur local) | **6333** | `docker-compose.yml:5` | interne = hôte = 6333 | Modifiable (mapping hôte) | **Libre actuellement** |
| Neo4j Browser | **7474** | `docker-compose.yml:14` | fixe dans compose | Modifiable (mapping hôte) | **Libre actuellement** |
| Neo4j Bolt | **7687** | `docker-compose.yml:15` ; `backend/app/rag/knowledge_graph/config.py:14,63` (défaut `bolt://localhost:7687`) | `NEO4J_URI` | Modifiable (mapping hôte) | **Libre actuellement** |
| PostgreSQL | **5432** | `docker-compose.yml:26` | fixe dans compose | Modifiable (mapping hôte) | **⚠️ OCCUPÉ** (Docker Desktop / wslrelay d'un autre projet écoute déjà sur 5432) |
| Ollama | **11434** | `docker-compose.yml:33` ; README | `OLLAMA_HOST` | Modifiable (mapping hôte) | **⚠️ OCCUPÉ** (un processus `ollama` natif tourne déjà sur cette machine, modèle déjà téléchargé dans `model/`) |
| Variable `API_URL` dans `.env` | **8000** (incohérent) | `.env:22` | `API_URL` | — | Ne correspond à **aucun service réellement lancé sur 8000** ; incohérent avec le port réel de l'API (8080) |
| Variable `FRONTEND_PORT` dans `.env` | 7860 | `.env:23` | `FRONTEND_PORT` | — | **Variable jamais lue par le code** (`gradio_app.py` lit `GRADIO_PORT`, pas `FRONTEND_PORT`) — sans effet |
| `scripts/test_api.py` | **8000** (codé en dur) | `scripts/test_api.py:14` | `BASE_URL = "http://localhost:8000"` | Non modifiable sans éditer le script | Incohérent avec le port réel de l'API (8080) — ce script échouera contre une API lancée normalement |
| `frontend/utils/api_client.py` | **8000** (codé en dur, code mort) | `api_client.py:18` | valeur par défaut du constructeur | Non modifiable sans éditer le code | Incohérent, mais fichier non utilisé actuellement |

**Vérification des ports fréquemment utilisés par vos autres projets (état réel constaté sur la machine, `Get-NetTCPConnection`) :**

| Port | État constaté | Process |
|---:|---|---|
| 3000 | Occupé | `com.docker.backend` / `wslrelay` (autre projet Docker) |
| 8000 | Libre | — |
| 8011 | Occupé | `com.docker.backend` / `wslrelay` |
| 8005 | Libre | — |
| 5432 | **Occupé** | `com.docker.backend` / `wslrelay` — **conflit direct avec NURU** |
| 6379 | Occupé | `com.docker.backend` / `wslrelay` (probablement Redis d'un autre projet) |
| 3306 | Occupé | `mysqld` |
| 3307 | Occupé | `mysqld` |
| 80 | Occupé | `httpd` |
| 443 | Libre | — |
| 6333 (Qdrant) | Libre | — |
| 7474 / 7687 (Neo4j) | Libre | — |
| 11434 (Ollama) | **Occupé** | `ollama` (processus natif déjà lancé, hors Docker) — **conflit direct avec NURU** |

Aucun des ports `3000/8011/8005/3306/3307/80` n'est référencé dans le code de NURU (vérifié par recherche exhaustive) — ils ne posent donc pas de risque pour **ce** projet, mais confirment que la machine héberge déjà plusieurs stacks actives.

---

## 10. Proposition de nouveaux ports

Tous les ports candidats ci-dessous ont été vérifiés **libres** sur cette machine au moment de l'analyse. Seuls les ports **exposés côté hôte** sont proposés au changement ; les ports **internes aux conteneurs** ne sont pas modifiés (conformément à la consigne de ne pas toucher aux ports internes Docker sans nécessité).

| Composant | Port actuel (hôte) | Port proposé (hôte) | Port interne conteneur (inchangé) | Fichiers à modifier | Variables à modifier | Impact |
|---|---:|---:|---:|---|---|---|
| Frontend Gradio | 7860 | **3100** | 7860 | `docker-compose.yml` (mapping `"3100:7860"`), `.env` si vous y ajoutez `GRADIO_PORT`/`FRONTEND_URL` | Aucune variable applicative à changer (le conteneur écoute toujours en interne sur 7860) ; seule l'URL d'accès navigateur change en `http://localhost:3100` | Faible — juste l'URL d'accès change |
| API Backend | 8080 | **8110** | 8080 | `docker-compose.yml` (mapping backend `"8110:8080"` + `frontend.environment.API_URL` → `http://backend:8080` **inchangé**, c'est une URL inter-conteneurs) ; côté hôte, tout script/`curl` local doit viser `http://localhost:8110` | `API_URL` utilisé par un frontend lancé **hors Docker** (ex. `export API_URL=http://localhost:8110`) | Moyen — mettre à jour les commandes `curl`/README locales, mais aucune URL inter-conteneurs à changer |
| PostgreSQL | 5432 | **5433** | 5432 | `docker-compose.yml` (mapping `"5433:5432"`) | `DATABASE_URL` **inter-conteneurs reste `postgres:5432`** (inchangé, c'est le réseau Docker interne) ; seul un client externe (ex. `psql` depuis Windows) doit viser `localhost:5433` | **Nécessaire** — 5432 déjà occupé sur cette machine |
| Ollama | 11434 | **11435** (ou ne pas exposer le conteneur du tout, voir remarque) | 11434 | `docker-compose.yml` (mapping `"11435:11434"`) | `OLLAMA_HOST` **inter-conteneurs reste `http://ollama:11434`** (inchangé) ; seul un accès direct depuis l'hôte (`curl http://localhost:.../api/tags`) change de port | **Nécessaire** — 11434 déjà occupé par un Ollama natif sur cette machine |
| Qdrant | 6333 | 6333 (inchangé, libre) | 6333 | — | — | Aucun changement requis actuellement |
| Neo4j Browser / Bolt | 7474 / 7687 | 7474 / 7687 (inchangé, libre) | 7474 / 7687 | — | — | Aucun changement requis actuellement, **mais voir remarque ci-dessous** |

**Remarque importante sur Ollama** : un Ollama natif tourne déjà sur `11434` sur cette machine, avec le modèle `llama3.2:1b` déjà téléchargé (`model/manifests/registry.ollama.ai/library/llama3.2/1b`). Plutôt que de dupliquer le modèle dans un second conteneur Docker (téléchargement de plusieurs Go supplémentaires), il est probablement plus simple de **retirer le service `ollama` de `docker-compose.yml`** et de faire pointer le backend conteneurisé vers l'Ollama natif via `OLLAMA_HOST=http://host.docker.internal:11434` (Docker Desktop Windows résout `host.docker.internal` vers l'hôte). Ceci est une **proposition à valider avec vous avant application** — non appliquée dans cette analyse.

**Remarque sur Neo4j** : tant que `docker-compose.yml` pointera `NEO4J_URI` vers l'instance Aura cloud (voir §12), changer le port du conteneur `neo4j` local n'aura aucun effet pratique sur le fonctionnement du backend — ce conteneur restera démarré mais inutilisé. Ce point doit être corrigé indépendamment du plan de ports (voir Priorité 1, §19).

**Distinctions demandées :**
- **Port interne conteneur** : toujours identique au port applicatif natif du service (8080 FastAPI, 7860 Gradio, 5432 Postgres, 6333 Qdrant, 7474/7687 Neo4j, 11434 Ollama) — non modifié.
- **Port exposé sur l'hôte** : celui qui change dans le tableau ci-dessus (partie gauche du mapping `"hôte:conteneur"` dans `docker-compose.yml`).
- **URL utilisée par le frontend (navigateur)** : `http://localhost:3100` (proposé) pour l'UI, appels API vers `http://localhost:8110` si le frontend tourne hors Docker ; en Docker, le frontend appelle `http://backend:8080` (réseau interne, inchangé).
- **Origine autorisée par CORS** : actuellement `allow_origins=["*"]` (`main.py:31`) — fonctionne avec n'importe quel port frontend, mais voir §16/§18 pour la recommandation de restreindre cette origine.
- **URLs inter-conteneurs** (`http://backend:8080`, `http://qdrant:6333`, `http://ollama:11434`, `postgres:5432`) : basées sur les noms de service Docker Compose, **jamais impactées** par un changement de port hôte.

---

## 11. Variables d'environnement

Valeurs sensibles masquées (4 premiers + 4 derniers caractères, comme le fait déjà `scripts/check_env.py:39-40`).

| Variable | Composant | Description | Obligatoire | Exemple (non sensible) | Fichier(s) où utilisée |
|---|---|---|---|---|---|
| `QDRANT_URL` | RAG | URL du cluster Qdrant (cloud ou local) | Oui (sinon repli sur une URL factice `your-qdrant-cluster...`) | `http://localhost:6333` | `.env:5`, `vector_indexer/config.py:60` |
| `QDRANT_API_KEY` | RAG | Clé API Qdrant Cloud | Optionnel (vide si Qdrant local) | *(vide en local)* — **valeur réelle présente dans `.env`, masquée : `eyJh…Eong`** | `.env:6`, `vector_indexer/config.py:61` |
| `QDRANT_COLLECTION` | RAG | Nom de la collection vectorielle | Non (défaut `nuru_maths`) | `nuru_maths` | `.env:7` |
| `NEO4J_URI` | Knowledge Graph | URI de connexion Neo4j | Oui pour un vrai KG (sinon dégradation gracieuse) | `bolt://localhost:7687` | `.env:10`, `knowledge_graph/config.py:63` |
| `NEO4J_USER` | Knowledge Graph | Utilisateur Neo4j | Oui | `neo4j` | `.env:11` |
| `NEO4J_PASSWORD` | Knowledge Graph | Mot de passe Neo4j | Oui | *(non fourni ici)* — **valeur réelle présente dans `.env` et `docker-compose.yml`, masquée : `RF6M…zQ3U`** | `.env:12`, `docker-compose.yml:47` |
| `NEO4J_DATABASE` | Knowledge Graph | Nom de la base Neo4j | Non (défaut `neo4j`) | `neo4j` | `.env:13` |
| `GEMINI_API_KEY` | (non branché) | Clé API Gemini, mentionnée mais non utilisée dans le code actuel | Non | `your-gemini-api-key-here` | `.env:16` |
| `DATABASE_URL` | Mémoire élève | Chaîne de connexion PostgreSQL ; vide → SQLite auto | Non | `postgresql+psycopg://nuru:nuru_password@localhost:5432/nuru` | `backend/app/memory/db.py:25` |
| `OLLAMA_MODEL` | LLM | Nom du modèle Ollama | Non (défaut `llama3.2:1b`) | `llama3.2:1b` | `main.py:87`, `docker-compose.yml:50` |
| `OLLAMA_HOST` | LLM | Hôte du serveur Ollama (utilisé uniquement en Docker) | Non | `http://ollama:11434` | `docker-compose.yml:51` |
| `PORT` | Backend | Port d'écoute d'Uvicorn | Non (défaut `8080`) | `8080` | `main.py:107`, `Dockerfile:28` |
| `API_URL` | Frontend | URL de l'API vue par le frontend | Non (défaut `http://localhost:8080`) | `http://localhost:8080` | `gradio_app.py:23`, `app.py:12`, **incohérent avec `.env:22` qui vaut `8000`** |
| `GRADIO_PORT` | Frontend | Port d'écoute de Gradio | Non (défaut `7860`) | `7860` | `gradio_app.py:320`, `frontend/Dockerfile:14` |
| `FRONTEND_PORT` | (non lu par le code) | Présente dans `.env` mais jamais lue par `gradio_app.py` | — | `7860` | `.env:23` (variable orpheline) |
| `LOG_LEVEL` | Global | Niveau de log | Non (défaut `INFO`) | `INFO` | `.env:19` |
| `DEBUG` | Global | Mode debug | Non | `True` | `.env:20` |
| `ENVIRONMENT` | Global | Environnement (`development`/`production`) | Non | `development` | `.env:21` |
| `RAW_DIR` / `PROCESSED_DIR` | Ingestion | Chemins des données source/traitées | Non (défauts `data/raw`, `data/processed`) | `data/raw` | `scripts/ingest_config.py:61-62` |
| `USE_NOUGAT` | Ingestion | Active l'OCR Nougat | Non (défaut `False`) | `False` | `scripts/ingest_config.py:63` |
| `BATCH_SIZE` | Ingestion | Taille de lot pour l'ingestion | Non (défaut `32`) | `32` | `scripts/ingest_config.py:64` |

Un fichier `.env.example` (sans secrets) **n'existe pas** dans le dépôt — voir §12. Contenu proposé (à créer, non créé automatiquement dans cette analyse en lecture seule) :

```bash
# NURU - Exemple de configuration (.env.example)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=nuru_maths

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me
NEO4J_DATABASE=neo4j

DATABASE_URL=

OLLAMA_MODEL=llama3.2:1b
OLLAMA_HOST=http://localhost:11434

PORT=8080
API_URL=http://localhost:8080
GRADIO_PORT=7860

LOG_LEVEL=INFO
DEBUG=True
ENVIRONMENT=development
```

---

## 12. Prérequis

| Outil | Version demandée par la doc/le code | Preuve | Version réellement installée sur cette machine |
|---|---|---|---|
| Python | 3.10+ (README) / 3.11-slim (Dockerfile) | `README.md:40` ; `Dockerfile:2` | **3.12.9** (système) — aucune contrainte stricte trouvée (`.python-version` absent), donc probablement compatible mais **non testé par Binta sur 3.12** |
| pip | récent | `README.md:41` | 24.3.1 |
| Docker / Docker Compose | recommandé | `README.md:42` | Docker 29.4.1, Docker Compose v5.1.3 — présents et fonctionnels |
| Ollama | dernière | `README.md:43` | Présent et **déjà actif** (port 11434 en écoute), modèle `llama3.2:1b` déjà téléchargé |
| Git | — | `README.md:44` | Non vérifié dans cette analyse (non nécessaire, le dossier n'est pas un dépôt git) |
| Node.js / npm | **Non applicable** | Aucun `package.json` applicatif, aucun build JS | — |

Aucun `.python-version`, `pyproject.toml`, `poetry.lock`, `uv.lock`, `.nvmrc` trouvé dans le dépôt. Seul `requirements.txt` fixe des bornes minimales (`>=`), sans version exacte ni fichier de verrouillage — deux installations à des dates différentes peuvent donc obtenir des versions différentes de FastAPI/LangGraph/etc.

**Clés/API externes nécessaires** : `QDRANT_API_KEY` (si Qdrant Cloud), `NEO4J_PASSWORD` (obligatoire pour un vrai Knowledge Graph). `GEMINI_API_KEY` listé mais non utilisé par le code actuel.

---

## 13. Installation locale

**⚠️ Constat clé pour cette machine** : aucune des dépendances du projet n'est installée sur le Python système actuel (vérifié : `fastapi`, `langgraph`, `sqlalchemy`, `sympy`, `gradio`, etc. sont tous absents). Le dossier `venv/` livré dans le ZIP a été créé sous **Linux** (`venv/bin/python3.10`, pas de `venv/Scripts/python.exe`) et **ne fonctionnera pas sur Windows**. Il faut recréer un environnement virtuel Windows avant toute exécution.

### PowerShell (Windows — recommandé sur cette machine)

```powershell
# 1. Se placer dans le dossier du projet
Set-Location "c:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"

# 2. (Optionnel mais recommandé) Supprimer le venv Linux inutilisable
# Remove-Item -Recurse -Force venv    # <-- à valider avec Binta avant suppression

# 3. Créer un environnement virtuel Windows
python -m venv venv_win
.\venv_win\Scripts\Activate.ps1

# 4. Installer les dépendances
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Vérifier
python -c "import langgraph, sympy, sqlalchemy, fastapi; print('Dépendances OK')"
```

### Linux/macOS (équivalent)

```bash
cd nuru_agent_nbn
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note** : `torch`/`transformers` (requirements.txt:2-3) sont des dépendances lourdes (plusieurs centaines de Mo à plus d'1 Go selon la plateforme) ; leur installation n'a pas été exécutée dans cette analyse (délibérément, phase en lecture seule — voir §14).

---

## 14. Lancement du backend

```powershell
# Variables d'environnement (charger .env, ou les définir manuellement)
# PowerShell ne supporte pas `export $(cat .env)` comme run_api.sh (Bash) — équivalent :
Get-Content .env | Where-Object { $_ -match '=' -and $_ -notmatch '^#' } | ForEach-Object {
    $k,$v = $_ -split '=',2
    Set-Item -Path "Env:$k" -Value $v
}

# Lancer l'API (port 8080 par défaut)
python -m backend.app.api.main
```

Vérification :
```powershell
Invoke-RestMethod http://localhost:8080/health
Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat/ -ContentType "application/json" -Body '{"message":"Explique-moi les nombres complexes"}'
```
Documentation interactive : `http://localhost:8080/docs`.

**Le script `run_api.sh` est un script Bash** (`#!/bin/bash`) — il ne s'exécute pas nativement sous PowerShell. Sous Windows, utilisez Git Bash/WSL pour le lancer tel quel, ou la commande PowerShell équivalente ci-dessus.

---

## 15. Lancement du frontend

```powershell
# Dans un second terminal (après avoir activé le même venv)
$env:API_URL = "http://localhost:8080"   # doit correspondre au port réel de l'API
python -m frontend.gradio_app
```
Ouvrir `http://localhost:7860` (deux onglets : Espace Élève / Espace Enseignant).

`run_frontend.sh` est également un script Bash (nécessite Git Bash/WSL sous Windows).

---

## 16. Lancement avec Docker

Fichiers utilisés : `docker-compose.yml` (racine), `Dockerfile` (backend), `frontend/Dockerfile`.

```powershell
# Build + lancement complet
docker compose up -d --build

# Télécharger le modèle Ollama dans le conteneur (une seule fois)
docker compose exec ollama ollama pull llama3.2:1b

# Vérifier l'état des services
docker compose ps

# Logs
docker compose logs -f backend
docker compose logs -f frontend

# Arrêt
docker compose down          # conserve les volumes (données Qdrant/Neo4j/Postgres)
docker compose down -v       # supprime aussi les volumes — DESTRUCTIF, à utiliser en connaissance de cause
```

**⚠️ Avant de lancer cette commande sur cette machine**, `docker compose up` échouera très probablement à publier les ports `5432` (Postgres) et `11434` (Ollama), déjà occupés par d'autres processus (voir §9/§10). Ce point est à corriger (remapping des ports hôte, §10) **avant** un premier essai Docker complet — il s'agit d'une proposition à valider, aucun changement n'a été appliqué automatiquement.

Migration de la base de données : aucun outil de migration (Alembic, etc.) n'est présent dans le dépôt — les tables sont créées automatiquement au démarrage via `Base.metadata.create_all(bind=engine)` (`backend/app/memory/db.py:45-51`, appelé par `student_profile.ensure_initialized()` au startup de l'API). **Il n'y a donc pas de système de migrations versionnées** — voir §18.

---

## 17. Procédures de validation exécutées

| Vérification | Commande | Résultat | Statut | Cause si échec / remarque |
|---|---|---|---|---|
| Validation syntaxique Python (tous les fichiers) | `python -m py_compile <tous les .py de backend/frontend/scripts/tests>` | Aucune erreur de syntaxe sur l'ensemble des fichiers | ✅ Réussi | — |
| Validation `docker-compose.yml` | `docker compose config` | Fichier syntaxiquement valide, résolu sans erreur | ✅ Réussi | — |
| Versions Docker / Compose | `docker --version` ; `docker compose version` | Docker 29.4.1, Compose v5.1.3 | ✅ Réussi (outils présents et à jour) | — |
| Détection des ports en écoute | `Get-NetTCPConnection -LocalPort ... -State Listen` | Voir tableau §9 | ✅ Réussi | Conflits confirmés sur 5432 et 11434 |
| Résolution des dépendances Python (import réel) | `python -c "import fastapi, langgraph, sqlalchemy, ..."` | **Toutes les dépendances manquantes** sur le Python système actuel | ❌ Échec (attendu) | Aucun environnement virtuel Windows fonctionnel n'existe encore sur cette machine — nécessite l'installation de §13 |
| `pip install -r requirements.txt` | — | **Non exécuté** | ⏸️ Non exécuté | Décision volontaire : installation lourde (torch/transformers, plusieurs centaines de Mo), modification durable de l'environnement — à faire après validation du plan avec vous, pas en phase de lecture seule |
| Suite de tests pytest (`run_tests.sh`, `tests/`) | `pytest tests/ -v` | **Non exécuté** | ⏸️ Non exécuté | Dépendances non installées (voir ci-dessus) ; nécessiterait aussi d'écrire dans `nuru_student_memory.db` existant pour les tests d'intégration — évité par prudence tant que la base existante de Binta n'est pas sauvegardée |
| Build frontend (JS) | — | Non applicable | ➖ N/A | Pas de build JS : Gradio est servi directement par Python |
| Lint / type-check | — | **Non exécuté** | ⏸️ Non exécuté | Aucun outil de lint/type-check (ruff, mypy, flake8) configuré dans le dépôt (aucun fichier `ruff.toml`, `mypy.ini`, `.flake8` trouvé) |
| Détection des ports codés en dur | Recherche exhaustive (`grep`) sur tout le dépôt | Voir §9 | ✅ Réussi | Plusieurs incohérences relevées (8000 vs 8080, `FRONTEND_PORT` orpheline) |

---

## 18. Problèmes et éléments manquants

### Critique

1. **Secrets réels en clair dans le dépôt, sans `.gitignore`.**
   Preuve : `.env:6` (clé API Qdrant Cloud complète), `.env:12` et `docker-compose.yml:47` (mot de passe Neo4j Aura complet, identique dans les deux fichiers). Aucun `.gitignore` n'existe à la racine (vérifié : absent).
   Impact : si ce dossier est initialisé en dépôt Git et poussé (GitHub, etc.), ces identifiants partent dans l'historique et deviennent quasi impossibles à retirer proprement (rotation des clés nécessaire).
   Correction recommandée : créer un `.gitignore` incluant `.env`, `venv/`, `model/`, `__pycache__/`, `*.db`, `logs/` ; **faire tourner les clés Qdrant/Neo4j exposées** (les considérer comme compromises dès maintenant, puisqu'elles ont transité par un ZIP) ; ne garder que `.env.example` versionné.
   Fichiers concernés : `.env`, `docker-compose.yml`.

2. **`docker-compose.yml` connecte le backend au Neo4j Aura cloud de Binta, pas au conteneur `neo4j` local démarré dans le même stack.**
   Preuve : `docker-compose.yml:9-17` démarre un service `neo4j` local (`NEO4J_AUTH: neo4j/nuru_password`, ports 7474/7687) ; mais `docker-compose.yml:45-48` fixe `NEO4J_URI: neo4j+s://6c62c3e9.databases.neo4j.io` (cloud) pour le service `backend` — le conteneur local est démarré pour rien.
   Impact : consommation inutile de ressources (le conteneur Neo4j local tourne sans être utilisé) ; dépendance réseau cachée vers un compte cloud personnel de Binta ; confusion pour quiconque cherche à comprendre où sont les données du Knowledge Graph.
   Correction recommandée : soit faire pointer `backend.environment.NEO4J_URI` vers `neo4j://neo4j:7687` (service local) avec `NEO4J_PASSWORD: nuru_password`, soit supprimer le service `neo4j` du compose si l'intention est réellement d'utiliser Aura en permanence — à clarifier avec Binta.
   Fichiers concernés : `docker-compose.yml`.

### Élevé

3. **Aucun environnement Python fonctionnel sur cette machine.** Le `venv/` livré est un environnement Linux (`venv/bin/python3.10`), inutilisable tel quel sous Windows ; aucune dépendance n'est installée sur le Python système (3.12). Preuve : `find venv -iname python*` ne renvoie que `venv/bin/...` ; `python -c "import fastapi"` échoue. Impact : le projet ne démarre pas en l'état. Correction : recréer un venv Windows (§13).

4. **Conflits de ports Docker confirmés** sur `5432` (Postgres) et `11434` (Ollama) — voir §9/§10. Impact : `docker compose up` échouera à publier ces ports tant qu'un autre processus les occupe. Correction : appliquer le remapping proposé en §10 (à valider avant application).

5. **Incohérence de port API (`8000` vs `8080`)** entre `.env:22` (`API_URL=http://localhost:8000`), `scripts/test_api.py:14` (`BASE_URL = "http://localhost:8000"`), `frontend/utils/api_client.py:18` (défaut `8000`) d'une part, et le port réel de l'API (`8080`, confirmé dans `main.py`, `Dockerfile`, `docker-compose.yml`, `README.md`, `run_all.sh`) d'autre part. Impact : c'est très probablement la cause du "Mode hors-ligne" documenté dans le README (`README.md:358-373`) si quelqu'un exporte `API_URL` depuis `.env` tel quel. Correction : aligner `.env` sur `8080`, ou documenter clairement que `.env:API_URL` n'est pas utilisé par défaut (il ne l'est pas : `gradio_app.py` a son propre défaut `8080` codé en dur, il ne lit `.env` que si la variable est explicitement exportée dans l'environnement du process).

6. **Dépendance `flask` utilisée mais absente de `requirements.txt`.** Preuve : `frontend/app.py:7` (`from flask import Flask...`) ; recherche de `flask` dans `requirements.txt` → aucune occurrence. Impact : `frontend/app.py` plantera à l'import si quelqu'un essaie de le lancer sans avoir installé Flask manuellement. Correction : soit ajouter `flask` à `requirements.txt` si ce fichier doit rester maintenu, soit le supprimer s'il s'agit d'un prototype obsolète (à confirmer avec Binta — voir point 8).

7. **CORS entièrement ouvert combiné à `allow_credentials=True`.** Preuve : `backend/app/api/main.py:29-35` (`allow_origins=["*"], allow_credentials=True`). C'est une combinaison non conforme à la spécification CORS (les navigateurs modernes rejettent ou ignorent les credentials avec un wildcard) et, si elle fonctionnait, ouvrirait l'API à n'importe quelle origine. Impact : faible en développement local, mais à corriger avant tout déploiement public. Correction : restreindre `allow_origins` à la liste explicite des origines frontend (ex. `http://localhost:3100`), retirer `allow_credentials=True` si non nécessaire.

8. **Autorisation manquante côté enseignant** (voir détail §6) : les routes `/teacher/students/{teacher_id}`, `/teacher/class-stats/{teacher_id}`, `/teacher/link-student` ne vérifient pas qu'un jeton/session valide correspond au `teacher_id` fourni. Preuve : `backend/app/api/routes/teacher.py` (aucune dépendance d'authentification sur ces routes). Impact : un `teacher_id` connu ou deviné donne accès aux données de tous les élèves liés à ce compte. Correction : introduire un jeton de session signé (JWT ou équivalent) et vérifier sur chaque route protégée. Le code lui-même reconnaît cette limite (`teacher_profile.py:6-9`).

### Moyen

9. **`readme (2).md` contredit `README.md` actuel.** Preuve : `readme (2).md:254,261,436,458,465,678` référence `backend.api.main` et `frontend.app` (chemins/point d'entrée obsolètes, remplacés par `backend.app.api.main` et `frontend.gradio_app` selon `CHANGELOG_UPDATE.md:11-19`). Impact : confusion pour quiconque suit ce second document. Correction : supprimer `readme (2).md` ou le renommer clairement comme archive (`ARCHIVE_readme.md`), et ne garder que `README.md` comme source de vérité.

10. **`scripts/check_setup.py` vérifie des chemins de dossiers obsolètes.** Preuve : `check_setup.py:50-52` teste l'existence de `backend/rag/document_parser`, `backend/rag/chunker`, `backend/rag/metadata_extractor` — alors que la structure réelle est `backend/app/rag/...` (confirmé dans l'arborescence §3). Impact : ce script affichera toujours ❌ pour ces dossiers même quand tout est correctement installé. Correction : mettre à jour les chemins vers `backend/app/rag/...`.

11. **`scripts/diagnostic.py` et `LICENSE` référencés dans `README.md`/`readme (2).md` mais absents du dépôt.** Preuve : `README.md` mentionne `python scripts/diagnostic.py` (section Développement) — fichier introuvable ; `readme (2).md:517` référence un fichier `LICENSE` — introuvable également. Impact : commandes de la documentation qui échoueront si exécutées. Correction : soit créer ces fichiers, soit retirer les références.

12. **`requirements.txt` contient des blocs dupliqués** (`qdrant-client`, `python-dotenv`, `langgraph` apparaissent deux fois avec des contraintes de version différentes — ex. `langgraph>=0.0.20` ligne 21 puis `langgraph>=0.2.0` ligne 26). Impact : aucun impact fonctionnel (pip prend la contrainte la plus stricte), mais nuit à la lisibilité et à la maintenance. Correction : dédupliquer et consolider en un seul bloc trié par domaine.

13. **`AgentConfig.llm_model` par défaut vaut `"gemini-1.5-pro"`** (`backend/app/agents/config.py:13`), alors que le LLM réellement utilisé dans le code est Ollama/`llama3.2:1b` (`ollama_client.py`, `main.py:87`). Ce champ de configuration ne semble jamais lu par le code réel (vérifié : aucun agent n'utilise `config.llm_model` pour choisir son moteur). Impact : configuration trompeuse, à nettoyer ou à documenter comme vestige d'une itération antérieure.

14. **Fichiers frontend redondants (code mort probable)** : `frontend/app.py` (Flask), `frontend/components/chat.py`, `frontend/utils/api_client.py` ne sont utilisés par aucun chemin de démarrage documenté (`run_frontend.sh`, `frontend/Dockerfile`, `README.md` pointent tous vers `frontend/gradio_app.py`). Impact : confusion pour la maintenance, dépendances (Flask) non déclarées. Correction : confirmer avec Binta s'ils doivent être supprimés ou conservés comme prototypes archivés.

15. **Volumes très lourds inclus dans le ZIP livré**, à ne pas commiter/redistribuer tels quels :
    - `venv/` (≈ 445 Mo, environnement Linux inutilisable sous Windows).
    - `model/` (≈ 1,3 Go, cache local Ollama du modèle `llama3.2:1b`, régénérable via `ollama pull llama3.2:1b`).
    Impact : gonfle inutilement la taille du livrable et complique le versioning. Correction : les exclure via `.gitignore` et les documenter comme régénérables (§13, README Ollama).

### Faible

16. **Aucun health check applicatif détaillé** au-delà d'un `{"status": "healthy"}` statique (`backend/app/api/routes/health.py:6-13`) — ne vérifie pas réellement l'état de Qdrant/Neo4j/Postgres/Ollama, contrairement à ce que suggère l'exemple de `HealthResponse` dans `responses.py:22-27` (`services: {"qdrant": "connected", ...}`). Amélioration possible : faire de vraies vérifications de connectivité dans `/health`.

17. **Pas d'outil de lint/format/type-check configuré** (pas de `ruff`, `black`, `mypy`, `flake8` dans `requirements.txt` ni de fichier de config associé). Amélioration possible pour un Sprint futur.

18. **Pas de CI/CD** : aucun dossier `.github/workflows`, `.gitlab-ci.yml` ou équivalent trouvé.

19. **Commentaires d'en-tête de fichier obsolètes** (chemins pré-refactor) dans plusieurs fichiers, ex. `backend/app/api/models/requests.py:2` commente `# backend/api/models/requests.py` (chemin réel : `backend/app/api/models/requests.py`). Cosmétique, sans impact fonctionnel.

### Information

20. Le dossier `data/raw/` contient un vrai corpus (~100 PDF, programme sénégalais Terminale S1/S2) et `data/processed/` contient déjà des rapports d'ingestion (2 exécutions datées du 2026-07-10) — preuve que le pipeline RAG a été testé avec des données réelles avant l'envoi du ZIP.
21. `nuru_student_memory.db` (SQLite, 98 Ko) existe déjà à la racine — preuve que Binta a fait tourner l'application en mode "sans PostgreSQL" au moins une fois en local. Ce fichier contient potentiellement des données de test (identifiants élève/enseignant de démonstration) — à examiner avant suppression ou partage.
22. Le dossier `cloudflared/` est présent mais vide de tout fichier exploitable trouvé lors de l'analyse (aucun binaire ni fichier de configuration `.yml` détecté à l'intérieur) — son usage exact (tunnel Cloudflare pour exposer l'API/le frontend publiquement) **n'est pas confirmé par un fichier de configuration dans le dépôt**.
23. `get-docker.sh` à la racine est le script d'installation officiel de Docker Engine (contenu identique au script public `get.docker.com`) — probablement un résidu d'installation de l'environnement de Binta, sans lien direct avec le code applicatif.

---

## 19. Recommandations classées par priorité

### Priorité 1 — Nécessaire pour lancer le projet
- Faire tourner (régénérer) les identifiants Qdrant/Neo4j actuellement exposés dans `.env` et `docker-compose.yml`, puis les remplacer par les nouveaux dans un `.env` non versionné.
- Créer un `.gitignore` (`.env`, `venv/`, `model/`, `__pycache__/`, `*.db`, `logs/`) avant tout premier `git init`/commit.
- Recréer un environnement virtuel **Windows** (`python -m venv venv_win`) et installer `requirements.txt` (§13) — le `venv/` Linux livré est inutilisable ici.
- Corriger l'incohérence de port `8000` vs `8080` dans `.env` (`API_URL`) et `scripts/test_api.py`.
- Résoudre les conflits de ports Docker confirmés (`5432`, `11434`) avant `docker compose up` — appliquer (après votre validation) le plan de remapping du §10.
- Clarifier/corriger la configuration Neo4j de `docker-compose.yml` (cloud vs conteneur local, point 2 du §18).

### Priorité 2 — Nécessaire pour stabiliser le développement
- Ajouter `flask` à `requirements.txt` ou supprimer `frontend/app.py`, `frontend/components/chat.py`, `frontend/utils/api_client.py` s'ils sont confirmés obsolètes.
- Supprimer ou archiver clairement `readme (2).md` pour ne garder qu'une seule source de vérité documentaire.
- Mettre à jour `scripts/check_setup.py` avec les vrais chemins (`backend/app/rag/...`).
- Créer un `.env.example` versionné (contenu proposé en §11).
- Créer `scripts/diagnostic.py` (ou retirer la référence du README) et un fichier `LICENSE` (ou retirer la référence).
- Dédupliquer `requirements.txt`.
- Restreindre le CORS (`allow_origins`) à une liste explicite d'origines plutôt que `"*"` couplé à `allow_credentials=True`.
- Ajouter une vérification d'authenticité (jeton) sur les routes `/teacher/*` avant toute exposition au-delà d'un usage local/démo.
- Documenter clairement, dans le README, que `venv/` et `model/` ne doivent pas être inclus dans les livraisons futures (taille, portabilité).

### Priorité 3 — Améliorations futures
- Ajouter Alembic (ou équivalent) pour des migrations de schéma versionnées plutôt que `create_all()`.
- Ajouter des health checks applicatifs réels (`/health` vérifiant Qdrant/Neo4j/Postgres/Ollama).
- Ajouter lint/type-check (ruff, mypy) et une CI (GitHub Actions ou équivalent).
- Remplacer le `SimpleSessionManager` en mémoire par Redis si un déploiement multi-instance est envisagé.
- Durcir l'authentification enseignant (jetons de session avec expiration, éventuellement bcrypt/passlib).
- Étudier l'intégration ou la suppression définitive de la piste Gemini (`GEMINI_API_KEY`), actuellement un placeholder sans code associé.

---

## 20. Commandes rapides de démarrage

Voir la section Quick Start ci-dessous (les valeurs de ports utilisées sont celles **actuellement dans le code**, sans aucune modification appliquée par cette analyse).

---

## 21. Sources et fichiers analysés

`docker-compose.yml`, `Dockerfile`, `frontend/Dockerfile`, `README.md`, `readme (2).md`, `CHANGELOG_UPDATE.md`, `requirements.txt`, `.env`, `run_api.sh`, `run_frontend.sh`, `run_all.sh`, `run_ingest.sh`, `run_tests.sh`, `scripts/init_env.sh`, `scripts/check_env.py`, `scripts/check_setup.py`, `scripts/ingest_config.py`, `backend/utils/env_loader.py`, `backend/app/api/main.py`, `backend/app/api/dependencies/containers.py`, `backend/app/api/routes/{chat,health,evaluation,teacher}.py`, `backend/app/api/models/{requests,responses}.py`, `backend/app/api/middleware/logging.py`, `backend/app/agents/{__init__,config,graph,orchestrator,planner,state}.py`, `backend/app/tools/{math_tools,sandbox}.py`, `backend/app/llm/ollama_client.py`, `backend/app/memory/{db,models,teacher_profile}.py`, `backend/app/rag/vector_indexer/{config,qdrant_client}.py`, `backend/app/rag/knowledge_graph/{config,neo4j_client}.py`, `backend/app/rag/document_parser/nougat_adapter.py`, `frontend/gradio_app.py`, `frontend/app.py`, `frontend/components/chat.py`, `frontend/utils/api_client.py`, structure complète des dossiers `data/`, `model/`, `venv/`, `tests/`, `backend/tests/`, `.pytest_cache/`.

Commandes système exécutées (lecture seule / non destructives) : `python -m py_compile` (tous les fichiers), `docker --version`, `docker compose version`, `docker compose config`, `Get-NetTCPConnection` (vérification de ports), `python -c "import ..."` (résolution de dépendances, sans installation).

---

## Quick Start (copier-coller)

**⚠️ À exécuter seulement après avoir traité les points de Priorité 1 (§19), en particulier la rotation des secrets Qdrant/Neo4j.**

### Sans Docker (PowerShell, Windows)

```powershell
Set-Location "c:\Users\dell\Documents\AI4SENSE\Develop\Binta\nuru_agent_nbn"

# Environnement virtuel Windows (le venv/ livré est Linux, inutilisable ici)
python -m venv venv_win
.\venv_win\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Variables d'environnement (après avoir mis à jour .env avec des secrets tournés)
Get-Content .env | Where-Object { $_ -match '=' -and $_ -notmatch '^#' } | ForEach-Object {
    $k,$v = $_ -split '=',2
    Set-Item -Path "Env:$k" -Value $v
}

# Terminal 1 : API (port 8080)
python -m backend.app.api.main

# Terminal 2 : Frontend (port 7860)
$env:API_URL = "http://localhost:8080"
python -m frontend.gradio_app
```
Ouvrir : `http://localhost:7860`

### Avec Docker Compose

```powershell
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:1b
docker compose ps
```
Ouvrir : `http://localhost:7860` (frontend), `http://localhost:8080/docs` (API)

**Rappel** : sur cette machine, `5432` et `11434` sont déjà occupés — cette commande échouera probablement à publier ces deux ports tant que le remapping proposé en §10 n'est pas validé et appliqué.
