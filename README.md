# 🌟 NURU — Tuteur IA pour les Mathématiques Terminale S1/S2

Tuteur pédagogique intelligent basé sur **LangGraph** (multi-agents), **RAG** (Qdrant Cloud),
**Gemini API** (LLM) et **Next.js 16** (interface web).

> Programme Mathématiques — Terminale S1/S2/S3, Sénégal.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Navigateur                                                  │
│  http://localhost:3000  (Next.js 16 + React 19 + Tailwind)  │
└──────────────────────┬───────────────────────────────────────┘
                       │  fetch / REST JSON
┌──────────────────────▼───────────────────────────────────────┐
│  Backend FastAPI  —  http://localhost:8080                   │
│                                                              │
│  LangGraph StateGraph                                        │
│  Planner → Retriever → Cours / Exercices / Quiz              │
│          → Verifier → Progression                            │
│                                                              │
│  Gemini API (google-generativeai)   ←   LLM                  │
│  Qdrant Cloud (qdrant-client)       ←   RAG (2 635 points)   │
│  SymPy                              ←   calcul symbolique    │
│  SQLite / PostgreSQL                ←   mémoire élève        │
└──────────────────────────────────────────────────────────────┘
```

### Stack

| Couche | Technologie | Version |
|---|---|---|
| Frontend | Next.js, React, TypeScript, TailwindCSS | 16 / 19 / 5 / 4 |
| Backend API | FastAPI, Uvicorn | ≥0.110 / ≥0.27 |
| Orchestration IA | LangGraph, LangChain Core | ≥0.2 / ≥0.3 |
| LLM | Google Gemini API (`gemini-1.5-pro`) | ≥0.4 |
| Base vectorielle | Qdrant Cloud | client==1.18.0 |
| Embeddings | sentence-transformers | ≥2.2 |
| Calcul symbolique | SymPy | ≥1.12 |
| Mémoire élève | SQLite (défaut) ou PostgreSQL | SQLAlchemy ≥2.0 |
| Parsing PDF | PyMuPDF | ≥1.23 |

---

## 📁 Structure du projet

```
nuru_agent_nbn/
│
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── graph.py              # LangGraph StateGraph (flux principal)
│       │   ├── orchestrator.py       # Point d'entrée des requêtes
│       │   ├── planner.py            # Détection d'intention (cours/quiz/exercice)
│       │   ├── retriever_agent.py    # Retrieval RAG sur Qdrant
│       │   ├── cours_agent.py        # Génération d'explications de cours
│       │   ├── exercices_agent.py    # Génération d'exercices
│       │   ├── quiz_agent.py         # Génération + correction de quiz QCM
│       │   ├── verifier_agent.py     # Vérification pédagogique des réponses
│       │   ├── evaluation_agent.py   # Scoring et analyse des résultats
│       │   ├── progression_agent.py  # Mise à jour de la maîtrise par notion
│       │   ├── llm_utils.py          # Singleton GeminiClient
│       │   ├── config.py             # Prompts système des agents
│       │   └── state.py              # Schéma d'état LangGraph (TypedDict)
│       │
│       ├── api/
│       │   ├── main.py               # Assemblage FastAPI + routers
│       │   ├── routes/
│       │   │   ├── chat.py           # /chat/  (LangGraph complet)
│       │   │   ├── generate.py       # /generate/content  /generate/chat  /generate/chapitres
│       │   │   ├── evaluation.py     # /evaluation/quiz  /evaluation/exercice
│       │   │   ├── health.py         # /health
│       │   │   ├── auth.py           # /auth/register  /auth/login
│       │   │   ├── student.py        # /student/dashboard/:id
│       │   │   ├── teacher.py        # /teacher/students/:id  /teacher/class-stats/:id
│       │   │   ├── parent.py         # /parent/students/:id
│       │   │   └── admin.py          # /admin/stats  /admin/users
│       │   ├── models/
│       │   │   ├── requests.py       # Schémas Pydantic des requêtes
│       │   │   └── responses.py      # Schémas Pydantic des réponses
│       │   └── dependencies/
│       │       └── containers.py     # Injection de dépendances (singletons)
│       │
│       ├── llm/
│       │   └── gemini_client.py      # Client Gemini API (temperature, system_prompt)
│       │
│       ├── memory/
│       │   ├── db.py                 # SQLAlchemy engine + session factory
│       │   ├── models.py             # ORM : users, students, interactions, mastery, badges
│       │   ├── student_profile.py    # CRUD profil élève
│       │   ├── teacher_profile.py    # CRUD profil enseignant
│       │   └── auth_service.py       # Authentification + gestion des rôles
│       │
│       ├── rag/
│       │   ├── document_parser/      # PDF → Markdown (PyMuPDF, Nougat optionnel)
│       │   ├── chunker/              # Découpage pédagogique des documents
│       │   ├── metadata_extractor/   # Extraction et enrichissement des métadonnées
│       │   └── vector_indexer/       # Embeddings + indexation Qdrant
│       │
│       └── tools/
│           ├── math_tools.py         # Calcul symbolique SymPy (dériver, intégrer, résoudre)
│           └── sandbox.py            # Évaluation sécurisée de code Python
│
├── frontend/
│   └── src/
│       ├── app/                      # Next.js App Router
│       │   ├── page.tsx              # Accueil
│       │   ├── layout.tsx            # Layout racine
│       │   ├── matieres/             # Catalogue des matières
│       │   │   └── mathematiques/    # Catalogue Maths Terminale
│       │   ├── cours/[id]/           # Lecteur de cours dynamique
│       │   ├── exercices/[id]/       # Exercices interactifs
│       │   ├── quiz/[id]/            # Quiz adaptatif
│       │   ├── progression/          # Tableau de bord élève (XP, maîtrise, badges)
│       │   ├── defis/                # Défis et challenges
│       │   ├── recherche/            # Recherche dans la base documentaire
│       │   ├── enseignant/           # Espace enseignant
│       │   ├── parent/               # Espace parent
│       │   └── admin/                # Back-office admin
│       │       ├── utilisateurs/
│       │       ├── publications/
│       │       ├── generation-ia/
│       │       ├── centre-ia/
│       │       ├── journal-audit/
│       │       └── scheduler/
│       │
│       ├── components/
│       │   ├── ai/
│       │   │   ├── Chatbot.tsx              # Chat IA (RAG + Gemini)
│       │   │   └── NuruAssistantDrawer.tsx  # Panel assistant latéral
│       │   ├── auth/
│       │   │   └── AuthModal.tsx            # Connexion / Inscription
│       │   ├── layout/
│       │   │   ├── Navbar.tsx
│       │   │   └── Sidebar.tsx
│       │   └── math/
│       │       ├── MathRenderer.tsx         # Rendu KaTeX inline
│       │       └── MarkdownViewer.tsx       # Markdown + KaTeX + GFM
│       │
│       ├── context/
│       │   └── AuthContext.tsx       # État d'authentification global
│       ├── lib/
│       │   └── api.ts                # Fonctions fetch vers le backend FastAPI
│       └── types/
│           └── index.ts              # Types TypeScript partagés
│
├── data/
│   ├── raw/
│   │   ├── cours/                    # 23 PDFs — Terminale S1/S2
│   │   └── exercices/                # TDs organisés par chapitre
│   └── processed/                   # Markdown extraits (générés par ingest)
│
├── scripts/
│   ├── init_env.sh                  # Crée .env depuis .env.example
│   ├── check_env.py                 # Vérifie les variables d'environnement
│   ├── check_setup.py               # Vérifie les imports Python
│   ├── ingest_pipeline.py           # Pipeline PDF → Qdrant (principal)
│   ├── ingest_config.py             # Configuration du pipeline
│   └── ingest_utils.py              # Utilitaires du pipeline
│
├── tests/                           # Suite pytest (78 tests)
├── logs/                            # api.log, frontend.log (générés au runtime)
│
├── run_api.sh                       # Lance le backend FastAPI
├── run_frontend.sh                  # Lance le frontend Next.js
├── run_all.sh                       # Lance API + Frontend ensemble
├── run_ingest.sh                    # Lance le pipeline d'ingestion
├── run_tests.sh                     # Lance la suite de tests
│
├── Dockerfile                       # Image Docker backend (python:3.11-slim)
├── frontend/Dockerfile              # Image Docker frontend (node:20-slim)
├── docker-compose.yml               # Qdrant, PostgreSQL, backend, frontend
├── requirements.txt                 # Dépendances Python
└── .env                             # Variables d'environnement (non versionné)
```

---

## ⚙️ Prérequis

| Outil | Version minimale | Vérification |
|---|---|---|
| Python | 3.10+ | `python3 --version` |
| pip | récent | `pip --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Docker | récent | `docker --version` |
| Git | — | `git --version` |

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd nuru_agent_nbn
```

### 2. Environnement Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Vérification des imports :
```bash
python scripts/check_setup.py
```

### 3. Dépendances Node.js (frontend)

```bash
cd frontend
npm install
cd ..
```

---

## 🔧 Configuration

### Créer le fichier `.env`

```bash
cp .env .env.backup   # facultatif — sauvegarde l'existant
```

Édite `.env` à la racine avec tes valeurs :

```dotenv
# ─── Qdrant Cloud ─────────────────────────────────────────────
QDRANT_URL=https://<ton-cluster>.europe-west6-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=<ta-cle-qdrant>
QDRANT_COLLECTION=nuru_maths

