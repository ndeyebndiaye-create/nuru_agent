# Plan détaillé de retrait de Neo4j

## Statut du document

- **Nature** : plan d'exécution uniquement.
- **Décision d'architecture** : Neo4j n'est plus requis ; Qdrant devient l'unique base du RAG.
- **État au moment de la rédaction** : aucune modification fonctionnelle commencée.
- **Interdictions respectées pendant la préparation** : aucun test lancé, aucun service démarré ou arrêté, aucune ingestion relancée.
- **Condition de démarrage** : aucune phase ci-dessous ne doit être exécutée sans autorisation explicite.

## 1. Objectif et résultat cible

Le résultat cible est une architecture dans laquelle :

```text
PDF → parsing → métadonnées → chunking → embeddings → Qdrant
                                                     │
Gradio → FastAPI → Planner → Retriever Qdrant ───────┘
                         → agents pédagogiques → Ollama
                         → progression → SQLite/PostgreSQL
```

À la fin du retrait :

- le backend ne doit plus importer, initialiser ou contacter Neo4j ;
- le Retriever doit utiliser uniquement Qdrant ;
- l'ingestion doit se terminer immédiatement après l'indexation Qdrant et la génération du rapport ;
- les routes Cours, Exercices, Quiz, Enseignant et Progression doivent rester utilisables ;
- la carte de compétences doit reposer sur la mémoire élève, sans structure Neo4j ;
- Docker ne doit plus définir de service, volume, port ou dépendance Neo4j ;
- aucune variable `NEO4J_*` ne doit rester nécessaire ;
- le paquet Python `neo4j` ne doit plus être installé ;
- la documentation opérationnelle ne doit plus demander de lancer Neo4j.

## 2. Inventaire exact des fichiers concernés

### 2.1 Fichiers backend à modifier

1. `backend/app/agents/config.py`
2. `backend/app/agents/state.py`
3. `backend/app/agents/retriever_agent.py`
4. `backend/app/agents/graph.py`
5. `backend/app/agents/orchestrator.py`
6. `backend/app/agents/progression_agent.py`
7. `backend/app/api/dependencies/containers.py`
8. `backend/app/api/routes/chat.py`
9. `backend/app/api/routes/teacher.py`
10. `backend/app/api/main.py`
11. `backend/app/api/models/responses.py`

### 2.2 Fichiers backend à supprimer après découplage

Le dossier complet suivant devient inutile :

1. `backend/app/rag/knowledge_graph/__init__.py`
2. `backend/app/rag/knowledge_graph/config.py`
3. `backend/app/rag/knowledge_graph/models.py`
4. `backend/app/rag/knowledge_graph/neo4j_client.py`
5. `backend/app/rag/knowledge_graph/concept_extractor.py`
6. `backend/app/rag/knowledge_graph/graph_builder.py`
7. `backend/app/rag/knowledge_graph/graph_queries.py`

La suppression ne devra intervenir qu'après élimination de tous les imports et après validation statique du runtime et de l'ingestion.

### 2.3 Pipeline et scripts à modifier

1. `scripts/ingest_pipeline.py`
2. `scripts/check_env.py`
3. `scripts/check_setup.py`
4. `scripts/init_env.sh`
5. `scripts/setup_windows.ps1`
6. `scripts/run_backend_windows.ps1`

### 2.4 Script à supprimer

1. `scripts/test_knowledge_graph.py`

### 2.5 Configuration et dépendances à modifier

1. `requirements.txt`
2. `.env.example`
3. `.env` — fichier local ignoré par Git ; retrait manuel des clés Neo4j sans afficher ni journaliser leurs valeurs.
4. `docker-compose.yml`

### 2.6 Frontend à modifier

1. `frontend/gradio_app.py`

La modification est uniquement documentaire dans le docstring d'architecture : le frontend ne contacte jamais Neo4j directement.

### 2.7 Tests existants concernés

1. `scripts/test_knowledge_graph.py` — à supprimer.
2. Les tests qui construisent à l'avenir `RetrieverAgent`, `NuruGraph` ou `OrchestratorAgent` devront ne plus fournir `graph_queries`.
3. La suite existante `tests/` devra être relue après modification pour confirmer qu'aucun mock ou contrat `graph_context` ne subsiste.

L'inventaire statique actuel n'a trouvé aucune référence directe à Neo4j dans les fichiers `tests/test_*.py`. Cela ne dispense pas de vérifier les signatures modifiées lors de l'implémentation.

### 2.8 Nouveaux tests proposés

1. `tests/test_retriever_qdrant_only_unit.py`
2. `tests/test_containers_qdrant_only_unit.py`
3. `tests/test_ingest_pipeline_qdrant_only_unit.py`
4. `tests/test_competency_map_qdrant_only_unit.py`
5. `tests/test_no_neo4j_references.py`

