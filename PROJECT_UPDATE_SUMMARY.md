# Synthèse de mise à jour du projet NURU

## 1. Objet de la phase

Cette phase avait pour objectif de stabiliser NURU sous Windows, de revoir
indépendamment les corrections déjà réalisées, puis d'aligner l'architecture sur la
décision suivante : le cas d'usage ne nécessite pas Neo4j et le RAG doit fonctionner
avec Qdrant comme unique base de recherche documentaire.

Le projet comprend actuellement :

- un backend FastAPI orchestrant les agents LangGraph ;
- un frontend Gradio ;
- Ollama pour la génération locale avec `llama3.2:1b` ;
- Qdrant pour l'index vectoriel et la récupération RAG ;
- PostgreSQL ou SQLite pour la mémoire élève ;
- Docker Compose pour les services d'infrastructure et les images applicatives.

## 2. Problèmes identifiés au départ

La revue initiale a mis en évidence plusieurs catégories de problèmes :

- dépendance runtime et ingestion à Neo4j alors que le graphe n'apportait pas de
  contexte exploitable au Retriever ;
- construction du Knowledge Graph lente, défaillante et accompagnée de statistiques
  pouvant compter des créations ayant échoué ;
- complexité inutile dans le conteneur de dépendances, l'orchestration, les prompts,
  Docker, les scripts d'installation et les variables d'environnement ;
- incohérence possible entre l'option déclarée correcte dans un quiz, l'explication
  générée et la réponse comparée lors de la soumission ;
- erreurs HTTP 400 de Qdrant lors des recherches filtrées par `classe` et `serie` ;
- lenteur notable des réponses utilisant Ollama et le RAG ;
- qualité pédagogique variable avec le petit modèle `llama3.2:1b` ;
- documentation de lancement partiellement obsolète ou trop optimiste sur le mode
  entièrement conteneurisé.

## 3. Architecture Qdrant-only obtenue

Le chemin RAG actif est désormais :

```text
Question utilisateur
  -> Planner
  -> Retriever Qdrant
  -> contexte documentaire vectoriel
  -> agent pédagogique concerné
  -> Verifier
  -> réponse
```

Le pipeline d'ingestion suit désormais uniquement :

```text
PDF -> parsing -> métadonnées -> chunking -> embeddings -> Qdrant -> rapport
```

Neo4j a été retiré :

- du Retriever et de l'état interne du graphe d'agents ;
- de `NuruGraph`, de l'Orchestrator et du conteneur de dépendances ;
- de la route Enseignant et de la carte de compétences ;
- des prompts et docstrings runtime concernés ;
- du pipeline d'ingestion et de ses statistiques ;
- du package Python, des scripts dédiés et de `requirements.txt` ;
- des variables `NEO4J_*` dans les fichiers d'environnement ;
- de Docker Compose, de ses ports, dépendances et volumes déclarés ;
- des scripts de vérification, d'installation et de lancement.

La carte de compétences repose maintenant uniquement sur la maîtrise enregistrée dans
la mémoire élève. Cette simplification correspond au comportement utile déjà observé :
l'ancien chemin Neo4j échouait et retombait sur cette mémoire.

## 4. Changements réalisés par zone

### Backend

- Retriever rendu exclusivement vectoriel avec conservation d'un repli non filtré.
- Suppression de la construction et de l'injection des composants de graphe Neo4j.
- Adaptation des états LangGraph et des composants orchestrateurs.
- Adaptation de la génération Enseignant et de la carte de compétences.
- Nettoyage des références runtime Neo4j dans les prompts et docstrings concernés.

### Ingestion

- Suppression des imports et de l'initialisation du Knowledge Graph.
- Suppression de l'étape de construction du graphe et de la méthode associée.
- Suppression de `graph_nodes` et `graph_relations` des nouveaux rapports.
- Conservation du parsing, des métadonnées, du chunking, des embeddings, de
  l'indexation Qdrant et du rapport final.

### Dépendances, environnement et scripts

- Suppression de la dépendance Python `neo4j`.
- Suppression des variables `NEO4J_*` de `.env.example` et de l'environnement local.
- Nettoyage des scripts `check_env.py`, `check_setup.py`, `init_env.sh`,
  `setup_windows.ps1` et `run_backend_windows.ps1`.
- Suppression du package `backend/app/rag/knowledge_graph/` et du script de test dédié.

### Docker

- Suppression du service Neo4j, des ports 7474/7687 et du volume associé.
- Suppression des variables Neo4j du backend et de sa dépendance Compose.
- Stack déclarée restante : PostgreSQL, Qdrant, backend et frontend ; Ollama est
  disponible via un profil optionnel.

### Quiz

Le flux complet a été rendu cohérent entre les deux requêtes partageant le même
`session_id` :

- la question générée est normalisée avant stockage ;
- l'option correcte stockée devient la référence unique ;
- l'explication est alignée sur cette option ;
- la réponse de l'élève est comparée à la même valeur canonique ;
- l'état de session conserve la même question entre génération et soumission.

Cette correction garantit la cohérence interne du QCM. Elle ne garantit pas à elle
seule la vérité mathématique du contenu produit par le LLM.

### Filtres Qdrant