# ─── Qdrant local via Docker (alternative) ────────────────────
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=
# QDRANT_COLLECTION=nuru_maths

# ─── LLM Gemini API ───────────────────────────────────────────
GEMINI_API_KEY=<ta-cle-gemini>       # https://aistudio.google.com/
LLM_MODEL=gemini-1.5-pro

# ─── Mémoire élève ────────────────────────────────────────────
DATABASE_URL=                        # vide = SQLite automatique

# ─── Backend ──────────────────────────────────────────────────
PORT=8080

# ─── Frontend ─────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8080

# ─── Général ──────────────────────────────────────────────────
LOG_LEVEL=INFO
DEBUG=True
ENVIRONMENT=development
```

Vérification :
```bash
python scripts/check_env.py
# QDRANT_URL, QDRANT_COLLECTION et GEMINI_API_KEY doivent afficher ✅
```

---

## 🗄️ Bases de données

### Option A — Qdrant Cloud (recommandé, déjà configuré)

La collection `nuru_maths` est déjà indexée avec **2 635 points**.
Il suffit de renseigner `QDRANT_URL` et `QDRANT_API_KEY` dans `.env`. Aucun service local à démarrer.

### Option B — Qdrant + PostgreSQL via Docker

```bash
docker compose up -d qdrant postgres
docker compose ps
```

Vérifications :
```bash
# Qdrant
curl http://localhost:6333/collections