### 2.9 Documents opérationnels à mettre à jour

1. `README.md`
2. `COMMANDES_LANCEMENT_WINDOWS.md`
3. `PROJECT_TODO.md`
4. `CHANGELOG_LOCAL.md`
5. `CODE_REVIEW_AFTER_CLAUDE.md`
6. `readme (2).md`

### 2.10 Documents historiques à annoter, sans réécrire l'historique

1. `CHANGELOG_UPDATE.md`
2. `SPRINT2_PROJECT_TECHNICAL_ANALYSIS.md`
3. `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md`
4. `SPRINT2_FUNCTIONAL_AND_PEDAGOGICAL_DIAGNOSTIC.md`
5. `SPRINT2_MANUAL_WINDOWS_SETUP_AND_TESTING.md`

Ces fichiers décrivent des états passés. Il est préférable d'ajouter un bandeau indiquant que les instructions Neo4j sont historiques et remplacées par l'architecture Qdrant-only, plutôt que de modifier rétroactivement les constats d'origine.

### 2.11 Artefacts à ne pas modifier

- `data/ingestion_logs/pipeline.log` ;
- `data/processed/reports/*.json` ;
- `data/processed/chunks/*.json` ;
- les PDF de `data/raw/` ;
- les données Qdrant déjà indexées ;
- `nuru_student_memory.db` ;
- le volume Docker Neo4j pendant toute la période de validation et de retour arrière.

## 3. Dépendances et configuration à retirer

### 3.1 Dépendance Python

Supprimer de `requirements.txt` :

```text
neo4j>=5.14.0
```

Ne pas exécuter immédiatement de désinstallation manuelle dans l'environnement actif. La validation correcte consiste d'abord à reconstruire ou synchroniser un environnement à partir du nouveau `requirements.txt`, puis à confirmer que le projet fonctionne sans le paquet.

### 3.2 Variables d'environnement

Retirer de `.env.example`, de `.env` et de tout script de génération ou validation :

```text
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
NEO4J_DATABASE
```

Supprimer également :

- les messages signalant ces variables comme obligatoires ;
- les valeurs de démonstration ;
- les commentaires relatifs à Aura, Bolt, au Browser Neo4j ou au mot de passe Neo4j.

Précaution : ne jamais copier la valeur actuelle de `NEO4J_PASSWORD` dans un changelog, un test, une sauvegarde versionnée ou une sortie de commande.

## 4. Éléments Docker à supprimer ou modifier

### 4.1 Service à retirer de `docker-compose.yml`

Supprimer intégralement le service :

```yaml
neo4j:
  image: neo4j:5
  environment: ...
  ports: ...
  volumes: ...
```

Cela retire également les ports :

- `7474` — Neo4j Browser ;
- `7687` — protocole Bolt.

### 4.2 Environnement du backend Docker

Retirer du service `backend` :

```yaml
NEO4J_URI: ...
NEO4J_USER: ...
NEO4J_PASSWORD: ...
NEO4J_DATABASE: ...
```

### 4.3 Dépendances Docker

Retirer `neo4j` de :

```yaml
backend:
  depends_on:
```

Le backend devra dépendre uniquement des composants réellement utilisés, notamment Qdrant et PostgreSQL selon le mode retenu.

### 4.4 Volume déclaré

Retirer de la section `volumes:` du fichier Compose :

```yaml
neo4j_data:
```

Important : retirer la déclaration du fichier Compose ne supprime normalement pas automatiquement le volume déjà créé. Pendant la période de validation, ne lancer aucune commande de suppression du volume.

### 4.5 Nettoyage physique différé

La suppression réelle du volume Neo4j devra constituer une opération séparée, optionnelle et destructive, exécutée uniquement :

1. après validation complète du backend Qdrant-only ;
2. après expiration de la période de retour arrière ;
3. après autorisation explicite ;
4. après identification exacte du nom du volume.

Ne pas utiliser `docker compose down -v`, car cette commande supprimerait aussi les volumes Qdrant et PostgreSQL.

## 5. Composants backend impactés

### 5.1 `RetrieverAgent`

État actuel :

- construit un `HybridRetriever` Qdrant ;
- construit aussi `GraphQueries` ;
- renvoie `documents`, `graph_context` et `has_context` ;
- ajoute les prérequis Neo4j au prompt.

État cible :

- constructeur limité à `config` et `retriever` ;
- suppression de `_graph_queries` ;
- suppression de `_get_graph_queries()` ;
- suppression des appels `get_concept_details()` et `get_prerequisites_chain()` ;
- `has_context` calculé uniquement avec `bool(documents)` ;
- suppression de l'ajout « Prérequis nécessaires » issu de Neo4j ;
- conservation de la recherche filtrée puis du repli sans filtre Qdrant.