L'analyse de la collection existante a confirmé que `classe` et `serie` sont des
chaînes dans les payloads. Les erreurs HTTP 400 provenaient de l'absence d'index
payload requis pour les filtres `keyword`.

La correction a consisté à :

- construire les filtres avec les champs et types réels ;
- créer de manière idempotente les index `keyword` manquants sur `classe` et `serie` ;
- préserver la collection et ses 2 635 points ;
- conserver le repli vers une recherche non filtrée en cas d'erreur ou de zéro
  résultat filtré.

## 5. Validations réalisées

Les validations ont été effectuées avec `venv_win`, sans réingestion complète et sans
recréation de collection.

### Vérifications ciblées

- tests Quiz : **18 réussis**, avec 8 avertissements de dépréciation Pydantic ;
- tests Qdrant : **6 réussis** ;
- vérification réelle des filtres `classe`, `serie` et combinés : aucune erreur HTTP
  400 après création des index ;
- nombre de points Qdrant avant et après l'opération : **2 635**, inchangé ;
- syntaxe Python, imports backend et configuration Compose validés au fil des phases.

### Suite complète

Résultat final de `pytest tests/` :

- **78 tests réussis** ;
- **1 test ignoré** ;
- **8 avertissements**, liés à l'ancienne forme `class Config` de Pydantic et non au
  retrait de Neo4j.

### Validation fonctionnelle minimale

- endpoint `/health` accessible avec statut HTTP 200 ;
- question RAG filtrée par `classe` et `serie` traitée sans HTTP 400 Qdrant ;
- quiz généré puis soumis avec le même `session_id` ;
- correction alignée sur l'option correcte stockée ;
- aucune erreur Neo4j, aucun HTTP 500 et aucun traceback bloquant relevé dans les logs
  de validation.

Les données temporaires de l'utilisateur de validation ont été retirées de manière
ciblée de la mémoire locale après les tests.

## 6. État de lancement sous Windows

Le mode recommandé et validé pour la démonstration est :

```text
PostgreSQL et Qdrant dans Docker
Ollama natif
backend FastAPI dans venv_win
frontend Gradio dans venv_win
```

Les scripts `scripts/run_backend_windows.ps1` et
`scripts/run_frontend_windows.ps1` ciblent les bons modules et ports. La syntaxe de ces
scripts et de `scripts/setup_windows.ps1` a été vérifiée statiquement. La configuration
Compose est valide et déclare `postgres`, `qdrant`, `backend` et `frontend`.

L'audit final a retiré du `Dockerfile` l'instruction obsolète qui copiait un dossier
racine `config/` absent. La configuration Compose est valide, mais le build complet
n'a pas été exécuté. Le mode hybride reste recommandé pour la démonstration, notamment
parce que le Qdrant local peut ne pas contenir les données validées sur Qdrant Cloud.

## 7. Réserves restantes

- `llama3.2:1b` peut produire des formulations faibles, du contenu mathématique erroné
  ou des QCM peu naturels malgré la cohérence technique désormais garantie.
- La génération RAG observée peut être lente, de l'ordre de plusieurs dizaines de
  secondes selon la machine et la charge Ollama.
- Aucune réingestion complète n'a été relancée pendant les corrections ; les problèmes
  déjà relevés autour des chunks longs, checkpoints et UUID restent hors périmètre.
- Les valeurs de `serie` présentes dans la collection ne sont pas entièrement
  normalisées (`S1`, `TS1`, variantes de casse, etc.), ce qui peut réduire le rappel
  d'un filtre exact même si la requête est techniquement valide.
- PostgreSQL est disponible dans Compose, mais l'application peut utiliser SQLite si
  `DATABASE_URL` n'est pas configurée dans le mode natif.
- Le build Docker complet n'a pas été exécuté pendant l'audit final ; seule sa
  configuration statique a été vérifiée.
- Les anciens scripts, interfaces, caches et logs non nécessaires ont été déplacés de
  façon réversible dans `delete_file/`, avec leur inventaire dans son `README.md`.

Conclusion de remise : **PRÊT AVEC RÉSERVES**, principalement sur la qualité et les
performances du LLM, pas sur le retrait de Neo4j ni sur la cohérence technique des
filtres et du quiz.

## 8. Recommandations pour les évolutions futures

1. Évaluer un modèle plus robuste et mesurer qualité, latence et ressources sur un jeu
   fixe de questions pédagogiques.
2. Ajouter une validation mathématique structurée des quiz avant présentation à
   l'élève, au-delà de la seule cohérence interne.
3. Normaliser les métadonnées `classe` et `serie` à l'ingestion et prévoir une migration
   contrôlée des payloads existants.
4. Optimiser séparément le chunking, les checkpoints, les UUID et les embeddings, puis
   mesurer une ingestion complète sur un échantillon reproductible.
5. Ajouter des métriques de latence par étape : retrieval, prompt, génération et
   vérification.
6. Tester réellement le build Docker complet avant de le présenter comme mode de
   déploiement principal.
7. Migrer les modèles Pydantic concernés vers `ConfigDict` pour supprimer les
   avertissements de dépréciation.
8. Conserver les rapports Sprint 2, la revue initiale et le plan de retrait Neo4j comme
   archives historiques ; utiliser ce document et les guides actifs pour l'état actuel.
