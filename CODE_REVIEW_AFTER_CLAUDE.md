# CODE_REVIEW_AFTER_CLAUDE.md

> Revue indépendante effectuée en lecture seule le 17 juillet 2026. Aucun test ou service n'a été lancé et aucune ingestion n'a été relancée. Les résultats de tests mentionnés ci-dessous proviennent uniquement des rapports et artefacts existants.

## 1. Résumé exécutif

Le travail de Claude est globalement utile et techniquement sérieux. Les corrections les plus importantes — compatibilité Gradio 6, migration Qdrant vers `query_points()`, détection des calculs mathématiques, extraction du concept, format du quiz et chargement du `.env` pendant l'ingestion — sont justifiées et doivent être conservées.

Cependant, la validation annoncée est trop optimiste :

- Neo4j est structurellement défaillant et n'apporte actuellement aucune donnée utile.
- L'ingestion n'est plus « en cours » : elle s'est terminée le 17 juillet à 09:09:55 après environ 12 h 30.
- Qdrant a bien reçu 2 634 chunks.
- Les statistiques Neo4j sont fausses : 5 328 créations de concepts ont échoué, mais le pipeline les comptabilise quand même comme réussies.
- Le quiz a été amélioré, mais n'utilise en réalité aucun contexte RAG à cause d'un oubli dans le graphe.
- Le Retriever peut fonctionner avec Qdrant seul.
- Le Verifier ne constitue pas une vérification mathématique fiable.
- Plusieurs problèmes non signalés subsistent dans Docker, l'ingestion, la gestion des sessions et la sécurité du parsing SymPy.

Conclusion d'architecture : la suppression de Neo4j est pertinente, réduit fortement la complexité et ne provoquera pas de perte fonctionnelle significative dans l'état actuel. Qdrant suffit pour le RAG de ce cas d'usage.

## 2. Périmètre et limites de la revue

Ont été inspectés :

- les trois rapports demandés ;
- le rapport technique initial et les README ;
- l'ensemble des sources backend, frontend, scripts, configurations et tests ;
- les rapports d'ingestion, chunks produits et journaux existants ;
- les sorties pédagogiques conservées dans le dépôt.

Les environnements virtuels, modèles binaires et PDF bruts ont été inventoriés, mais pas relus octet par octet. Aucun historique Git n'étant disponible dans le dossier courant, l'attribution à Claude repose sur les listes de fichiers et changements documentées dans ses rapports.

## 3. Architecture actuelle

```text
Gradio
  │ POST /chat/
  ▼
FastAPI ── sessions en RAM ── SQLite/PostgreSQL
  │
  ▼
Planner à règles
  │
  ▼
Retriever
  ├── Qdrant + BGE-M3
  └── Neo4j, appelé systématiquement mais vide/défaillant
  │
  ├── outil SymPy éventuel
  ▼
Cours / Exercices / Quiz
  │
  ▼
Ollama llama3.2:1b
  │
  ▼
Verifier heuristique
  │
  ▼
Progression et réponse
```

Le pipeline d'ingestion est séparé :

```text
PDF → PyMuPDF/Nougat → métadonnées → chunking
    → embeddings BGE-M3 → Qdrant
    → extraction de concepts → Neo4j
```

À l'exécution, la mémoire élève utilise SQLite si `DATABASE_URL` est absent. PostgreSQL est disponible dans Docker, mais n'est pas nécessaire au mode natif actuel.

## 4. Évaluation du travail de Claude