Choix de compatibilité recommandé : retirer proprement `graph_context` du contrat interne plutôt que de garder un champ mort. Comme ce champ n'est pas exposé par la réponse HTTP publique actuelle, le risque externe est faible.

### 5.2 `GraphState`

Dans `backend/app/agents/state.py`, supprimer :

```python
graph_context: Dict[str, Any]
```

Conserver `retrieved_docs` et `prompt_context`.

### 5.3 `NuruGraph`

Dans `backend/app/agents/graph.py` :

- retirer le paramètre `graph_queries` du constructeur ;
- construire `RetrieverAgent` avec Qdrant seulement ;
- ne plus recopier `result["graph_context"]` dans l'état ;
- conserver le flux Planner → Retriever → outils/agent → Verifier → Progression.

### 5.4 `OrchestratorAgent`

Dans `backend/app/agents/orchestrator.py` :

- retirer le paramètre `graph_queries` ;
- adapter la construction de `NuruGraph` ;
- ne changer ni `process()` ni le contrat HTTP final.

### 5.5 Conteneur de dépendances

Dans `backend/app/api/dependencies/containers.py` :

- supprimer les imports `GraphQueries` et `KnowledgeGraphConfig` ;
- supprimer `_graph_queries` ;
- supprimer `get_graph_queries()` ;
- ne transmettre que `get_retriever()` à `OrchestratorAgent` ;
- conserver les singletons Qdrant, orchestrateur et gestionnaire de session.

Effet attendu : le démarrage du backend ne tentera plus de connexion Neo4j et ne dépendra plus d'un mot de passe Neo4j.

### 5.6 Route Enseignant

Dans `backend/app/api/routes/teacher.py` :

- ne plus importer `get_graph_queries` ;
- construire `RetrieverAgent` avec `get_retriever()` uniquement ;
- conserver la génération de cours basée sur Qdrant.

### 5.7 Carte de compétences

Dans `backend/app/agents/progression_agent.py` :

- retirer le paramètre `graph_queries` de `get_competency_map()` ;
- supprimer la lecture des chapitres/concepts Neo4j ;
- construire directement les nœuds depuis la maîtrise enregistrée en mémoire élève ;
- documenter que la carte représente les notions effectivement travaillées.

Dans `backend/app/api/routes/chat.py` :

- retirer l'import local de `get_graph_queries` ;
- appeler `get_competency_map(student_id)` ;
- remplacer la description « Knowledge Graph + maîtrise » par « maîtrise enregistrée de l'élève ».

Cette modification ne retire pas une fonction réellement opérationnelle : les méthodes Neo4j appelées actuellement par la carte de compétences n'existent pas et le code utilise déjà son repli mémoire.

### 5.8 Prompts et documentation interne

Dans `backend/app/agents/config.py` :

- retirer du prompt Retriever la récupération du Knowledge Graph ;
- remplacer par une exigence d'utiliser les documents Qdrant et leurs métadonnées.

Dans `backend/app/api/main.py` :

- retirer Neo4j du docstring du mode simple ;
- conserver la distinction entre API démarrée et composants prêts.

Dans `backend/app/api/models/responses.py` :

- supprimer `"neo4j": "connected"` de l'exemple de réponse de santé ;
- ne pas prétendre que Qdrant est connecté si l'endpoint `/health` ne réalise toujours pas de contrôle réel.

## 6. Pipeline d'ingestion impacté

### 6.1 Imports

Dans `scripts/ingest_pipeline.py`, supprimer :

```python
from backend.app.rag.knowledge_graph import GraphBuilder, KnowledgeGraphConfig
```

Adapter le commentaire du chargement `.env` pour ne mentionner que Qdrant et les autres variables réellement nécessaires.

### 6.2 Initialisation

Supprimer de `_init_components()` :

- `KnowledgeGraphConfig.from_env()` ;
- `GraphBuilder(...)` ;
- `self.graph_builder` ;
- le log « GraphBuilder initialisé ».

### 6.3 Exécution

Supprimer de `run()` :

- l'étape « Construire le Knowledge Graph » ;
- l'appel `self._build_knowledge_graph(all_chunks)`.

Après l'indexation Qdrant, le pipeline doit directement générer le rapport.

### 6.4 Méthode à supprimer

Supprimer intégralement :

```python
def _build_knowledge_graph(...)
```

### 6.5 Statistiques et rapport

Supprimer de `self.stats`, du JSON final et de l'affichage :

```text
graph_nodes
graph_relations
```

Ne pas modifier les anciens rapports déjà produits. Ils constituent des artefacts historiques, même si leurs statistiques Neo4j sont trompeuses.