# PostgreSQL
docker compose logs postgres | tail -5
```

> **SQLite** : si `DATABASE_URL` est vide dans `.env`, la mémoire élève
> utilise automatiquement `nuru_student_memory.db` à la racine — rien à faire.

---

## 📦 Pipeline d'ingestion documentaire

> À lancer uniquement si tu ajoutes de nouveaux PDFs ou si tu utilises Qdrant local vide.

Place tes PDFs dans `data/raw/cours/` et `data/raw/exercices/`, puis :

```bash
source venv/bin/activate
bash run_ingest.sh
```

Le pipeline exécute :
```
PDF → PyMuPDF (parsing) → nettoyage → chunking pédagogique
    → sentence-transformers (embeddings) → Qdrant (indexation)
```

Options :
```bash
# Tester sur 1 fichier
python -m scripts.ingest_pipeline --limit 1

# Forcer la réingestion de tous les fichiers
python -m scripts.ingest_pipeline --force

# Afficher toutes les options
python -m scripts.ingest_pipeline --help
```

Logs d'ingestion disponibles dans `data/ingestion_logs/pipeline.log`.

---

## ▶️ Lancer l'application

### Option 1 — Tout en une commande

```bash
source venv/bin/activate
bash run_all.sh
```

Ce script :
1. Tue les processus existants sur les ports 8080 et 3000
2. Lance le backend FastAPI en arrière-plan → `logs/api.log`
3. Lance le frontend Next.js en arrière-plan → `logs/frontend.log`

```
✅ NURU est en cours d'exécution !
🎨 Application Web : http://localhost:3000
📚 Swagger API    : http://localhost:8080/docs
```

### Option 2 — Terminaux séparés (recommandé en développement)

**Terminal 1 — Backend FastAPI :**
```bash
source venv/bin/activate
bash run_api.sh
```

Sortie attendue :
```
================================================================================
🚀 NURU - Agent Tuteur IA (LangGraph multi-agents)
================================================================================
📍 API    : http://localhost:8080
📚 Docs   : http://localhost:8080/docs
================================================================================
```

**Terminal 2 — Frontend Next.js :**
```bash
bash run_frontend.sh
```

Sortie attendue :
```
▲ Next.js 16.2.12
- Local:   http://localhost:3000
- Network: http://0.0.0.0:3000
```

---

## 🔍 Vérifications

### API backend
```bash
# Santé
curl http://localhost:8080/health