| Modification | Évaluation | Nécessité | Windows | Risque | Décision |
|---|---|---:|---:|---|---|
| `.gitignore` et `.env.example` | Correct | Élevée | Non | Faible | Conserver |
| Retrait des secrets du Compose | Correct | Critique | Non | Faible | Conserver |
| Neo4j Aura → Neo4j local | Correct au moment de la décision initiale, désormais obsolète | Nulle avec la nouvelle architecture | Non | Complexité inutile | Retirer |
| Port PostgreSQL hôte 5433 | Correct pour cette machine | Locale | Pas intrinsèquement | Peut surprendre ailleurs | Déplacer idéalement dans une configuration locale |
| Ollama Docker rendu optionnel | Cohérent avec Ollama natif | Oui localement | Surtout Docker Desktop | Linux moins portable | Conserver en option |
| Ports API unifiés sur 8080 | Correct | Oui | Non | Faible | Conserver |
| Scripts Windows Python 3.12 | Bonne décision | Oui | Oui | Quelques défauts | Conserver et durcir |
| `PYTHONUTF8=1` | Correct | Oui pour les consoles concernées | Oui | Très faible | Conserver |
| Nougat désactivé | Pragmatique et cohérent avec le repli PyMuPDF | Oui localement | Partiellement | Perte OCR/formules complexes | Conserver comme dépendance optionnelle |
| Gradio au format `messages` | Correct | Critique | Non | Faible | Conserver |
| `gradio==6.20.0` | Reproductible pour l'environnement validé | Oui | Non | Vieillissement futur | Conserver provisoirement |
| Qdrant `query_points()` | Correct | Critique | Non | Faible | Conserver |
| Troncature embeddings à 4 000 caractères | Empêche l'OOM, mais masque le défaut du chunker | Défensive | Non | Perte de contenu | Conserver temporairement |
| `load_dotenv()` dans l'ingestion | Correct | Oui | Non | Faible | Conserver |
| Détection des outils mathématiques | Nettement meilleure | Oui | Non | Parsing encore risqué | Conserver et sécuriser |
| Nettoyage du concept par le Planner | Utile mais incomplet | Oui | Non | Suppressions excessives possibles | Conserver avec futurs tests |
| Quiz JSON sans placeholders | Bonne correction structurelle | Oui | Non | Vérité mathématique non validée | Conserver |
| État actif du quiz | Corrige le bug original | Oui | Non | Toute prochaine saisie peut être consommée comme réponse | Conserver l'approche, revoir l'implémentation |
| Verifier rendu visible | Amélioration limitée | Oui | Non | Faux sentiment de sécurité | Conserver comme alerte, pas comme validation |
| Correction Cypher `$depth` | Correcte | Seulement si Neo4j reste | Non | Faible | Retirer avec Neo4j |
| Nouveaux tests | Bons tests ciblés | Oui | Non | Couverture trop étroite | Conserver |

### Défauts dans les scripts Windows

Le choix de Python 3.12 est bon, mais `scripts/setup_windows.ps1` :

- réutilise `venv_win` sans vérifier la version de Python qui l'a créé ;
- possède un repli fragile lorsque `$PyLauncher` ne contient que `"python"` : l'expression de découpage du tableau peut construire une commande incorrecte ;
- vérifie encore l'import `neo4j`, qui deviendra inutile.

Ces défauts ne remettent pas en cause la stratégie générale.

## 5. Points forts

- Diagnostic précis du bug Qdrant, qui expliquait l'absence totale de contexte RAG.
- Bonne séparation entre demandes conceptuelles et calculs explicites.
- Suppression du repli dangereux qui envoyait un mot naturel à SymPy.
- Correction réelle du format Gradio, avec analyse correcte des conflits de dépendances.
- Refus d'afficher des placeholders de quiz.
- Conservation de la réponse correcte du quiz côté backend jusqu'à la réponse de l'élève.
- Chargement explicite du `.env` par le pipeline.
- Ajout de tests ciblés sur les régressions observées.
- Documentation détaillée des incidents rencontrés.

## 6. Erreurs et affirmations à corriger

### 6.1 L'ingestion est terminée

Le rapport de Claude indique qu'elle est encore en cours. Les artefacts montrent désormais :

- début : 16 juillet 20:39:08 ;
- fin des embeddings : 17 juillet 09:07:01 ;
- fin de l'indexation Qdrant : 09:08:36 ;
- fin du pipeline : 09:09:55 ;
- durée totale : 45 047 secondes, soit environ 12 h 30 min 47 s ;
- 103 PDF examinés ;
- 101 succès de parsing/chunking ;
- 2 échecs ;
- 2 634 chunks créés et indexés.

Les deux documents en échec sont :

- `TD1-Probabilite-Corrige-TS1.pdf` ;
- `TD1-Probabilite-Exercices-TS1.pdf`.

### 6.2 Les statistiques Neo4j ne représentent pas des insertions réussies

Le pipeline annonce 5 340 nœuds, mais le journal contient 5 328 erreurs Neo4j :

```text
Property values can only be of primitive types or arrays thereof
```

`graph_builder.py` incrémente `stats["concepts"]` même si `_add_concept()` retourne `False`. Les compteurs sont donc des tentatives, pas des succès.

### 6.3 Le quiz n'utilise pas le RAG