### 6.6 Indépendance Qdrant à confirmer

Pendant cette phase, vérifier également statiquement que :

- `VectorIndexer` ne dépend d'aucun module `knowledge_graph` ;
- la collection ciblée utilise bien `qdrant_collection_name` ;
- aucune erreur Neo4j ne peut empêcher l'initialisation du pipeline ;
- l'échec de Qdrant reste visible et ne produit pas un faux rapport de succès.

La correction du chunking, des checkpoints ou des UUID n'appartient pas strictement au retrait Neo4j. Elle devra faire l'objet d'un changement séparé afin de limiter le périmètre et faciliter le retour arrière.

## 7. Stratégie de tests

Les commandes ci-dessous sont des vérifications futures. Elles ne doivent être exécutées qu'après autorisation.

### 7.1 Test à supprimer

Supprimer :

```text
scripts/test_knowledge_graph.py
```

### 7.2 Tests unitaires à ajouter

#### `tests/test_retriever_qdrant_only_unit.py`

Cas à couvrir :

1. le Retriever retourne les documents du mock Qdrant ;
2. aucun import ou constructeur Neo4j n'est nécessaire ;
3. `has_context=True` quand Qdrant retourne un document ;
4. `has_context=False` quand Qdrant retourne une liste vide ;
5. le prompt contient les extraits et sources Qdrant ;
6. le repli sans filtres reste fonctionnel ;
7. aucun champ ou texte de prérequis Neo4j ne subsiste.

#### `tests/test_containers_qdrant_only_unit.py`

Cas à couvrir :

1. `get_orchestrator()` se construit avec un Retriever Qdrant mocké ;
2. aucune variable `NEO4J_*` n'est requise ;
3. aucune tentative de connexion Bolt n'est déclenchée ;
4. le singleton de l'orchestrateur reste fonctionnel.

#### `tests/test_ingest_pipeline_qdrant_only_unit.py`

Cas à couvrir :

1. l'initialisation ne construit que parser, chunker, métadonnées et indexeur vectoriel ;
2. l'indexation Qdrant est appelée lorsque des chunks existent ;
3. aucune étape post-Qdrant de graphe n'est appelée ;
4. le rapport ne contient plus `graph_nodes` ni `graph_relations` ;
5. un échec Qdrant est correctement reflété dans les statistiques.

#### `tests/test_competency_map_qdrant_only_unit.py`

Cas à couvrir :

1. la carte retourne les concepts de maîtrise enregistrés ;
2. un élève sans historique reçoit `nodes=[]` ;
3. aucun objet `graph_queries` n'est nécessaire ;
4. les statuts `maitrise`, `en_cours`, `faible` et `non_commence` restent cohérents.

#### `tests/test_no_neo4j_references.py`

Test de garde empêchant une réintroduction involontaire dans les fichiers opérationnels :

- aucun import `neo4j` ;
- aucun import `backend.app.rag.knowledge_graph` ;
- aucune variable `NEO4J_*` dans les modèles de configuration ;
- aucun service `neo4j` dans Compose.

Les documents historiques devront être exclus de ce test, car ils doivent pouvoir conserver la trace de l'ancienne architecture.

### 7.3 Tests existants à adapter

- adapter toute construction de `RetrieverAgent(..., graph_queries=...)` si une référence apparaît pendant l'implémentation ;
- adapter toute construction de `NuruGraph` ou `OrchestratorAgent` avec `graph_queries` ;
- conserver les tests Planner, outils mathématiques, Quiz, API et mémoire élève ;
- ne supprimer aucun test Qdrant, chunker, parser ou métadonnées.

### 7.4 Ordre futur des validations

1. vérification statique des références ;
2. imports Python ciblés ;
3. tests unitaires Qdrant-only ;
4. tests existants des agents ;
5. suite complète `pytest tests/` ;
6. validation de la configuration Compose ;
7. seulement ensuite, validation manuelle du backend et du frontend ;
8. aucune réingestion n'est nécessaire pour valider le retrait de Neo4j.

## 8. Documents à mettre à jour

### 8.1 Documentation opérationnelle

#### `README.md`

- remplacer l'architecture Qdrant + Neo4j par Qdrant seul ;
- retirer les variables Neo4j ;
- retirer les instructions Neo4j Desktop/Aura ;
- retirer les ports 7474/7687 ;
- remplacer les commandes `docker compose up -d qdrant neo4j postgres` ;
- décrire l'ingestion comme terminant dans Qdrant ;
- retirer `scripts/test_knowledge_graph.py` de la procédure et de l'arborescence ;
- mettre à jour le dépannage.

#### `COMMANDES_LANCEMENT_WINDOWS.md`