# Chat IA (RAG + Gemini)
curl -X POST http://localhost:8080/generate/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explique-moi la dérivabilité", "classe": "Terminale"}'

# Génération de cours
curl -X POST http://localhost:8080/generate/content \
  -H "Content-Type: application/json" \
  -d '{"classe": "Terminale", "serie": "S1", "chapitre": "Nombres complexes", "content_type": "cours"}'

# Génération de quiz
curl -X POST http://localhost:8080/generate/content \
  -H "Content-Type: application/json" \
  -d '{"classe": "Terminale", "chapitre": "Dérivabilité", "content_type": "quiz", "num_questions": 3}'

# Chapitres disponibles
curl http://localhost:8080/generate/chapitres
```

### Frontend
Ouvre **http://localhost:3000** et navigue vers :

| URL | Description |
|---|---|
| `/` | Page d'accueil |
| `/matieres/mathematiques` | Catalogue des chapitres Maths |
| `/cours/[id]` | Lecteur de cours (RAG + Gemini) |
| `/quiz/[id]` | Quiz adaptatif avec correction |
| `/exercices/[id]` | Exercices avec feedback IA |
| `/progression` | Tableau de bord élève (XP, badges, maîtrise) |
| `/enseignant` | Espace enseignant |
| `/parent` | Espace parent |
| `/admin` | Back-office administrateur |

### Swagger UI interactif
Disponible sur **http://localhost:8080/docs** — toutes les routes testables directement dans le navigateur.

---

## 📋 Routes API

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Santé de l'API |
| `POST` | `/generate/chat` | Chat IA (RAG + Gemini) |
| `POST` | `/generate/content` | Génère cours / exercices / quiz |
| `GET` | `/generate/chapitres` | Liste des chapitres indexés |
| `POST` | `/chat/` | Chat via LangGraph complet (multi-agents) |
| `GET` | `/chat/progression/:user_id` | Historique de progression |
| `GET` | `/chat/badges/:user_id` | Badges gamification |
| `GET` | `/chat/competency-map/:user_id` | Carte des compétences |
| `POST` | `/evaluation/quiz` | Correction et scoring de quiz |
| `POST` | `/evaluation/exercice` | Correction d'exercice |
| `POST` | `/auth/register` | Inscription (élève / enseignant / parent) |
| `POST` | `/auth/login` | Connexion |
| `GET` | `/student/dashboard/:id` | Tableau de bord élève |
| `GET` | `/teacher/students/:id` | Élèves d'un enseignant |
| `GET` | `/teacher/class-stats/:id` | Statistiques de classe |
| `GET` | `/parent/students/:id` | Élèves d'un parent |
| `GET` | `/admin/stats` | Statistiques globales |
| `GET` | `/admin/users` | Liste des utilisateurs |

---

## 🧪 Tests

```bash
source venv/bin/activate
bash run_tests.sh
```

Résultat attendu : **78 tests réussis**, 1 ignoré, quelques avertissements Pydantic (sans impact).

Tests disponibles dans `tests/` :

| Fichier | Couverture |
|---|---|
| `test_quiz_agent_unit.py` | Quiz Agent |
| `test_planner_unit.py` | Planner Agent |
| `test_math_tools_unit.py` | Outils SymPy |
| `test_qdrant_filters_unit.py` | Filtres Qdrant |
| `test_auth_and_roles.py` | Authentification et rôles |
| `test_integration.py` | Tests d'intégration |
| `test_chunker_unit.py` | Chunker pédagogique |
| `test_parser_unit.py` | Parser PDF |
| `test_metadata_unit.py` | Extracteur de métadonnées |
| `test_quiz_state_integration.py` | État de session quiz |

Tests de composants RAG (scripts isolés) :
```bash
python scripts/test_vector_indexer.py    # Vérifie Qdrant + 2 635 points
python scripts/test_chunker.py
python scripts/test_parser.py
```

---

## 🐳 Déploiement Docker

```bash
# Build et lancement de tous les services
docker compose up -d --build