`QuizAgent` sait recevoir `prompt_context`, mais `graph.py` ne lui transmet que `concept` et `quiz_type`. Le contexte est donc toujours vide pour les quiz.

La correction « quiz branché sur LLM » est réelle, mais « quiz branché sur le RAG » ne l'est pas.

### 6.4 La carte de compétences Neo4j est déjà cassée

`ProgressionAgent.get_competency_map()` appelle :

- `graph_queries.get_all_chapters()` ;
- `graph_queries.get_concepts_by_chapter()`.

Ces méthodes n'existent pas dans `GraphQueries`. L'exception est interceptée et la fonction revient silencieusement à la mémoire élève. Retirer Neo4j ne supprimera donc pas une fonctionnalité opérationnelle.

### 6.5 Les tests ne démontrent pas l'absence globale de régression

Les « 69 passed » sont une preuve utile provenant d'une exécution antérieure, mais les nouveaux tests ne couvrent pas :

- une vraie recherche Qdrant après ingestion ;
- la transmission du RAG au quiz ;
- la qualité mathématique des réponses ;
- l'isolation des sessions entre onglets ;
- l'ingestion incrémentale et sa reprise ;
- Docker ;
- les compteurs d'erreur Neo4j ;
- le Verifier sur des hallucinations réelles.

## 7. Architecture RAG sans Neo4j

### Parties utilisant encore Neo4j

- `backend/app/rag/knowledge_graph/` ;
- `RetrieverAgent._get_graph_queries()` ;
- l'injection de dépendances dans `containers.py` ;
- `NuruGraph` et `OrchestratorAgent` via `graph_queries` ;
- la carte de compétences ;
- la génération de cours enseignant ;
- la fin du pipeline d'ingestion ;
- `neo4j>=5.14.0` ;
- le service, volume, variables et `depends_on` Docker ;
- `.env`, `.env.example`, scripts de vérification et documentation ;
- tests et scripts dédiés au Knowledge Graph.

### Éléments supprimables

Avec la décision du superviseur, peuvent être retirés :

- tout le package `knowledge_graph` ;
- `get_graph_queries()` et `_graph_queries` ;
- les paramètres `graph_queries` des agents et orchestrateurs ;
- les appels Neo4j du Retriever ;
- `_build_knowledge_graph()` dans l'ingestion ;
- la dépendance Python `neo4j` ;
- le service et volume Neo4j du Compose ;
- les variables `NEO4J_*` ;
- les instructions et tests Neo4j.

La carte de compétences peut continuer à afficher les concepts réellement travaillés depuis la mémoire élève. Si une structure complète du programme est souhaitée, une simple taxonomie JSON versionnée serait plus adaptée qu'une base graphe.

### Pipeline Qdrant uniquement

Oui, il peut fonctionner avec :

```text
PDF → parsing → métadonnées → chunks → BGE-M3 → Qdrant
```

Neo4j intervient seulement après l'indexation Qdrant. Sa suppression ne bloque donc aucune étape vectorielle.

### Retriever Qdrant uniquement

Oui. Le résultat contient déjà séparément :

- `documents` ;
- `graph_context`.

`build_prompt_context()` fonctionne avec les documents seuls. Les prérequis Neo4j ne sont qu'un enrichissement optionnel, actuellement vide ou en erreur.

Le principal travail sera de supprimer les tentatives de connexion automatiques, pas de réécrire le Retriever.

## 8. Analyse de l'ingestion

### Pourquoi elle est lente

La phase réellement lente est l'encodage BGE-M3 :

- parsing/chunking : environ 12 secondes ;
- embeddings : environ 12 h 17 min ;
- transfert Qdrant : environ 95 secondes ;
- tentative Neo4j : environ 79 secondes.

Les facteurs principaux sont :

1. `BAAI/bge-m3` est un modèle d'embeddings relativement lourd exécuté sur CPU.
2. Les 2 634 textes sont envoyés dans une seule grande opération sans checkpoint.
3. Le chunker ne respecte pas réellement sa limite de 1 500 caractères lorsqu'un paragraphe individuel dépasse cette taille.
4. Sur la dernière production :

   - 244 chunks dépassent 1 500 caractères ;
   - 42 dépassent 4 000 caractères ;
   - le plus grand atteint 80 683 caractères.

5. La troncature à 4 000 empêche l'OOM, mais le modèle traite encore des entrées inutilement longues et une partie du corpus est perdue.
6. Aucun cache d'embeddings ni mécanisme de reprise n'existe.