- retirer Neo4j de toutes les commandes `up`, `start`, `stop` et `logs` ;
- retirer les avertissements sur le volume Neo4j ;
- conserver Qdrant, PostgreSQL et Ollama selon le mode d'exécution.

#### `PROJECT_TODO.md`

- conserver la tâche non cochée pendant l'implémentation ;
- la marquer terminée seulement après la suite complète de vérification ;
- ajouter les sous-tâches runtime, ingestion, Docker, tests et documentation si le format du fichier le permet.

#### `CHANGELOG_LOCAL.md`

- documenter précisément les fichiers modifiés et supprimés ;
- indiquer que Qdrant devient l'unique stockage RAG ;
- indiquer qu'aucune donnée Qdrant n'a été supprimée ni réingérée ;
- inclure les résultats réels des validations futures.

#### `CODE_REVIEW_AFTER_CLAUDE.md`

- ne pas réécrire le diagnostic ;
- ajouter éventuellement une note de statut indiquant la date à laquelle le plan a été exécuté et validé.

#### `readme (2).md`

Ce README est ancien et contradictoire. Option recommandée : le supprimer après confirmation qu'il n'est plus utilisé. Option conservatrice : ajouter un bandeau « document obsolète » et retirer ses instructions opérationnelles. Ne pas maintenir deux guides concurrents.

### 8.2 Documentation historique

Ajouter en tête des documents suivants un court bandeau daté :

```text
Note d'architecture : depuis [date], Neo4j a été retiré du runtime et de
l'ingestion. Les références Neo4j ci-dessous décrivent uniquement l'état
historique du Sprint 2. Consulter README.md et NEO4J_REMOVAL_PLAN.md pour
l'architecture actuelle.
```

Fichiers :

- `CHANGELOG_UPDATE.md` ;
- `SPRINT2_PROJECT_TECHNICAL_ANALYSIS.md` ;
- `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md` ;
- `SPRINT2_FUNCTIONAL_AND_PEDAGOGICAL_DIAGNOSTIC.md` ;
- `SPRINT2_MANUAL_WINDOWS_SETUP_AND_TESTING.md`.

## 9. Risques de régression

### 9.1 Carte de compétences moins complète

Risque : sans Neo4j, la carte n'affichera pas tous les chapitres non encore travaillés.

Impact réel actuel : faible, car l'intégration Neo4j est déjà non fonctionnelle et retombe sur la mémoire élève.

Réduction du risque : documenter que la carte montre les notions travaillées. Si une carte complète est nécessaire plus tard, utiliser une taxonomie JSON/YAML versionnée.

### 9.2 Changement de signatures internes

Risque : appels ou tests non détectés utilisant `graph_queries=`.

Réduction : modifier les signatures par couche, rechercher toutes les occurrences avant suppression du package, puis exécuter les imports et tests ciblés.

### 9.3 Rupture du démarrage backend

Risque : un import Neo4j résiduel empêche le démarrage une fois la dépendance supprimée.

Réduction : supprimer la dépendance seulement après le découplage du code et ajouter un test de garde sur les imports.

### 9.4 Rupture du pipeline d'ingestion

Risque : suppression incorrecte de l'étape 5, des statistiques ou d'un attribut `graph_builder`.

Réduction : test unitaire du pipeline Qdrant-only avec composants mockés ; validation du schéma du rapport.

### 9.5 Documentation incohérente

Risque : des commandes anciennes continuent de demander Neo4j.

Réduction : recherche globale finale sur `neo4j`, `knowledge_graph`, `graph_queries`, ports `7474` et `7687`, en distinguant documentation active et archives annotées.

### 9.6 Perte accidentelle de données Docker

Risque : utilisation de `docker compose down -v` ou suppression du mauvais volume.

Réduction : ne supprimer aucun volume pendant l'implémentation ; différer le nettoyage physique ; identifier explicitement le volume avant toute suppression.

### 9.7 Faux sentiment que Qdrant est validé

Risque : le retrait de Neo4j n'assure pas à lui seul la pertinence des résultats Qdrant.

Réduction : séparer la validation « absence de Neo4j » de la validation qualitative du RAG. Ne pas réingérer ; utiliser d'abord la collection existante lors des futurs tests autorisés.

### 9.8 Modification excessive du périmètre

Risque : corriger simultanément le chunking, les prompts, Docker et le modèle rendrait le diagnostic de régression difficile.

Réduction : limiter ce chantier au retrait Neo4j. Traiter les autres problèmes dans des changements distincts.

## 10. Phases d'exécution et ordre optimal

## Phase 0 — Préparation et point de retour arrière

### Objectif

Créer un état de référence récupérable avant toute modification.

### Actions futures