# Vérification
docker compose ps
```

Services démarrés :

| Service | Image | Port | Notes |
|---|---|---|---|
| `qdrant` | `qdrant/qdrant:latest` | 6333 | Base vectorielle locale (si pas Qdrant Cloud) |
| `postgres` | `postgres:16` | 5433→5432 | Mémoire élève persistante |
| `backend` | Build depuis `Dockerfile` | 8080 | FastAPI + LangGraph |
| `frontend` | Build depuis `frontend/Dockerfile` | 3000 | Next.js |

> `GEMINI_API_KEY` est injecté automatiquement depuis ton `.env` dans le conteneur backend.

```bash
# Logs en temps réel
docker compose logs -f backend
docker compose logs -f frontend

# Arrêter sans perdre les données
docker compose down

# Arrêter ET supprimer les volumes (⚠️ efface les données Qdrant/Postgres)
docker compose down -v
```

---

## 🩺 Dépannage

### Le frontend affiche une erreur de connexion API

```bash
# 1. L'API tourne-t-elle ?
curl http://localhost:8080/health

# 2. Vérifier les logs
tail -50 logs/api.log

# 3. Relancer manuellement avec la bonne URL
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev --prefix frontend
```

### La génération IA ne répond pas

```bash
# Vérifier la clé Gemini
python scripts/check_env.py

# Tester directement
curl -X POST http://localhost:8080/generate/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "classe": "Terminale"}'
```

### Qdrant inaccessible

```bash
# Tester Qdrant Cloud
curl -H "api-key: $QDRANT_API_KEY" "$QDRANT_URL/collections"

# Ou Qdrant local Docker
curl http://localhost:6333/collections
```

### Erreur d'import Python

```bash
# Vérifier les modules installés
python scripts/check_setup.py

# Réinstaller si nécessaire
pip install -r requirements.txt
```

### Port déjà utilisé

```bash
# Libérer le port 8080
fuser -k 8080/tcp

# Libérer le port 3000
fuser -k 3000/tcp
```

---

## 🔐 Rôles utilisateurs

| Rôle | Accès |
|---|---|
| **élève** | Chat IA, cours, exercices, quiz, progression, badges, défis |
| **enseignant** | Tout élève + suivi des élèves liés, stats de classe, génération de cours |
| **parent** | Consultation du tableau de bord de l'enfant |
| **admin** | Back-office complet : utilisateurs, stats, logs, génération IA |

---

## 📊 État du projet

| Composant | Statut |
|---|---|
| Backend FastAPI + LangGraph | ✅ Fonctionnel |
| LLM Gemini API | ✅ Intégré |
| RAG Qdrant Cloud | ✅ 2 635 points indexés |
| Frontend Next.js 16 | ✅ En développement actif |
| Mémoire élève SQLite | ✅ Fonctionnel |
| PostgreSQL (optionnel) | ✅ Supporté via Docker |
| Suite de tests pytest | ✅ 78 tests validés |
| Docker Compose | ✅ Configuré |

---

## ⚡ Récapitulatif express

```bash
# 1. Installer les dépendances
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Configurer (remplir GEMINI_API_KEY dans .env)
python scripts/check_env.py

# 3. Lancer (tout-en-un)
bash run_all.sh

# Navigateur
# http://localhost:3000       → Application
# http://localhost:8080/docs  → Swagger API
```