### Était-elle bloquée ?

Non. Le journal montre une progression complète et une fin normale. L'absence de nouvelles lignes pendant l'encodage vient principalement du fait que la barre de progression de `sentence-transformers` est affichée sur la console et n'alimente pas correctement le journal fichier.

### Optimisations possibles

Priorité élevée :

- corriger `_split_large_chunks()` afin de découper aussi les paragraphes individuels trop longs ;
- indexer par petits groupes de fichiers ou de chunks avec checkpoints ;
- produire des identifiants déterministes pour éviter les doublons ;
- ne marquer un fichier « traité » qu'après succès de l'indexation Qdrant ;
- séparer parsing et embeddings pour pouvoir reprendre uniquement l'encodage ;
- rendre le modèle, le batch et le périphérique configurables ;
- utiliser un GPU si disponible, ou évaluer un modèle multilingue plus léger.

Actuellement, `--force` génère de nouveaux UUID et peut dupliquer les documents dans une collection existante. De plus, les fichiers sont marqués traités avant que l'indexation globale réussisse : un crash d'embedding peut laisser `processed_index.json` dans un état incohérent.

## 9. Qualité pédagogique

### Cours

Causes observées, par importance :

1. `llama3.2:1b` : cause majeure des erreurs factuelles.
2. RAG auparavant vide : cause majeure avant la fin de l'ingestion.
3. Prompts : trop génériques et parfois contradictoires avec la demande.
4. Verifier : ne détecte qu'une petite liste de symptômes.
5. Planner : le niveau d'aide augmente selon le nombre total de tours, pas selon les tentatives sur le même concept.
6. Retriever : techniquement rétabli, mais pas encore validé par une requête post-ingestion existante.

L'exemple conservé sur les nombres complexes est globalement meilleur que les premiers essais, mais contient encore des formulations pédagogiquement douteuses, notamment la représentation de `2i` comme une « ligne qui se déplace » et l'analogie de « multiplication de deux plans ».

### Quiz

Le problème initial venait principalement de `QuizAgent`, qui utilisait des placeholders statiques. Cette cause a été correctement supprimée.

Les risques restants sont :

- absence réelle de contexte RAG ;
- question et bonne réponse générées par le même modèle 1B ;
- validation structurelle du JSON, mais aucune validation mathématique ;
- session de quiz partagée entre les trois onglets Gradio.

Comme Cours, Exercices et Quiz utilisent le même `session_state`, commencer un quiz puis saisir une question dans l'onglet Cours peut faire interpréter cette question comme la réponse au quiz.

### Exercices

Causes principales :

- mauvais cadrage dans `OllamaClient.generate()`, qui présente une instruction de génération comme une « Question de l'élève » ;
- faible fiabilité du modèle 1B ;
- qualité variable des chunks ;
- aucune validation symbolique de l'énoncé ;
- concept parfois mal nettoyé, par exemple `exercice simple intégrales`.

Le RAG peut améliorer l'ancrage, mais ne corrigera pas à lui seul le cadrage du prompt ou les limites du modèle.

### Verifier

Le Verifier :

- calcule surtout des heuristiques lexicales ;
- produit habituellement une confiance proche de 0,5 ;
- ne contrôle pas les formules de manière générale ;
- ne régénère pas une réponse invalide ;
- peut afficher un avertissement, mais laisse passer le contenu.

Il doit être considéré comme un détecteur partiel, pas comme une garantie de justesse.

## 10. Autres risques techniques

- `Dockerfile` contient `COPY config/ ./config/`, alors qu'aucun dossier racine `config/` n'existe : le build backend peut échouer.
- Le Dockerfile frontend installe `gradio` sans version et ignore l'épinglage `6.20.0`.
- Le backend Docker utilise le Qdrant local, alors que l'ingestion terminée semble avoir ciblé le Qdrant Cloud chargé depuis `.env`. Le mode Docker peut donc interroger une collection locale vide.
- Le « hybrid retriever » utilise TF-IDF uniquement sur les candidats déjà remontés par la recherche dense : ce n'est pas une vraie recherche hybride globale.
- `score_threshold` n'est pas appliqué.
- Le contexte final est tronqué à 1 800 caractères, potentiellement au milieu d'un chunk.
- `scripts/ingest_pipeline.py` écrit `vector_config.qdrant_collection`, alors que la propriété réellement lue est `qdrant_collection_name`.
- `GraphQueries.get_related_concepts()` référence une variable Cypher `r` qui n'est jamais liée.
- `parse_expr()` de SymPy ne doit pas être présenté comme équivalent à un parseur sûr : il évalue des expressions Python et mérite une politique de symboles/fonctions explicitement autorisés.
- La session en RAM n'a ni expiration, ni persistance, ni mécanisme explicite d'annulation d'un quiz.