1. vérifier l'état du dépôt et les modifications locales ;
2. identifier les fichiers utilisateur non suivis à préserver ;
3. créer une branche ou un point de sauvegarde dédié ;
4. consigner le nom exact du volume Neo4j sans le modifier ;
5. consigner les commandes de démarrage actuellement utilisées ;
6. ne pas toucher aux données Qdrant ou SQLite.

### Vérifications après la phase

- le point de retour arrière est identifiable ;
- aucune donnée ou configuration sensible n'a été ajoutée à Git ;
- aucun service n'a été modifié ;
- la liste des fichiers concernés correspond à l'inventaire de ce document.

### Critère de passage

Un retour à l'état initial doit être possible fichier par fichier ou commit par commit.

## Phase 1 — Découplage du runtime backend

### Objectif

Faire fonctionner le code conversationnel sans importer ni construire Neo4j, tout en gardant temporairement le package et la dépendance installés.

### Actions futures

1. modifier `RetrieverAgent` pour Qdrant seul ;
2. retirer `graph_context` de `GraphState` et du graphe ;
3. retirer `graph_queries` de `NuruGraph` et `OrchestratorAgent` ;
4. supprimer `get_graph_queries()` du conteneur de dépendances ;
5. adapter la route Enseignant ;
6. adapter la carte de compétences et sa route ;
7. mettre à jour les prompts et docstrings backend ;
8. conserver encore `backend/app/rag/knowledge_graph/` et `neo4j` dans `requirements.txt` jusqu'à la validation de cette phase.

### Vérifications après la phase

- recherche statique : aucun import opérationnel de `GraphQueries` ou `KnowledgeGraphConfig` hors package historique ;
- les constructeurs n'acceptent plus `graph_queries` ;
- le Retriever mocké renvoie et formate des documents Qdrant ;
- la carte de compétences fonctionne avec la mémoire élève seule ;
- les routes publiques conservent leurs champs essentiels.

### Critère de passage

Le backend doit être constructible en tests unitaires sans variable Neo4j et sans tentative de connexion Bolt.

## Phase 2 — Découplage du pipeline d'ingestion

### Objectif

Transformer l'ingestion en pipeline Qdrant-only.

### Actions futures

1. supprimer les imports Knowledge Graph ;
2. supprimer l'initialisation de `GraphBuilder` ;
3. supprimer l'étape de construction du graphe ;
4. supprimer `_build_knowledge_graph()` ;
5. retirer les métriques Neo4j du rapport ;
6. adapter les messages de logs et commentaires ;
7. ajouter les tests unitaires du pipeline Qdrant-only.

### Vérifications après la phase

- l'instanciation du pipeline avec composants mockés ne crée aucun client Neo4j ;
- l'ordre est parsing → chunking → Qdrant → rapport ;
- les rapports nouveaux ne contiennent aucune métrique de graphe ;
- aucun ancien rapport ou chunk n'a été modifié ;
- aucune ingestion réelle n'est nécessaire à ce stade.

### Critère de passage

Le pipeline doit pouvoir exécuter son flux simulé complet avec Qdrant mocké et produire un rapport cohérent.

## Phase 3 — Tests de protection Qdrant-only

### Objectif

Verrouiller le nouveau contrat avant de supprimer physiquement le package Neo4j.

### Actions futures

1. ajouter les cinq fichiers de tests proposés ;
2. adapter les tests existants aux nouvelles signatures ;
3. supprimer `scripts/test_knowledge_graph.py` ;
4. exécuter d'abord les tests ciblés ;
5. exécuter ensuite la suite existante si les tests ciblés passent.

### Vérifications après la phase

- Retriever Qdrant-only validé ;
- conteneur de dépendances validé sans Neo4j ;
- ingestion simulée validée sans Neo4j ;
- carte de compétences validée sans Neo4j ;
- garde statique contre les imports Neo4j validée ;
- tests Planner, maths, Quiz et mémoire toujours passants.

### Critère de passage

Aucune régression connue dans les tests automatisés et aucune référence runtime Neo4j.

## Phase 4 — Retrait des dépendances et du package

### Objectif

Supprimer les éléments Python devenus réellement inaccessibles.

### Actions futures

1. supprimer `neo4j>=5.14.0` de `requirements.txt` ;
2. supprimer `backend/app/rag/knowledge_graph/` ;
3. retirer `neo4j` de la vérification d'imports Windows ;
4. retirer les variables Neo4j des scripts d'environnement ;
5. synchroniser un environnement propre à partir du nouveau fichier de dépendances ;
6. ne pas désinstaller manuellement au milieu de la phase avant validation du code.

### Vérifications après la phase

- recherche globale des imports `neo4j` et `knowledge_graph` dans le code opérationnel ;
- import des modules backend principaux dans un environnement sans paquet Neo4j ;
- tests ciblés puis suite complète ;
- absence de `ModuleNotFoundError` liée à Neo4j.

