# 🌟 NURU — Guide complet d'exécution (étape par étape)

Tuteur IA multi-agents (LangGraph) pour les Mathématiques Terminale S1, programme sénégalais.

Ce guide part de zéro (dossier dézippé) jusqu'à l'interface web fonctionnelle, en local
puis en déploiement (Docker / Hugging Face Spaces). Exécute les étapes **dans l'ordre**,
sans en sauter — chaque étape vérifie que la précédente a fonctionné.

> ⚠️ **Si tu vois le message "🤖 NURU (Mode hors-ligne)"** dans l'interface (écran jaune),
> ça veut dire que le frontend Gradio n'arrive pas à joindre l'API FastAPI. Va directement
> à la section [🩺 Dépannage : Mode hors-ligne](#-dépannage--mode-hors-ligne) après avoir
> lu les étapes 0 à 5.

---

## 📋 Sommaire

- [Étape 0 — Prérequis](#étape-0--prérequis)
- [Étape 1 — Installation](#étape-1--installation)
- [Étape 2 — Configuration (.env)](#étape-2--configuration-env)
- [Étape 3 — Lancer les bases de données (Qdrant, Postgres)](#étape-3--lancer-les-bases-de-données)
- [Étape 4 — Lancer le LLM local (Ollama)](#étape-4--lancer-le-llm-local-ollama)
- [Étape 5 — Pipeline d'ingestion documentaire](#étape-5--pipeline-dingestion-documentaire)
- [Étape 6 — Lancer l'API (agents LangGraph)](#étape-6--lancer-lapi-agents-langgraph)
- [Étape 7 — Lancer l'interface (frontend)](#étape-7--lancer-linterface-frontend)
- [Étape 8 — Tester le système de bout en bout](#étape-8--tester-le-système-de-bout-en-bout)
- [Étape 9 — Déploiement (Docker)](#étape-9--déploiement-docker)
- [Étape 10 — Déploiement (Hugging Face Spaces)](#étape-10--déploiement-hugging-face-spaces)
- [🩺 Dépannage : Mode hors-ligne](#-dépannage--mode-hors-ligne)
- [Structure du projet](#structure-du-projet)

---

## Étape 0 — Prérequis

À installer avant de commencer :

| Outil | Version | Vérifier avec |
|---|---|---|
| Python | 3.10+ | `python3 --version` |
| pip | récent | `pip --version` |
| Docker (recommandé) | récent | `docker --version` |
| Ollama (LLM local) | dernière | `ollama --version` |
| Git | — | `git --version` |

Si tu n'as pas Docker, tu peux quand même tout lancer en local (les sections l'indiquent),
mais Docker simplifie énormément Qdrant/Postgres.

---

## Étape 1 — Installation

```bash
# 1. Se placer dans le dossier du projet (celui qui contient requirements.txt)
cd NURU

# 2. Créer un environnement virtuel Python
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

**Vérification :**
```bash
python -c "import langgraph, sympy, sqlalchemy, fastapi; print('✅ Dépendances OK')"
```
Si ça affiche `✅ Dépendances OK` sans erreur, passe à l'étape suivante.

---

## Étape 2 — Configuration (.env)

```bash
bash scripts/init_env.sh
```

Ça crée un fichier `.env` à la racine. Édite-le et renseigne :

```bash
# Qdrant (base vectorielle RAG)
QDRANT_URL=http://localhost:6333        # ou ton URL Qdrant Cloud
QDRANT_API_KEY=                         # vide si Qdrant local
QDRANT_COLLECTION=nuru_maths

# Mémoire élève (PostgreSQL) — laisse vide pour utiliser SQLite automatiquement
DATABASE_URL=

# LLM local (Ollama)
OLLAMA_MODEL=llama3.2:1b

LOG_LEVEL=INFO
DEBUG=True
ENVIRONMENT=development
```

**Vérification :**
```bash
python scripts/check_env.py
```
Toutes les variables obligatoires Qdrant doivent afficher ✅. `DATABASE_URL` peut
rester vide (repli SQLite automatique).

---

## Étape 3 — Lancer les bases de données

### Option A — Avec Docker (recommandé, le plus simple)

```bash
docker compose up -d qdrant postgres
```

Vérifie que tout tourne :
```bash
docker compose ps
```
Tu dois voir `qdrant` et `postgres` avec le statut `Up`.

- Qdrant : http://localhost:6333/dashboard

### Option B — Sans Docker

- Qdrant : `pip install qdrant-client` puis lance le binaire Qdrant localement, ou utilise
  un cluster **Qdrant Cloud** gratuit et mets son URL/clé dans `.env`.
- PostgreSQL : optionnel — si tu ne le configures pas, la mémoire élève utilise
  automatiquement un fichier SQLite local (`nuru_student_memory.db`), rien à faire.

**Vérification :**
```bash
curl http://localhost:6333/collections     # doit répondre en JSON, pas une erreur de connexion
```

---

## Étape 4 — Lancer le LLM local (Ollama)

```bash
# Terminal séparé, à garder ouvert
ollama serve
```

Dans un autre terminal, télécharge le modèle utilisé par NURU :
```bash
ollama pull llama3.2:1b
```

**Vérification :**
```bash
curl http://localhost:11434/api/tags        # doit lister llama3.2:1b
```

> 💡 Si Ollama n'est pas lancé, NURU continue de fonctionner en mode dégradé (les agents
> Cours/Exercices utilisent alors des gabarits texte au lieu du LLM), mais sans génération
> pédagogique riche. Pour la démo/soutenance, Ollama doit tourner.

---

## Étape 5 — Pipeline d'ingestion documentaire

Place tes PDF (cours, exercices, annales) dans `data/raw/cours/` et `data/raw/exercices/`,
puis lance le pipeline complet (extraction → nettoyage → chunking → embeddings → Qdrant) :

```bash
bash run_ingest.sh
```

Ce script :
1. Vérifie que des PDF existent dans `data/raw/`.
2. Exécute `python -m scripts.ingest_pipeline`.

**Options utiles :**
```bash
python -m scripts.ingest_pipeline --help            # affiche les options disponibles
python -m scripts.ingest_pipeline --limit 1         # limite le traitement à un fichier
python -m scripts.ingest_pipeline --force           # réingère même les fichiers déjà traités
```

**Vérification :**
```bash
python scripts/test_vector_indexer.py   # confirme que Qdrant contient des documents
```

---

## Étape 6 — Lancer l'API (agents LangGraph)

```bash
bash run_api.sh
```

Ou directement :
```bash
python -m backend.app.api.main
```

**Ce que tu dois voir dans le terminal :**
```
================================================================================
🚀 NURU - Agent Tuteur IA (LangGraph multi-agents)
================================================================================
📍 API: http://localhost:8080
📚 Docs: http://localhost:8080/docs
================================================================================
```

**Vérification (dans un autre terminal) :**
```bash
curl http://localhost:8080/health
# {"status": "healthy", ...}

curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Explique-moi les nombres complexes"}'
```

Tu dois recevoir un JSON avec une clé `"response"` contenant une explication (pas un
message d'erreur). Ouvre aussi http://localhost:8080/docs pour explorer toutes les
routes (Swagger UI généré automatiquement par FastAPI).

**Ne passe pas à l'étape 7 tant que cette étape n'est pas verte.** C'est la cause la plus
fréquente du "Mode hors-ligne" à l'écran.

---

## Étape 7 — Lancer l'interface (frontend)

Dans un **nouveau terminal** (laisse l'API tourner dans l'autre) :

```bash
source venv/bin/activate     # si pas déjà actif dans ce terminal
bash run_frontend.sh
```

Ou directement :
```bash
export API_URL=http://localhost:8080   # doit correspondre au port de l'étape 6
python -m frontend.gradio_app
```

**Ce que tu dois voir :**
```
🚀 NURU - Interface Finale
📍 http://localhost:7860 (onglets Espace Élève / Espace Enseignant intégrés)
```

Ouvre **http://localhost:7860** dans ton navigateur (deux onglets : 🎓 Espace Élève et 👩🏾‍🏫 Espace Enseignant).

### Ou lancer API + frontend ensemble en une commande

```bash
bash run_all.sh
```
(lance l'API en arrière-plan, attend qu'elle réponde, puis lance le frontend — logs dans
`logs/api.log` et `logs/frontend.log`)

---

## Étape 8 — Tester le système de bout en bout

Dans l'onglet 🎓 Espace Élève (http://localhost:7860), essaie dans l'ordre :

1. **Cours** : *"Explique-moi la dérivabilité"* → doit renvoyer une explication (pas le
   message jaune "Mode hors-ligne").
2. **Exercice** : *"Génère-moi un exercice sur la dérivabilité"* → doit renvoyer un énoncé.
3. **Quiz** : *"Crée-moi un quiz sur les suites numériques"* → doit renvoyer des questions.
4. **Calcul** : *"Dérive la fonction x^2 + 3x"* → doit renvoyer `2x + 3` calculé par SymPy
   (visible dans la réponse ou dans `math_tool_result` si tu regardes `/docs`).

Tu peux aussi lancer la suite de tests automatisés :
```bash
bash run_tests.sh
```

---

## Étape 9 — Déploiement (Docker)

Le fichier Compose déclare Qdrant, PostgreSQL, le backend et le frontend. L'instruction
obsolète qui copiait un dossier racine `config/` absent a été retirée du `Dockerfile`.
Le build complet n'a toutefois pas été exécuté pendant l'audit final, et le Qdrant local
peut être vide si les données validées se trouvent sur Qdrant Cloud. Pour la
démonstration Windows, utilise de préférence le mode hybride décrit dans
`COMMANDES_LANCEMENT_WINDOWS.md`.

Commande déclarative du stack par défaut :

```bash
docker compose up -d --build
```

Cette commande vise `qdrant`, `postgres`, `backend` (API sur le port 8080) et
`frontend` (interface Gradio sur le port 7860). Ollama ne démarre pas par défaut : le
service est placé derrière le profil `ollama-docker`.

Pour utiliser explicitement Ollama en conteneur, active son profil puis télécharge le
modèle une seule fois :
```bash
docker compose --profile ollama-docker up -d ollama
docker compose exec ollama ollama pull llama3.2:1b
```

**Vérification :**
```bash
docker compose ps                          # tous les services "Up"
curl http://localhost:8080/health           # API
curl http://localhost:7860                  # Frontend (doit répondre en HTML)
```

Ouvre http://localhost:7860 — c'est le même comportement qu'en local, mais tout
tourne dans des conteneurs isolés, prêt à être poussé sur un serveur (VPS, etc.).

**Pour arrêter :**
```bash
docker compose down          # arrête tout
docker compose down -v       # arrête tout ET supprime les données (Qdrant/Postgres)
```

---

## Étape 10 — Déploiement (Hugging Face Spaces)

Pour une démo publique rapide (soutenance, portfolio), déploie l'API sur un Space Docker :

1. Crée un compte sur https://huggingface.co puis un nouveau Space :
   **New Space → Docker → nom "nuru-api"**.
2. Pousse le code du dossier `backend/` + `Dockerfile` + `requirements.txt` sur ce Space
   (via `git push`, comme un dépôt Git classique) :

   ```bash
   git remote add hf https://huggingface.co/spaces/<ton-compte>/nuru-api
   git push hf main
   ```

3. Dans **Settings → Variables and secrets** du Space, ajoute les mêmes variables que ton
   `.env` (QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, OLLAMA_MODEL...).

   > ⚠️ Ollama en local ne fonctionne pas sur HF Spaces gratuit (pas de modèle lourd
   > persistant facilement). Deux options :
   > - Utiliser un Space payant avec GPU + Ollama installé dans le Dockerfile.
   > - Remplacer temporairement le LLM local par une API compatible OpenAI hébergée
   >   (ex: un endpoint Hugging Face Inference), en adaptant `backend/app/llm/ollama_client.py`.

4. HF Spaces construit automatiquement l'image à partir du `Dockerfile` (le `PORT` est géré
   automatiquement, `main.py` lit déjà `os.getenv("PORT", 8080)`).

5. Fais de même pour l'interface (`frontend/`) dans un second Space Docker
   ("nuru-frontend"), avec la variable `API_URL` pointant vers l'URL publique du premier
   Space (ex: `https://<ton-compte>-nuru-api.hf.space`).

**Vérification :** ouvre l'URL publique du Space frontend (`https://<ton-compte>-nuru-frontend.hf.space/eleve`).

---

## 🩺 Dépannage : Mode hors-ligne

Si l'interface affiche l'encadré jaune **"🤖 NURU (Mode hors-ligne)"**, c'est que la requête
`POST {API_URL}/chat/` a échoué (timeout, connexion refusée, ou erreur 500). Vérifie dans
l'ordre :

1. **L'API tourne-t-elle vraiment ?**
   ```bash
   curl http://localhost:8080/health
   ```
   Si ça ne répond pas → retourne à l'**Étape 6**, regarde le terminal de l'API pour
   l'erreur exacte (souvent : Qdrant injoignable au démarrage — c'est normal, l'API
   dégrade gracieusement, mais vérifie qu'il n'y a pas de `Traceback` bloquant).

2. **`API_URL` du frontend pointe-t-il vers le bon port ?**
   Le frontend lit la variable d'environnement `API_URL` (défaut `http://localhost:8080`).
   Si ton API tourne sur un autre port, relance le frontend avec :
   ```bash
   export API_URL=http://localhost:8080
   python -m frontend.gradio_app
   ```

3. **Utilises-tu bien la version à jour du code ?**
   Si le message d'erreur affiché mentionne `backend/app/api/main_local.py` (chemin qui
   n'existe pas dans cette version), c'est que tu exécutes une **ancienne copie** du
   projet. Utilise le zip mis à jour (`NURU_updated.zip`) et relance depuis l'**Étape 1**
   avec un environnement virtuel propre :
   ```bash
   rm -rf venv
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Le format de la requête est-il correct ?**
   L'API attend un `POST /chat/` avec un corps JSON `{"message": "...", "session_id": "..."}`
   (et non plus des paramètres d'URL `?message=...`, format utilisé avant cette mise à jour).
   Teste directement :
   ```bash
   curl -X POST http://localhost:8080/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
   ```
   Si cette commande fonctionne mais pas l'interface, le problème vient du frontend
   (vérifie `frontend/gradio_app.py`, fonction `_post()`, doit envoyer `json=...`).

5. **Regarde les logs.**
   Si tu utilises `run_all.sh` :
   ```bash
   tail -50 logs/api.log
   tail -50 logs/frontend.log
   ```

---

## Structure du projet

```
NURU/
├── backend/app/
│   ├── agents/          # Planner, Retriever, Cours, Exercices, Quiz, Verifier,
│   │                     # Evaluation, Progression + graph.py (LangGraph StateGraph)
│   ├── tools/            # math_tools.py (SymPy), sandbox.py (exécution restreinte)
│   ├── memory/           # mémoire élève (SQLAlchemy, PostgreSQL/SQLite)
│   ├── rag/               # ingestion, chunking, vector_indexer (Qdrant)
│   ├── llm/               # client Ollama
│   └── api/                # FastAPI (routes chat/evaluation/health, containers.py = DI)
├── frontend/               # interface Gradio (gradio_app.py) — onglets Élève/Enseignant
├── data/raw/               # PDF sources (cours/, exercices/)
├── scripts/                # ingestion, tests, vérifications d'environnement
├── tests/                  # tests unitaires/intégration
├── run_api.sh / run_frontend.sh / run_all.sh / run_ingest.sh / run_tests.sh
├── Dockerfile              # image API
├── frontend/Dockerfile     # image interface
├── docker-compose.yml      # Qdrant, Postgres, API, frontend + profil Ollama optionnel
├── delete_file/            # quarantaine réversible des anciens artefacts
└── CHANGELOG_UPDATE.md      # détail des 3 dernières étapes implémentées (LangGraph, outils math, mémoire élève)
```

---

## 🆕 Mise à jour majeure : Gradio, Espace Enseignant, Badges, Nougat

Cette version ajoute :

- **Interface Gradio** (`frontend/gradio_app.py`) remplaçant le prototype Flask, avec deux
  onglets : 🎓 **Espace Élève** (Tableau de bord, Cours, Exercices, Quiz, Progression, Carte
  des compétences, Profil) et 👩🏾‍🏫 **Espace Enseignant** (connexion séparée, génération de
  cours, suivi des élèves liés, statistiques de classe).
- **Authentification enseignant** (`backend/app/memory/teacher_profile.py` +
  `POST /teacher/register`, `POST /teacher/login`, `POST /teacher/link-student`,
  `GET /teacher/{teacher_id}/students`) — mot de passe haché (jamais stocké en clair).
- **Badges** (gamification) — attribués automatiquement après chaque exercice/quiz
  (premier exercice, 10 exercices, 50 exercices, score parfait, notion maîtrisée), visibles
  dans l'onglet Profil.
- **Carte des compétences** — construite à partir de la maîtrise par notion
  (`ConceptMastery`) enregistrée dans la mémoire élève, affichée dans
  l'onglet dédié de l'Espace Élève.
- **Nougat OCR** (`backend/app/rag/document_parser/nougat_adapter.py`) — extraction
  prioritaire pour les PDF mathématiques (formules, LaTeX). **Optionnel** : si
  `nougat-ocr` n'est pas installé (paquet lourd, GPU recommandé), le pipeline retombe
  automatiquement sur PyMuPDF, sans planter.

> 💡 Pour activer réellement Nougat (extraction de formules), installe séparément :
> `pip install nougat-ocr torch` (idéalement avec un GPU — sur CPU, l'extraction est lente).
> Sans cette installation, le pipeline d'ingestion fonctionne quand même via PyMuPDF.

---

## Récapitulatif express (une fois tout configuré)

```bash
# Terminal 1
docker compose up -d qdrant postgres
ollama serve

# Terminal 2
source venv/bin/activate
bash run_ingest.sh          # une seule fois, ou quand tu ajoutes des PDF

# Terminal 3
bash run_all.sh              # lance API + interface

# Navigateur
http://localhost:7860
```
