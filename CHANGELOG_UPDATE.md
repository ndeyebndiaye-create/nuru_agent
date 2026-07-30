# CHANGELOG - Mise à jour NURU (Étapes 1 à 3)

Cette mise à jour corrige le bug bloquant identifié et implémente les 3 premières étapes
validées : **(1) StateGraph LangGraph réel**, **(2) Outils mathématiques + Agent Retriever**,
**(3) Agents Evaluation/Progression + mémoire élève PostgreSQL/SQLite**.

## 🐛 Bugs corrigés

- `backend/app/agents/orchestrator.py` : `PlannerAgent` était appelé sans être importé
  (`NameError` garanti au démarrage). `planner.py` était un fichier vide.
- `backend/app/api/dependencies/containers.py` : imports vers `backend.agents` /
  `backend.rag.*` (chemins inexistants) au lieu de `backend.app.agents` / `backend.app.rag.*` ;
  `get_session_manager()` utilisait `datetime` sans l'importer.
- `backend/app/api/routes/chat.py` : la route `/chat` ne faisait que renvoyer un écho, sans
  jamais appeler l'orchestrateur ni les agents.
- `backend/app/api/main.py` : application FastAPI "de secours" (RAG+LLM direct) qui
  n'incluait aucun des routers `chat`/`health`, ni les agents LangGraph.
- `__init__.py` manquants sur plusieurs packages (`backend/app`, `backend/app/rag`,
  `backend/app/rag/knowledge_graph`, `backend/app/api/*`) : ajoutés pour un import fiable.

## 1️⃣ Vrai graphe LangGraph (StateGraph)

- `backend/app/agents/state.py` : ajout de `GraphState` (TypedDict), schéma d'état utilisé
  par LangGraph (conservé en plus de l'ancien `AgentState`, toujours utilisé par les agents
  historiques via un petit adaptateur).
- `backend/app/agents/planner.py` (était vide) : détection d'intention (cours / exercice /
  quiz / calcul), niveau d'aide façon Khanmigo (reformulation → rappel → indice →
  solution guidée → solution complète, avec escalade automatique si l'élève insiste),
  extraction de concept, détection de demande de calcul.
- `backend/app/agents/graph.py` (nouveau) : construit le graphe réel avec
  `langgraph.graph.StateGraph` :

  ```
  START -> planner -> retriever -> [math_tool ?] -> {cours | exercices | quiz}
        -> verifier -> progression -> END
  ```

  Le routage `cours/exercices/quiz` est conditionnel (`add_conditional_edges`), basé sur
  l'intention détectée par le Planner.
- `backend/app/agents/orchestrator.py` : réécrit en wrapper fin autour de `NuruGraph`, pour
  ne pas casser le code appelant existant (`containers.py`).
- `CoursAgent` / `ExercicesAgent` : génèrent maintenant leur contenu via le LLM local
  (Ollama) en s'appuyant sur le contexte RAG, avec repli sur les anciens gabarits texte si
  le LLM est indisponible (dégradation gracieuse, testée sans Ollama lancé).

## 2️⃣ Outils mathématiques (SymPy + sandbox) + Agent Retriever

- `backend/app/tools/math_tools.py` (nouveau) : dérivée, intégrale (primitive/définie),
  résolution d'équation, simplification, développement, factorisation, limite, étude de
  fonction — tous calculés exactement via SymPy (jamais par le LLM). Détection de demande
  de calcul + extraction de l'expression mathématique dans un message en langage naturel.
- `backend/app/tools/sandbox.py` (nouveau) : exécution de code Python restreint dans un
  **processus séparé avec timeout** (5s par défaut), builtins whitelistés, pas d'`import`
  arbitraire (seuls `math`/`numpy`/`matplotlib` sont injectés) → testé : bloque
  effectivement `import os; os.system(...)`. Fournit `plot_function()` pour tracer une
  fonction et retourner l'image en base64.
- `backend/app/agents/retriever_agent.py` (nouveau) : agent dédié qui interroge Qdrant
  (via `HybridRetriever`) et le Knowledge Graph (via `GraphQueries`), avec filtre
  classe/série et repli si aucun résultat filtré. Construit le bloc de contexte injecté
  dans le prompt LLM.

## 3️⃣ Agents Evaluation / Progression + mémoire élève (PostgreSQL/SQLite)

- `backend/app/memory/` (nouveau package) :
  - `db.py` : connexion SQLAlchemy, `DATABASE_URL` (PostgreSQL en prod) avec repli
    automatique sur SQLite local (`nuru_student_memory.db`) si non défini — pratique pour
    développer/tester sans dépendance externe.
  - `models.py` : `Student`, `Interaction`, `ExerciseResult`, `ConceptMastery`.
  - `student_profile.py` : CRUD + calcul de maîtrise par notion (moyenne mobile
    exponentielle à chaque nouvelle observation → mastery learning).
- `backend/app/agents/evaluation_agent.py` (nouveau) : corrige un quiz (QCM/vrai-faux) ou
  un exercice, calcule un score, identifie les erreurs répétées, génère des
  recommandations ; agrège aussi la performance d'une classe entière (pour l'espace
  enseignant à venir).
- `backend/app/agents/progression_agent.py` (nouveau) : enregistre chaque interaction et
  résultat, expose le profil de progression (carte de maîtrise, notions faibles), propose
  la prochaine étape pédagogique (réviser une notion faible ou avancer).
- Nouvelles routes API :
  - `GET /chat/progression/{user_id}` : profil de progression d'un élève.
  - `POST /evaluation/quiz` et `POST /evaluation/exercice` : corrigent et mettent à jour
    la mémoire de l'élève.
- `POST /chat` utilise maintenant un `student_id` interne (résolu depuis `user_id`),
  journalise chaque échange et renvoie un résumé de progression.

## ✅ Tests effectués (voir aussi `backend/tests` / `tests`)

Testé manuellement dans un environnement isolé (sans Qdrant/Neo4j/Ollama réels, pour
valider la dégradation gracieuse) :

- Planner : détection d'intention et de niveau, extraction de concept/expression.
- Outils SymPy : dérivée, résolution d'équation.
- Graphe LangGraph complet (`NuruGraph.invoke`) avec retriever/graph_queries mockés :
  routage correct vers cours / exercices / quiz / calcul.
- Sandbox : tracé de fonction (image générée), blocage effectif d'un `import os`.
- Mémoire élève (SQLite) : création de profil, enregistrement de résultats, calcul de
  maîtrise, notions faibles, suggestion de prochaine étape, correction de quiz.

## ⚠️ Ce qui reste à faire (hors périmètre de cette mise à jour)

- Espace Enseignant (génération pédagogique, gestion de classe, statistiques) — la base
  existe déjà côté `EvaluationAgent.summarize_class_performance()`, mais pas d'interface.
- Vraie recherche hybride BM25 (actuellement TF-IDF + cosinus en repli, comme avant cette
  mise à jour).
- Déploiement Hugging Face Spaces (phase 8 du cahier des charges).
- Le Planner reste basé sur des règles/mots-clés plutôt qu'un LLM avec sortie structurée :
  volontaire pour la rapidité et la fiabilité en local, mais à réévaluer si le modèle local
  choisi supporte bien le structured output.

## 🔧 Pour lancer avec la mémoire élève

```bash
# Local (SQLite automatique, rien à faire)
uvicorn backend.app.api.main:app --reload

# Production (PostgreSQL)
export DATABASE_URL="postgresql+psycopg://user:password@host:5432/nuru"
uvicorn backend.app.api.main:app
```