### Critère de passage

Le projet fonctionne dans un environnement où le paquet `neo4j` n'est pas installé.

## Phase 5 — Configuration et Docker

### Objectif

Retirer Neo4j de la configuration d'exécution et de l'infrastructure déclarée.

### Actions futures

1. nettoyer `.env.example` ;
2. nettoyer localement `.env` sans exposer ses valeurs ;
3. retirer le service Neo4j du Compose ;
4. retirer l'environnement Neo4j du backend ;
5. retirer `neo4j` de `depends_on` ;
6. retirer la déclaration `neo4j_data` du Compose ;
7. mettre à jour les scripts de vérification et de lancement ;
8. préserver physiquement le volume existant.

### Vérifications après la phase

- `docker compose config` valide le fichier ;
- la configuration résolue ne contient ni service Neo4j ni `NEO4J_*` ;
- les ports 7474/7687 ne sont plus déclarés par ce projet ;
- les commandes Windows ne demandent plus de lancer Neo4j ;
- le volume historique existe encore pour le retour arrière.

### Critère de passage

La stack déclarée contient uniquement les services réellement nécessaires.

## Phase 6 — Documentation

### Objectif

Éliminer les instructions opérationnelles contradictoires sans falsifier les rapports historiques.

### Actions futures

1. mettre à jour `README.md` ;
2. mettre à jour `COMMANDES_LANCEMENT_WINDOWS.md` ;
3. mettre à jour `PROJECT_TODO.md` ;
4. documenter les changements dans `CHANGELOG_LOCAL.md` ;
5. traiter `readme (2).md` comme document obsolète ;
6. ajouter un bandeau aux rapports historiques ;
7. ajouter éventuellement une note d'exécution au rapport de revue.

### Vérifications après la phase

- les commandes actives ne mentionnent plus Neo4j ;
- les documents historiques sont clairement identifiés comme historiques ;
- aucune clé ou valeur sensible n'apparaît ;
- les schémas d'architecture montrent Qdrant seul ;
- la liste des fichiers supprimés correspond à la réalité.

### Critère de passage

Un nouveau développeur peut installer et lancer le projet sans connaître ni configurer Neo4j.

## Phase 7 — Validation fonctionnelle finale

### Objectif

Confirmer que le retrait n'a pas dégradé les parcours applicatifs.

### Actions futures, uniquement après autorisation

1. vérifier les imports dans un environnement propre ;
2. exécuter les tests ciblés ;
3. exécuter la suite complète ;
4. valider `docker compose config` ;
5. lancer ultérieurement le backend et vérifier sa readiness ;
6. tester une question de cours utilisant Qdrant ;
7. tester un exercice ;
8. tester un quiz et sa réponse au second tour ;
9. tester la génération de cours Enseignant ;
10. tester la progression et la carte de compétences ;
11. confirmer qu'aucun log de connexion ou d'erreur Neo4j n'apparaît ;
12. ne pas relancer l'ingestion pour cette validation.

### Vérifications attendues

- backend démarré sans `NEO4J_*` ;
- Retriever retourne des documents Qdrant ;
- Cours et Exercices reçoivent un `prompt_context` ;
- Quiz continue de fonctionner selon son contrat actuel ;
- mémoire élève inchangée ;
- aucune connexion sur le port 7687 initiée par NURU ;
- aucune donnée Qdrant supprimée ou recréée.

### Critère de passage

Tous les parcours critiques fonctionnent, les tests sont passants et aucun composant Neo4j n'est chargé.

## Phase 8 — Clôture et nettoyage différé

### Objectif

Clore le chantier tout en conservant une fenêtre de retour arrière.

### Actions futures

1. marquer la tâche `PROJECT_TODO.md` comme terminée ;
2. finaliser `CHANGELOG_LOCAL.md` avec les résultats mesurés ;
3. conserver le volume Neo4j pendant une période définie ;
4. après cette période, demander une autorisation distincte avant sa suppression ;
5. ne jamais utiliser une commande globale supprimant également Qdrant ou PostgreSQL.

### Vérifications après la phase

- tous les changements sont regroupés en commits cohérents ;
- la stratégie de retour arrière est documentée ;
- le volume Neo4j n'est supprimé que si cela a été explicitement approuvé ;
- Qdrant et la mémoire élève sont intacts.

## 11. Vérifications récapitulatives après chaque étape