## 11. Éléments à conserver

- corrections Gradio et format `messages` ;
- port API 8080 cohérent ;
- scripts Windows et `PYTHONUTF8` ;
- `.gitignore`, `.env.example` et retrait des secrets ;
- Qdrant `query_points()` ;
- chargement du `.env` dans l'ingestion ;
- détection mathématique défensive ;
- extraction améliorée du concept ;
- quiz JSON et rejet des placeholders ;
- tests ajoutés ;
- troncature à 4 000 caractères comme garde temporaire ;
- Qdrant, BGE-M3 et la mémoire élève.

## 12. Éléments à retirer

- Neo4j, son package, sa dépendance et sa configuration ;
- GraphBuilder et la phase Knowledge Graph ;
- l'injection `graph_queries` ;
- les instructions de démarrage Neo4j ;
- les tests et scripts uniquement Neo4j ;
- les références documentaires affirmant que Neo4j est requis ;
- le volume et les ports 7474/7687 ;
- les métriques trompeuses `graph_nodes` et `graph_relations`.

## 13. Architecture recommandée

```text
Gradio
  → FastAPI
  → Planner
  → Retriever Qdrant
  → SymPy si calcul explicite
  → agent pédagogique
  → validation ciblée
  → Ollama
  → mémoire SQLite/PostgreSQL
```

Dans Qdrant, conserver des métadonnées suffisamment riches :

- discipline ;
- classe et série ;
- chapitre ;
- type de document ;
- type de chunk ;
- source et page ;
- niveau de difficulté ;
- présence de formules ;
- correction/exercice/cours.

Pour les prérequis ou le programme, utiliser un petit fichier JSON/YAML versionné si nécessaire.

## 14. Plan d'action priorisé

### P0 — Décision d'architecture

1. Retirer Neo4j de l'exécution, de l'ingestion, de Docker et des dépendances.
2. Mettre à jour toute la documentation autour d'une architecture Qdrant-only.
3. Clarifier Qdrant Cloud contre Qdrant local et choisir une seule source de vérité par environnement.

### P1 — Fiabiliser le RAG

4. Vérifier ultérieurement, avec des tests autorisés, que la collection contient bien 2 634 points et que les recherches retournent des passages pertinents.
5. Transmettre `prompt_context` au QuizAgent.
6. Corriger le chunking des paragraphes longs.
7. Ajouter checkpoints, reprise et identifiants déterministes à l'ingestion.
8. Exposer les sources et scores utilisés afin d'auditer chaque réponse.

### P1 — Corriger les risques fonctionnels

9. Isoler les sessions Cours, Exercices et Quiz, ou permettre d'annuler un quiz.
10. Corriger le Dockerfile backend et épingler Gradio dans le Dockerfile frontend.
11. Sécuriser réellement le parsing SymPy.

### P2 — Améliorer la pédagogie

12. Séparer les prompts « question d'élève », « génération de cours », « génération d'exercice » et « génération de quiz ».
13. Évaluer la qualité après restauration effective du RAG.
14. Comparer un modèle plus fiable ou une stratégie où le LLM reformule principalement des passages RAG.
15. Transformer le Verifier en contrôle réellement actionnable : rejet, régénération ou repli extractif.
16. Construire un jeu d'évaluation pédagogique stable avec réponses attendues.

## 15. Conclusion

La base technique laissée par Claude est meilleure que l'état initial, mais elle n'est pas encore validée au niveau annoncé. Les corrections structurelles les plus importantes sont bonnes ; les faiblesses restantes concernent surtout l'ingestion, l'ancrage réel des générations, le modèle 1B, les prompts et le Verifier.

La suppression de Neo4j est recommandée sans réserve dans ce contexte. Elle simplifiera l'installation, supprimera un composant actuellement non fonctionnel et laissera intact le cœur utile du système : Qdrant, le Retriever vectoriel, Ollama, les outils mathématiques et la mémoire élève.