| Étape | Vérification statique | Vérification automatisée future | Vérification manuelle future |
|---|---|---|---|
| Runtime | aucun import ou paramètre `graph_queries` | Retriever, conteneur, agents | cours/exercice/quiz |
| Ingestion | aucun `GraphBuilder` | pipeline mocké Qdrant-only | aucune ingestion réelle requise |
| Dépendance | aucun import `neo4j` | imports dans environnement propre | démarrage backend |
| Docker | aucun service/port/env Neo4j | `docker compose config` | stack sans conteneur Neo4j |
| Progression | aucun appel de méthode GraphQueries | test carte mémoire seule | affichage carte |
| Documentation | aucune instruction active Neo4j | garde documentaire éventuelle | relecture Quick Start |
| Final | recherche globale maîtrisée | suite complète | parcours fonctionnels critiques |

Recherches statiques finales recommandées :

```powershell
rg -n -i "neo4j|knowledge_graph|graph_queries|graph_builder|7474|7687" backend frontend scripts tests requirements.txt docker-compose.yml .env.example README.md COMMANDES_LANCEMENT_WINDOWS.md
```

Les occurrences encore présentes devront être limitées aux documents historiques annotés, au plan de retrait et au changelog expliquant la suppression.

## 12. Stratégie de retour arrière

### 12.1 Principes

- un commit ou groupe de commits par phase ;
- ne jamais mélanger retrait Neo4j et corrections pédagogiques non liées ;
- ne supprimer aucune donnée Qdrant ;
- ne supprimer aucun volume Neo4j pendant la validation ;
- conserver l'ancien `.env` uniquement dans un emplacement local sécurisé et non versionné si une restauration est nécessaire ;
- préférer `git revert` à une réécriture destructive de l'historique.

### 12.2 Points de retour proposés

1. **Point R0** : état avant toute modification.
2. **Point R1** : runtime Qdrant-only, package Neo4j encore présent.
3. **Point R2** : ingestion Qdrant-only, package Neo4j encore présent.
4. **Point R3** : tests de protection ajoutés.
5. **Point R4** : package et dépendance supprimés.
6. **Point R5** : Docker et documentation finalisés.

### 12.3 Retour arrière selon le type de problème

#### Échec du runtime après Phase 1

- revenir au commit R0 ou réintroduire les paramètres `graph_queries` ;
- aucun changement de données n'aura été effectué ;
- Neo4j et sa dépendance seront encore disponibles.

#### Échec de l'ingestion simulée après Phase 2

- revenir à R1 ;
- rétablir uniquement les blocs GraphBuilder ;
- ne relancer aucune ingestion tant que la cause n'est pas comprise.

#### Import manquant après suppression du package

- revenir à R3 ;
- rétablir temporairement le dossier `knowledge_graph` et la ligne `neo4j>=5.14.0` ;
- corriger la référence résiduelle avant une nouvelle tentative.

#### Échec Docker après Phase 5

- restaurer la version précédente de `docker-compose.yml` ;
- restaurer localement les variables Neo4j ;
- le volume Neo4j préservé permet une reprise sans reconstruction des données du graphe.

#### Régression de la carte de compétences

- conserver le runtime Qdrant-only ;
- restaurer temporairement seulement le comportement précédent si indispensable ;
- solution préférée à moyen terme : taxonomie statique, pas réintroduction de Neo4j.

### 12.4 Conditions autorisant la suppression définitive du volume Neo4j

Toutes les conditions suivantes doivent être satisfaites :

1. suite automatisée passante ;
2. parcours manuels critiques validés ;
3. aucun import ou paramètre Neo4j dans le code actif ;
4. documentation Qdrant-only publiée ;
5. période de retour arrière terminée ;
6. autorisation explicite de suppression ;
7. nom du volume vérifié comme appartenant uniquement à ce projet.

## 13. Définition de terminé

Le retrait de Neo4j sera considéré terminé uniquement lorsque :

- le package `backend/app/rag/knowledge_graph/` n'existe plus ;
- `neo4j` n'est plus dans `requirements.txt` ;
- aucune variable `NEO4J_*` n'est requise ;
- Compose ne contient plus de service, volume ou port Neo4j ;
- le backend se construit sans `graph_queries` ;
- l'ingestion produit Qdrant + rapport, sans étape graphe ;
- la carte de compétences repose sur la mémoire élève ;
- les tests Qdrant-only et la suite existante sont passants ;
- les commandes de lancement ne mentionnent plus Neo4j ;
- les documents historiques sont annotés ;
- aucune donnée Qdrant ou mémoire élève n'a été supprimée ;
- les résultats de validation sont consignés dans `CHANGELOG_LOCAL.md`.

## 14. Décision requise avant exécution

Ce document n'autorise aucune modification. L'exécution devra commencer uniquement après une instruction explicite précisant au minimum que la Phase 0 et la Phase 1 peuvent être lancées. Les suppressions physiques du package, de la dépendance et surtout du volume Docker devront rester des décisions séparées et contrôlées.
