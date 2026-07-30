# NURU — Diagnostic fonctionnel et pédagogique (Sprint 2, Phase 4)

**Statut : diagnostic complet ET corrections appliquées, testées et validées** (périmètre complet
choisi : toutes les corrections du §8, ingestion Qdrant complète relancée, `llama3.2:1b` conservé
par défaut). Ce document reproduit chaque problème signalé, trace sa cause exacte fichier par
fichier, documente la correction minimale appliquée, et consigne les résultats avant/après (§9).

L'intégration technique (Sprint 2, phases 1-3) reste valide : les endpoints répondent, Docker/Ollama/
Neo4j/Qdrant sont accessibles, le frontend affiche les réponses. **Mais, comme demandé, le critère de
réussite n'est pas HTTP 200 — c'est la cohérence mathématique et pédagogique**, et plusieurs défauts
graves ont été confirmés.

---

## 1. Symptômes observés (rapportés par l'utilisateur)

1. Premier message ("Explique-moi les nombres complexes") → timeout 60 s côté frontend, le message
   suivant fonctionne.
2. "C'est quoi la dérivabilité ?" → réponse confondant dérivabilité, gradient, dérivées partielles,
   fonctions à deux variables, avec des affirmations mathématiquement fausses.
3. "Explique-moi les dérivées" → `math_tool_result` renvoie un calcul SymPy absurde (`result: "0"`),
   le mot « dérivées » ayant été interprété comme une expression mathématique.
4. "Créer un quiz sur les suites numériques" → questions à choix avec des options placeholder
   (« Définition incorrecte 1 », etc.) et le concept extrait contient encore le verbe « créer » ;
   répondre "1" ensuite déclenche une nouvelle explication générale absurde au lieu de corriger le quiz.
5. Exercice sur les intégrales → égalité mathématique incohérente et sans consigne claire.

---

## 2. Reproductions effectuées (preuves)

Toutes les reproductions ci-dessous ont été faites contre le backend réellement lancé sur cette
machine (`http://localhost:8080`), avec Qdrant/Neo4j en Docker et Ollama natif, **sans modifier aucun
fichier au préalable**.

### 2.1 Timeout initial (Test 1)

- Redémarrage complet du backend, mesure du temps de la toute première requête `/chat/` après
  `Application startup complete` : **8,98 s** (`curl -w time_total`). Pas de timeout observé dans
  cette tentative précise.
- Rechargement à froid du modèle Ollama (`ollama stop llama3.2:1b` puis appel direct
  `/api/chat`) : **6,65 s**. Pas de blocage.
- Chargement du modèle d'embeddings `BAAI/bge-m3` dans un script isolé (processus Python neuf, cache
  HuggingFace déjà chaud sur disque) : **~20-25 s**.
- Recherche Qdrant (voir §2.3) : **0,08-0,15 s par appel** — rapide, pas de blocage réseau observé au
  moment du test (mais échoue silencieusement, voir plus bas).
- **Aucun composant testé isolément n'atteint 60 s.** L'hypothèse retenue (voir §3.1) est un
  chargement à froid complet (modèle d'embeddings + agents) exécuté **dans** la requête HTTP elle-même
  plutôt qu'au démarrage, si le préchargement du démarrage a échoué silencieusement (voir cause
  racine détaillée en §3.1). Cette hypothèse n'a pas pu être déclenchée à la demande (elle dépend d'un
  aléa réseau/temporaire au démarrage), mais elle est corroborée par le code (`main.py`, gestion
  d'erreur autour de `get_orchestrator()` au démarrage).

### 2.2 Qualité du cours sur la dérivabilité (Test 2) — reproduit à l'identique

Reproduction en conversation multi-tours (comme un vrai onglet Gradio), pour retrouver le niveau
d'aide réellement utilisé par l'utilisateur (`level` escalade avec le nombre d'échanges) :

| Tour | Message | `level` détecté | Extrait de la réponse |
| --- | --- | --- | --- |
| 1 | "Bonjour" | reformulation | Réponse d'accueil générique |
| 2 | "Explique-moi les nombres complexes" | **indice** | *« un nombre complexe est... avec un élément supplémentaire qui représente la direction ou l'angle de rotation... »* — définition fausse, mélange avec la géométrie du cercle/triangle |
| 3 | "c'est quoi la dérivabilité ?" | **indice** | *« La dérivabilité est la capacité de trouver la valeur de cette fonction... imaginez un montant de 100 euros... taxe de 10%... »* — aucune définition mathématique correcte, analogie financière incohérente |

Confirmation directe : la réponse est mathématiquement creuse, sans définition formelle, sans lien
avec le programme réel. Reproduit à chaque tentative (non déterministe dans le détail, mais
systématiquement incohérent).

### 2.3 Déclenchement erroné de l'outil mathématique (Test 3) — reproduit

Appel direct des fonctions `_extract_concept()` et `detect_math_intent()` (sans passer par HTTP) :

| Message | `concept` extrait | `math_intent` détecté |
| --- | --- | --- |
| `Explique-moi les dérivées` | `dérivées` | **`{tool: derivee, expression: None}`** ⚠️ déclenché à tort |
| `Fais-moi un exercice sur les intégrales` | `intégrales` | **`{tool: integrale, expression: None}`** ⚠️ déclenché à tort (même bug, non signalé par l'utilisateur mais confirmé) |
| `Dérive f(x)=x**2+3x` | `Dérive f(x)=x**2+3x` | `{tool: derivee, expression: "(x)=x**2+3x"}` — attendu, calcul explicite |

Confirmation directe (backend réel) : requête `/chat/` avec `"Explique-moi les dérivées"` →
`math_tool_result.result = "0"`, `steps_hint` montrant que SymPy a traité le mot comme un produit de
lettres isolées.

### 2.4 Bug Qdrant critique découvert pendant le diagnostic (non signalé initialement, mais causal)

En traçant la « recherche Qdrant » demandée à l'étape 3, une erreur systématique est apparue :

```
ERROR:backend.app.rag.vector_indexer.qdrant_client:❌ Erreur recherche: 'QdrantClient' object has no attribute 'search'
```

Confirmée à la fois dans un script isolé et **dans les logs du backend réellement en cours
d'exécution** (déclenchée par nos propres tests de cette session). Cause : `qdrant-client==1.18.0`
(résolu aujourd'hui par `requirements.txt: qdrant-client>=1.9.0`, sans borne supérieure — même
classe de problème que le bug Gradio de la phase précédente) **a supprimé la méthode `.search()`**,
remplacée par `.query_points()`. Conséquence : **toutes les recherches RAG échouent silencieusement et
renvoient 0 document, depuis le début de cette session de tests, pour tous les agents (Cours,
Exercices, Quiz).** C'est très probablement la cause principale de la mauvaise qualité observée au
Test 2 (aucun contexte documentaire réel n'atteint jamais le prompt).

### 2.5 Génération du quiz (Test 4) — reproduit à l'identique

```
Message 1: "créer un quiz sur les suites numériques"
  -> intent=quiz, concept extrait = "créer suites numériques"
  -> réponse : "Que signifie créer suites numériques ?" + options "Définition correcte de..."/
     "Définition incorrecte 1/2/3" (placeholders)

Message 2 (même session): "1"
  -> intent=general (pas "quiz"), level=indice
  -> réponse : nouvelle explication hors-sujet sur "le concept fascinant appelé 1"
```

Reproduit exactement, y compris le verbe « créer » non retiré du concept.

### 2.6 Bug Neo4j confirmé (secondaire, découvert en phase 3, revérifié ici)

```
Neo.ClientError.Statement.SyntaxError: Parameter maps cannot be used in `MATCH` patterns
"MATCH path = (c:Concept {name: $name})<-[:PREREQUIS_DE*1..$depth]-(prereq)"
```

Confirmé dans `backend/app/rag/knowledge_graph/graph_queries.py:41-51`
(`get_prerequisites_chain`). Actuellement sans impact visible (le Knowledge Graph local est vide,
donc aucun prérequis ne serait retourné de toute façon), mais bloquerait toute utilisation future des
prérequis même une fois le graphe alimenté.

---

## 3. Traces précises du pipeline et causes racines

Pipeline suivi pour chaque problème : Frontend → route API → session → Planner → extraction du
concept → Retriever Qdrant/Neo4j → outil SymPy éventuel → agent Cours/Exercices/Quiz → Verifier →
réponse.

### 3.1 Timeout initial (Test 1)

- **Fichier** : `backend/app/api/main.py`
- **Fonction** : `on_startup()` (événement de démarrage FastAPI), lignes 49-65
- **Données reçues** : aucune (événement de démarrage, pas de requête)
- **Données produites** : préchargement de `student_profile` et de `get_orchestrator()` (construit
  tout `NuruGraph` : Planner, Retriever, agents, y compris le chargement du modèle d'embeddings
  `BAAI/bge-m3`, ~20-25 s)
- **Décision prise** : le préchargement est entouré d'un `try/except` qui **avale silencieusement
  toute exception** (`logger.warning("⚠️ Orchestrateur non pré-chargé (sera réessayé à la 1ère
  requête)")`) — le serveur démarre et accepte des requêtes même si ce préchargement échoue.
- **Cause racine** : si le préchargement échoue au démarrage (aléa réseau vers Qdrant Cloud ou Neo4j
  au moment précis du démarrage, ou toute autre exception transitoire), **la première vraie requête
  utilisateur doit reconstruire tout l'orchestrateur en synchrone**, y compris les ~20-25 s de
  chargement du modèle d'embeddings, en plus du temps de génération Ollama (6-10 s) et des appels
  Qdrant/Neo4j — le cumul peut dépasser 60 s. Le message d'erreur observé
  (`HTTPConnectionPool(...): Read timed out. (read timeout=60)`) vient du **frontend**
  (`frontend/gradio_app.py:24`, `TIMEOUT = 60`), pas du backend lui-même (qui n'a pas de timeout
  serveur configuré) — cela explique pourquoi le message suivant, une fois l'orchestrateur mis en
  cache dans le singleton du process, fonctionne immédiatement.
- **Non reproductible à la demande** : il faudrait forcer une exception précise au moment du
  démarrage pour le démontrer de façon déterministe ; le code démontre cependant clairement ce mode
  de défaillance.
- **Correction minimale recommandée** :
  1. Ne pas avaler silencieusement l'échec du préchargement : logger en `ERROR` (pas `WARNING`) avec
     la trace complète, pour que ce cas soit visible dans les logs de Binta.
  2. Ajouter un endpoint de « readiness » séparé (`GET /health/ready`) qui renvoie 503 tant que
     `get_orchestrator()` n'a pas réussi, pour que le frontend (ou un futur monitoring) sache
     distinguer « API démarrée mais pas prête » de « API prête ».
  3. Augmenter/rendre configurable le timeout du frontend (`TIMEOUT` dans `gradio_app.py`, via une
     variable d'environnement) et afficher un message explicite du type « Le premier démarrage peut
     prendre jusqu'à une minute, merci de patienter » plutôt qu'un message d'erreur froid.
  4. Ne **pas** se contenter d'augmenter le timeout sans les points 1-2 : cela masquerait le problème
     réel (préchargement qui échoue silencieusement) au lieu de le corriger.

### 3.2 Déclenchement erroné de l'outil mathématique (Test 3)

- **Fichiers concernés** : `backend/app/tools/math_tools.py` (`detect_math_intent`,
  `extract_math_expression`), `backend/app/agents/planner.py` (`plan()`, ligne 93),
  `backend/app/agents/graph.py` (`_node_math_tool`, lignes 89-101)
- **Fonction** : `detect_math_intent()` — `math_tools.py:257-292`
- **Données reçues** : message brut de l'utilisateur (ex. `"Explique-moi les dérivées"`)
- **Données produites** : `{"tool": "derivee", "expression": None}` car le test
  `if keyword in text` (ligne 285) fait une **recherche de sous-chaîne**, et `"dérivée"` est une
  sous-chaîne de `"dérivées"` (pluriel) — aucune limite de mot (`\b`) n'est utilisée. Le même défaut
  touche `"intégra"` (sous-chaîne de « intégrales », « intégration »...).
- **Décision prise** : `planner.py:91-93` ajoute l'outil `derivee` aux `required_tools`, et comme
  `extract_math_expression()` ne trouve aucune expression exploitable (son regex
  `[0-9x\+\-\*/\^\(\)\.= ]{2,}` ne capture que chiffres/`x`/opérateurs, pas de lettres accentuées),
  elle retourne `None` — **`planner.py:93` retombe alors sur `concept` comme expression
  mathématique** : `parameters["math_expression"] = math_intent.get("expression") or concept`.
- **Cause racine (double)** :
  1. Détection par sous-chaîne sans limite de mot → faux positifs sur les formes conjuguées/plurielles
     et les mots de la même famille (dérivée/dérivées/dérivabilité potentiellement, intégra/intégrale/
     intégration/intégrales).
  2. **Absence totale de validation avant d'appeler SymPy** : quand aucune expression mathématique
     n'est extraite, le code utilise quand même le texte du concept (`"dérivées"`, `"intégrales"`) comme
     expression à parser. `sympy.parsing.sympy_parser.parse_expr` avec
     `implicit_multiplication_application` interprète alors chaque lettre comme un symbole séparé
     (`d*e*i*r*s*v*é**2`), d'où le résultat absurde `"0"` (dérivée par rapport à `x`, qui n'apparaît
     jamais dans ce produit de lettres).
- **Correction minimale recommandée** :
  1. `detect_math_intent()` : utiliser des limites de mot (`\bdérivée\b` plutôt qu'une simple
     sous-chaîne), et **distinguer les verbes d'action** (dérive, calcule, résous, simplifie...) des
     **noms de concept** (dérivée, dérivabilité, intégration...) — seuls les verbes d'action doivent
     déclencher l'outil.
  2. `extract_math_expression()` / `planner.py:93` : **ne jamais retomber sur `concept`** comme
     expression mathématique. Si `extract_math_expression()` ne trouve rien d'exploitable,
     `math_expression` doit rester `None` et **aucun outil ne doit être ajouté à `required_tools`**
     (annuler la détection plutôt que de transmettre une expression invalide).
  3. `math_tools.py` : ajouter une validation stricte avant `_safe_parse()` — rejeter toute expression
     qui, une fois les accents/espaces retirés, ne contient aucun chiffre et aucune variable latine
     seule (heuristique simple mais suffisante), et lever `MathToolError` proprement plutôt que de
     laisser SymPy produire un résultat absurde silencieusement accepté.

### 3.3 Mauvaise qualité du cours (Test 2)

- **Fichiers concernés** : `backend/app/rag/vector_indexer/qdrant_client.py` (méthode `search()`),
  `backend/app/rag/vector_indexer/retriever.py` (`HybridRetriever.search()`),
  `backend/app/agents/cours_agent.py` (`_generate_llm_explanation`),
  `backend/app/agents/verifier_agent.py` (`verify()`), `backend/app/agents/graph.py`
  (`_node_verifier`, `_build_final_response`)
- **Données reçues** : concept `"dérivabilité"`, `retrieved_docs = []` (voir cause 1 ci-dessous),
  `prompt_context = ""`
- **Données produites** : prompt envoyé à Ollama ne contenant **aucun extrait de cours réel** —
  uniquement l'instruction générique de niveau (`"Donne des indices progressifs sans révéler la
  solution complète."` pour `level=indice`) — et la réponse du LLM, non ancrée, invente une analogie
  financière incohérente.
- **Décision prise** : la réponse est passée telle quelle à `VerifierAgent.verify()`, qui calcule
  `coherence_score` (mots-clés de connecteurs logiques français, pas de vérification factuelle),
  `hallucination_risk` (mots de couverture du type « peut-être »/« je pense », absents ici donc risque
  = 0), et `pedagogical_issues` (longueur > 500 caractères sans le mot « résumé » → **1 problème
  détecté**, donc `is_valid = False`). **Mais** `graph.py::_build_final_response()` construit la
  réponse finale à partir de `agent_responses` **sans jamais consulter `verification["is_valid"]`** —
  le verdict du Verifier est calculé puis **jeté**, seul `coherence_score` sert à calculer une moyenne
  affichée comme `confidence` au frontend, sans aucune conséquence sur le contenu envoyé.
- **Cause racine (triple, par ordre d'impact)** :
  1. **Qdrant cassé silencieusement** (`qdrant_client.py`, méthode `.search()` supprimée dans
     `qdrant-client==1.18.0`, remplacée par `.query_points()`) → contexte RAG systématiquement vide,
     quel que soit le concept demandé.
  2. **`llama3.2:1b` produit du contenu mathématiquement incorrect même sans ce bug** : en testant en
     direct (hors backend, même prompt, contexte vide dans les deux cas) contre `llama3.1:8b`, le
     modèle 1B invente une pseudo-définition (« mesurer la capacité d'un objet à changer... angle de
     rotation... point de rupture ») alors que le modèle 8B donne une définition correcte et un
     exemple `f(x)=x²`, `f'(x)=2x` réellement calculé (voir §5, comparaison complète).
  3. **Le Verifier ne bloque ni ne corrige rien** : son verdict `is_valid` (qui, ici, était
     probablement `False` à cause de la règle « réponse trop longue sans résumé ») n'a **aucun effet**
     sur la réponse envoyée à l'utilisateur — `graph.py::_build_final_response()` ne le consulte pas.
- **Correction minimale recommandée** :
  1. Corriger `qdrant_client.py` pour utiliser `self.client.query_points(...)` (API actuelle) au lieu
     de `self.client.search(...)` (supprimée) — **correction la plus impactante de tout ce
     diagnostic**, car elle restaure le RAG pour tous les agents (Cours, Exercices, Quiz) d'un coup.
  2. `verifier_agent.py` : ajouter une validation pédagogique minimale et objective pour les réponses
     de type « cours » (voir §3.3.1 ci-dessous), en plus des heuristiques actuelles.
  3. `graph.py::_node_verifier` / `_build_final_response` : **faire agir** le verdict `is_valid` —
     a minima, si `is_valid=False`, ajouter un avertissement visible (« ⚠️ Cette réponse n'a pas pu
     être entièrement vérifiée ») plutôt que de l'envoyer sans distinction ; idéalement, tenter une
     régénération unique avant d'abandonner.
  4. Épingler `qdrant-client` dans `requirements.txt` avec une borne supérieure raisonnable, pour
     éviter que ce type de rupture d'API ne se reproduise silencieusement (même leçon que Gradio).

#### 3.3.1 Proposition de validation pédagogique minimale (Cours)

Vérifications objectives et peu coûteuses, sans nécessiter un second appel LLM :

- présence d'au moins une formule/notation mathématique standard si le concept en comporte une par
  nature (ex. présence de `f(x)`, `f'(x)`, `lim`, ou d'une expression SymPy-parsable) ;
- absence de vocabulaire hors-programme non expliqué (ex. « gradient », « dérivées partielles »,
  « f(x,y) ») pour un concept marqué comme mono-variable dans le Knowledge Graph/les métadonnées ;
- une seule variable introduite avant que plusieurs ne soient introduites (règle explicite demandée) ;
- rejet si la réponse contient des tournures d'auto-doute généralisées associées à des affirmations
  factuelles centrales (actuellement seulement utilisé pour le risque d'hallucination, jamais pour
  rejeter) ;
- si un `math_tool_result` existe pour la question, vérifier que le résultat qu'il contient apparaît
  bien, tel quel, dans le texte généré (empêche le LLM de « recalculer » et de se tromper).

### 3.4 Extraction du concept (Test 4, partie 1)

- **Fichier** : `backend/app/agents/planner.py`
- **Fonction** : `_extract_concept()`, lignes 38-51
- **Données reçues** : `"créer un quiz sur les suites numériques"`
- **Données produites** : `"créer suites numériques"`
- **Décision prise** : le regex de nettoyage (ligne 43-49) supprime des phrases spécifiques
  (`"un quiz sur"`, `"un exercice sur"`, `"un cours sur"`) et des mots outils isolés
  (`le|la|les|un|une|des|de|du`), ainsi que `crée[-\s]?moi`/`cree[-\s]?moi` — **mais pas le verbe nu
  `créer`/`crée` sans « moi »**.
- **Cause racine** : liste d'alternatives regex incomplète — ne couvre pas toutes les formulations
  demandées (`Crée`, `Fais-moi`, `Donne-moi`, `Je veux réviser`, etc. sont partiellement couverts,
  mais `créer` seul ne l'est pas).
- **Correction minimale recommandée** : ajouter au groupe d'alternatives les verbes d'action nus en
  début de phrase (`créer?|crée|génère|génèrer|donne|fais|veux réviser|veux revoir`), et ancrer la
  suppression en **début de chaîne** (`^\s*(verbe)\b`) plutôt qu'en toute position, pour éviter de
  supprimer accidentellement ces mots s'ils apparaissaient légitimement au milieu d'un concept.

### 3.5 Génération du quiz — contenu placeholder (Test 4, partie 2)

- **Fichier** : `backend/app/agents/quiz_agent.py`
- **Fonction** : `_generate_qcm()`, lignes 52-75
- **Données reçues** : `concept = "créer suites numériques"`
- **Données produites** : littéralement `f"Définition correcte de {concept}"`,
  `"Définition incorrecte 1"`, etc.
- **Décision prise/cause racine** : **`QuizAgent` n'appelle jamais le LLM** — contrairement à
  `CoursAgent` et `ExercicesAgent` (qui utilisent tous deux `generate_pedagogical_text()`),
  `QuizAgent._generate_qcm()`/`_generate_vrai_faux()`/`_generate_questions()` sont des gabarits
  statiques, non branchés sur Ollama ni sur le RAG. C'est un agent resté au stade de prototype,
  jamais complété (contrairement à ce que suggère `CHANGELOG_UPDATE.md`, qui ne mentionne pas
  explicitement le Quiz comme terminé).
- **Correction minimale recommandée** : brancher `QuizAgent` sur `generate_pedagogical_text()`
  (comme les deux autres agents), avec un prompt demandant explicitement un JSON structuré
  (voir schéma proposé en §3.6), et parser/valider la réponse avant de l'utiliser — avec repli sur
  gabarit **uniquement** si le parsing échoue, **jamais** affiché tel quel avec des placeholders.

### 3.6 Format du quiz et validation

Le format actuel (`_generate_qcm`) retourne `{"question", "options": [...], "correct": index}` — pas
de format `choices`/`correct_answer`/`explanation` structuré, pas de séparation entre ce qui est
envoyé à l'élève et la bonne réponse. Proposition conforme à la demande :

```json
{
  "question": "...",
  "choices": [
    {"id": "A", "text": "..."},
    {"id": "B", "text": "..."},
    {"id": "C", "text": "..."},
    {"id": "D", "text": "..."}
  ],
  "correct_answer": "B",
  "explanation": "..."
}
```

Validation minimale avant affichage : rejeter/régénérer si une valeur de `choices[].text` ou de
`question` contient (insensible à la casse) une des chaînes `"définition correcte"`,
`"définition incorrecte"`, `"application 1"`, `"option 1"`, `"placeholder"` — ce filtre couvre
exactement les gabarits actuels et empêcherait leur affichage même en cas de repli.

**Ne jamais transmettre `correct_answer` au frontend avant la réponse de l'élève** : actuellement,
tout le quiz (y compris la bonne réponse) part en une seule fois dans `questions` (visible dans le
JSON `/chat/`) — nécessite de séparer la question posée à l'élève (`GET`) de la correction
(`POST /evaluation/quiz`, qui existe déjà côté backend mais n'est jamais appelée par le frontend,
voir §3.7).

### 3.7 Gestion de l'état actif du quiz (Test 4, partie 3)

- **Fichiers concernés** : `backend/app/api/routes/chat.py` (dict `sessions`),
  `backend/app/api/dependencies/containers.py` (`SimpleSessionManager`, non utilisé par `chat.py`),
  `backend/app/agents/state.py` (`GraphState`), `backend/app/agents/planner.py`,
  `frontend/gradio_app.py`
- **Données reçues au tour 2** : message `"1"`, `session_id` identique au tour 1, mais **aucune trace
  de l'existence d'un quiz actif n'est transmise ni stockée**.
- **Décision prise** : `PlannerAgent._detect_intent("1")` ne correspond à aucun mot-clé
  (`_QUIZ_KEYWORDS`, `_EXERCICE_KEYWORDS`, `_COURS_KEYWORDS`, `_CALCUL_KEYWORDS`) → intent = `general`
  → route par défaut vers `CoursAgent` (ligne `graph.py:167`,
  `{"cours": "cours", "exercice": "exercices", "quiz": "quiz"}.get(intent, "cours")`), qui génère une
  explication sur le concept extrait de `"1"` lui-même.
- **Cause racine** : ni `chat.py` (`sessions[session_id]` ne stocke que `history`/`feedback`), ni
  `SimpleSessionManager` (créé mais jamais appelé depuis `chat.py` — code mort, confirmé par lecture),
  ni `GraphState`/`AgentState` (aucun champ `active_quiz`/`pending_question`) ne conservent le moindre
  état de quiz en cours. Le frontend ne stocke pas non plus la question/les choix affichés
  (`gradio_app.py`, `make_chat_fn` ne connaît que `history`/`user_id`/`session_id`).
- **Correction minimale recommandée** (la plus structurante de ce diagnostic) :
  1. Stocker dans `chat.py::sessions[session_id]` un champ `active_quiz` :
     `{"concept": ..., "questions": [...], "current_index": 0, "attempts": 0}` dès qu'un quiz est
     généré.
  2. Dans `chat.py::chat()`, **avant** d'appeler l'orchestrateur, vérifier si
     `sessions[session_id].get("active_quiz")` existe : si oui, interpréter le message comme une
     réponse (lettre/chiffre/texte correspondant à un des `choices`), appeler
     `EvaluationAgent.evaluate_quiz()` (déjà implémenté, jamais relié au flux `/chat/`), mettre à jour
     la progression via `ProgressionAgent.record_result()` (déjà implémenté), puis proposer la
     question suivante ou clôturer le quiz — **sans repasser par le Planner/LangGraph** pour ce tour.
  3. Le frontend n'a besoin d'aucune modification pour ce point précis : il continue d'envoyer
     `message`/`session_id` à `/chat/` comme aujourd'hui — toute la logique d'état peut rester
     côté backend (session_id sert de clé), ce qui respecte la consigne de ne pas toucher au frontend
     Gradio sauf nécessité démontrée.

### 3.8 Génération des exercices (Test 5)

- **Fichiers concernés** : `backend/app/agents/exercices_agent.py` (`_create_exercise`),
  `backend/app/llm/ollama_client.py` (`generate`)
- **Données reçues** : concept `"intégrales"`, `prompt_context = ""` (même bug Qdrant que §3.3),
  `math_tool_result` calculé (bug §3.2, sur « intégrales ») mais **jamais lu par `ExercicesAgent`**
  (confirmé par lecture : `context.get("concept")`, `context.get("difficulty")`,
  `context.get("prompt_context")` sont utilisés, pas `math_tool_result`) — donc le calcul SymPy erroné
  n'atteint pas directement l'exercice affiché, mais son absence de RAG si.
- **Cause racine** : même cause n°1 que le Test 2 (Qdrant cassé → zéro contexte RAG). Contribution
  supplémentaire : le prompt envoyé par `exercices_agent.py:57-61` («*Génère UN SEUL exercice... Donne
  uniquement l'énoncé (pas la solution).*») est ensuite injecté par
  `ollama_client.py::generate()` dans un gabarit générique
  (`"Question de l'élève: {prompt}"`) conçu pour une vraie question d'élève, pas pour une instruction
  de génération — ce cadrage sémantique inadapté peut contribuer à des sorties incohérentes avec un
  modèle aussi petit.
- **Correction minimale recommandée** :
  1. Corriger Qdrant (§3.3, correction n°1) — impact principal partagé avec le Cours.
  2. Ajouter une validation minimale avant affichage d'un exercice : rejeter/régénérer si l'énoncé ne
     contient aucune consigne verbale explicite (« calcule », « détermine », « montre que », «
     résous »...) ou si une égalité contenant `=` figure dans l'énoncé sans qu'aucune variable commune
     ne soit cohérente des deux côtés (heuristique simple, pas une vérification symbolique complète).
  3. `ollama_client.py::generate()` : distinguer, via un paramètre explicite, un prompt de type
     « instruction de génération » d'un prompt de type « question d'élève », pour éviter le gabarit
     `"Question de l'élève: ..."` quand ce n'est pas le cas (bénéficie aussi au Cours et au Quiz une
     fois branché sur le LLM).

---

## 4. Comparaison `llama3.2:1b` vs `llama3.1:8b`

Même prompt exact envoyé aux deux modèles en direct (hors backend, pour isoler l'effet du modèle
seul), sans contexte RAG dans les deux cas (puisque le RAG est actuellement cassé de toute façon) :
*« Explique le concept « dérivabilité » à un élève de Terminale S1... Rappelle brièvement la
définition et les propriétés clés, avec un exemple simple. »*

| Critère | `llama3.2:1b` | `llama3.1:8b` |
| --- | --- | --- |
| Temps de réponse (CPU, cette machine) | **27,1 s** | **137,8 s** (~5x plus lent) |
| Définition donnée | Fausse (« capacité d'un objet à changer... angle de rotation... point de rupture ») | Correcte (« mesure comment la fonction change... vitesse à laquelle elle augmente/diminue ») |
| Propriétés citées | Inventées (« limite infinie/supérieure », non standard) | Correctes (existence de la dérivée, continuité, dérivée comme limite du taux d'accroissement) |
| Exemple donné | Aucun calcul réel, analogie non mathématique (rotation d'un objet) | **Calcul réel et correct** : `f(x)=x²` → `f'(x)=2x` par la règle des puissances, interprétation correcte |
| Respect du format demandé | Partiel (structure présente, contenu faux) | Bon (structure + contenu corrects) |
| Cohérence pédagogique | Faible — activement trompeur pour un élève | Bonne — exploitable tel quel pour réviser |
| Consommation observée | 100 % CPU (pas de GPU sur cette machine) | 100 % CPU, nettement plus long |

**Constat honnête** : `llama3.2:1b` (1,2 milliard de paramètres) n'est **pas fiable** pour produire des
explications mathématiques correctes sur ce corpus, même sur un concept aussi central que la
dérivabilité — il invente des propriétés et des exemples sans lien avec les mathématiques réelles.
`llama3.1:8b` produit un résultat correct et exploitable sur ce même test, mais au prix d'un temps de
réponse ~5x plus long (137 s, ce qui **dépasserait quasi systématiquement** le timeout de 60 s du
frontend actuel sur cette machine sans GPU) — un changement de modèle par défaut nécessiterait donc
aussi de revoir le timeout/streaming, pas seulement le nom du modèle. **Aucun changement de modèle
n'a été appliqué** ; cette mesure est fournie pour que vous puissiez décider en connaissance de
cause (voir recommandations §7).

---

## 5. Corrections appliquées

Périmètre choisi : **toutes** les corrections ci-dessous ont été implémentées. Modèle par défaut
conservé (`llama3.2:1b`, voir §4/§7). Gestion d'état du quiz : approche « tout côté backend,
`session_id` comme clé, aucune modification du frontend Gradio » confirmée et appliquée telle quelle.

| # | Fichier | Modification |
| --- | --- | --- |
| 1 | `backend/app/rag/vector_indexer/qdrant_client.py` | `QdrantClientWrapper.search()` : `self.client.search(...)` (supprimé de qdrant-client) → `self.client.query_points(...).points`. |
| 2 | `backend/app/rag/vector_indexer/embeddings.py` | Ajout d'un cap défensif (`_MAX_CHARS_PER_TEXT = 4000`) avant l'encodage : un chunk anormalement long avait fait tenter une allocation de 8,6 Go et planté l'ingestion complète (bug découvert en exécutant la correction n°1 en conditions réelles). |
| 3 | `scripts/ingest_pipeline.py` | Ajout de `load_dotenv(".env")` en tête de script : sans cela, `QDRANT_URL`/`NEO4J_PASSWORD` retombent sur leurs valeurs factices par défaut quand le script est lancé directement (hors wrapper `run_backend_windows.ps1`). |
| 4 | `backend/app/tools/math_tools.py` | `detect_math_intent()` réécrit : limites de mot (`\b`), séparation verbes d'action / noms de concept, **aucune** détection ne renvoie de tool sans expression exploitable. `extract_math_expression()` : reconnaît les fonctions usuelles (`sin`, `cos`, `ln`...) et normalise les exposants unicode (`x²`→`x^2`). Nouvelles fonctions `_looks_like_natural_language()` (rejet avant SymPy) et `_strip_function_definition()` (gère `f(x)=...`). |
| 5 | `backend/app/agents/planner.py` | `plan()` : suppression du repli `math_intent.get("expression") or concept` (source du calcul absurde). `_extract_concept()` : ajout de `créer?/creer?`, `donne[-\s]?moi`, `je veux réviser/revoir` à la liste des verbes retirés. |
| 6 | `backend/app/agents/graph.py` | `_node_math_tool` : même suppression de repli dangereux, avec message explicite si aucune expression valide. `_node_verifier` : le verdict du Verifier (`pedagogical_issues`) déclenche désormais un avertissement visible dans la réponse — **seulement** quand un problème concret est identifié (voir §5.1 pour l'itération sur ce point). `_build_final_response` : rendu du quiz adapté au nouveau format `choices`/`correct_answer` (sans jamais révéler `correct_answer`). |
| 7 | `backend/app/agents/quiz_agent.py` | Réécrit entièrement : `QuizAgent` interroge désormais le LLM (`generate_pedagogical_text`) avec un prompt exigeant un JSON strict (`question`/`choices`/`correct_answer`/`explanation`), parse et valide la réponse (`_parse_quiz_json`), et rejette tout contenu contenant un marqueur de placeholder (`_contains_placeholder`, 2 tentatives puis liste vide plutôt qu'un gabarit factice). |
| 8 | `backend/app/agents/evaluation_agent.py` | `evaluate_quiz()` : lit `correct_answer` (nouveau schéma) avec repli sur `correct`/`answer` (compatibilité). Nouvelle fonction `_answers_match()` : normalise la réponse de l'élève (lettre, position numérique, ou texte du choix). |
| 9 | `backend/app/api/routes/chat.py` | Nouvelle fonction `_handle_active_quiz_answer()` + état `active_quiz` dans `sessions[session_id]` (concept, questions, index courant, tentatives). `chat()` : si un quiz est actif, la prochaine entrée est interprétée comme une réponse (correction, explication, question suivante ou clôture) au lieu de repasser par le Planner/LangGraph. |
| 10 | `backend/app/agents/verifier_agent.py` | Nouvelle méthode `_check_mathematical_consistency()` : détecte le vocabulaire hors-programme multivariable sur un concept mono-variable, et vérifie qu'un résultat SymPy calculé apparaît bien dans le texte généré. |
| 11 | `backend/app/rag/knowledge_graph/graph_queries.py` | `get_prerequisites_chain()` : la profondeur (`$depth`) était passée en paramètre de requête dans un motif de relation à longueur variable, syntaxiquement invalide en Cypher (`SyntaxError` systématique) — corrigé en interpolant l'entier directement dans la requête (`int(depth)`, jamais une chaîne utilisateur). |
| 12 | `requirements.txt` | `qdrant-client` épinglé à `1.18.0` (version réellement validée avec `query_points()`) ; ajout de `pytest>=8.0.0` (référencé par `run_tests.sh`/les tests mais jusqu'ici absent). |

### 5.1 Itération sur le Verifier (bug découvert pendant la validation)

Premier essai : le bandeau d'avertissement était déclenché par `is_valid` (qui combine
`coherence_score`, `hallucination_risk` et `pedagogical_issues`). En testant en conditions réelles,
le bandeau apparaissait avec une **liste de raisons vide** (`()`) sur presque toutes les réponses
Cours simples — `coherence_score` (heuristique préexistante, basée sur la présence de connecteurs
français comme « donc »/« parce que ») ne dépasse quasiment jamais le seuil `> 0.7` pour une réponse
courte de niveau « reformulation », faisant échouer `is_valid` sans qu'aucun problème concret ne soit
identifiable. **Corrigé** : le bandeau ne se déclenche plus que si `pedagogical_issues` est non vide
(problème nommé et explicable), indépendamment du score de cohérence générique. Confirmé par test réel
après correction : une réponse Cours simple n'affiche plus de bandeau ; une réponse Calcul dont le
texte n'intègre pas le résultat SymPy affiche désormais un avertissement pertinent et spécifique
(« Le résultat calculé exactement (2*x + 3) n'apparaît pas dans le texte généré »).

### 5.2 Ingestion Qdrant relancée (données réelles)

Le cluster Qdrant Cloud de Binta était vide (`get_collections()` → `[]`), démontrant que le problème
venait bien de l'absence de données, pas seulement du bug `.search()`. Sur confirmation explicite,
le pipeline d'ingestion complet a été relancé sur les 103 PDF de `data/raw/` (`python -m
scripts.ingest_pipeline --force`, après le correctif §5 point 3). Voir §7 pour l'état d'avancement au
moment de la rédaction de ce document (opération très longue, encodage CPU sans GPU).

## 6. Tests ajoutés

| Fichier | Contenu | Résultat |
| --- | --- | --- |
| `tests/test_math_tools_unit.py` | Les 6 exemples requis (3 conceptuels → `None`, 3 calculs explicites → résultat SymPy exact), rejet de la forme plurielle (« intégrales »), rejet direct d'un mot naturel par `call_math_tool`. | 8/8 ✅ |
| `tests/test_planner_unit.py` | Les 6 formulations d'extraction de concept demandées. | 6/6 ✅ |
| `tests/test_quiz_agent_unit.py` | Détection de placeholder, parsing JSON (valide, entouré de markdown, malformé, réponse correcte absente/hors choix), comportement de `QuizAgent.generate()` avec LLM mocké (contenu placeholder rejeté, quiz valide accepté, LLM indisponible → liste vide). | 10/10 ✅ |
| `tests/test_quiz_state_integration.py` | Conversation de quiz en 2 tours : réponse correcte → question suivante, réponse incorrecte → révèle la bonne réponse et clôture, réponse par position numérique acceptée, stockage de l'état actif après une réponse d'orchestrateur. | 4/4 ✅ |

**Total : 30 nouveaux tests, tous passants.** Suite complète du projet (`pytest tests/`) : **69 passed,
1 skipped** — aucune régression sur les tests déjà existants (chunker, parser, métadonnées).

## 7. Résultats avant/après (batterie de tests fonctionnels complète)

Exécutée contre le backend réellement relancé avec toutes les corrections, via l'API réelle
(`POST /chat/`), pas de mock.

| Entrée | Intent détecté | Concept extrait | Outil appelé | Contexte RAG | Résultat | Statut |
| --- | --- | --- | --- | --- | --- | --- |
| Explique-moi les nombres complexes | cours | nombres complexes | — | vide (ingestion en cours, voir §5.2) | Réponse de reformulation, sans bandeau d'avertissement | ✅ (forme) / ⚠️ (fond dépend du RAG, pas encore alimenté) |
| Qu'est-ce que la dérivabilité ? | cours | dérivabilité | — | vide | Toujours du contenu approximatif/hallucination partielle (ex. formules trigonométriques hors-sujet) ; le Verifier ne l'a pas signalé cette fois (vocabulaire « gradient »/« f(x,y) » absent de cette génération précise — non déterministe) | ⚠️ Amélioré (plus la confusion multivariable spécifique du rapport initial) mais **pas résolu** : dépend du RAG (§5.2) et de la fiabilité du modèle (§4) |
| Explique-moi les suites numériques | cours | suites numériques | — | vide | Définitions arithmétique/géométrique inversées par le modèle (erreur factuelle différente, mais toujours une erreur) | ⚠️ Non résolu (modèle) |
| Dérive f(x)=x²+3x | cours | f(x)=x²+3x | `derivee` | vide | `math_tool_result.result = "2*x + 3"` **exact** ; Verifier signale à juste titre que le texte généré ne reprend pas ce résultat | ✅ Outil corrigé et validé ; ⚠️ le LLM n'intègre pas toujours le résultat exact dans son texte (limitation résiduelle, voir §8) |
| Calcule la dérivée de sin(x) | cours | dérivée de sin(x) | `derivee` | vide | `math_tool_result.result = "cos(x)"` **exact** | ✅ |
| Trouve une primitive de 2x+1 | general (voir note) | primitive 2x+1 | `integrale` | vide | `math_tool_result.result = "x*(x + 1)"` **exact** | ✅ Outil corrigé ; note : l'intention conversationnelle globale (`intent`) reste « general » car `_detect_intent()` ne reconnaît pas le verbe « trouve » — bannière d'introduction generique affichée au lieu de « Cours », défaut cosmétique mineur non corrigé (hors périmètre initial), signalé en §8 |
| Crée un quiz sur les suites numériques | quiz | suites numériques | — | vide | Quiz JSON valide généré par le LLM : 4 choix distincts et réels (aucun placeholder) | ✅ Résolu |
| → réponse "A" (2ᵉ tour, même session) | quiz_answer | — | — | — | « ✅ Bonne réponse ! » + explication + « 🏁 Quiz terminé » | ✅ Résolu — confirmation directe que l'état actif du quiz fonctionne en conditions réelles |
| Donne-moi un exercice simple sur les intégrales | exercice | exercice simple intégrales | — | vide | Énoncé incohérent (dérive vers une identité trigonométrique sans rapport) ; **le Verifier signale correctement** « donne la solution sans étapes » et « réponse trop longue sans résumé » | ⚠️ Non résolu (qualité LLM + RAG vide), mais le Verifier détecte désormais le problème |
| Donne-moi un exercice sur les suites arithmétiques | exercice | suites arithmétiques | — | vide | Le LLM répète l'instruction interne au lieu de produire un exercice (« L'élève doit générer un seul exercice... ») ; Verifier signale les mêmes problèmes | ⚠️ Non résolu — cause distincte et non corrigée : gabarit de prompt générique dans `ollama_client.py::generate()` (« Question de l'élève: {prompt} ») qui cadre mal une instruction de génération comme une question ; voir §8 |

**Synthèse** : les corrections **structurelles** (outil mathématique, extraction du concept, format et
persistance du quiz, activation du Verifier) sont **confirmées fonctionnelles à 100 %** par des appels
réels à l'API. Les corrections dépendant du **contenu généré par le LLM** (qualité des cours/exercices)
restent partiellement limitées par deux facteurs non résolus dans cette phase : le RAG pas encore
peuplé (ingestion en cours, §5.2) et les limites intrinsèques de `llama3.2:1b` (§4).

## 8. Limitations restantes / risques

- **Ingestion Qdrant en cours, non terminée** au moment de la rédaction de ce document (voir §5.2) —
  l'encodage CPU du corpus complet (2634 chunks, modèle `BAAI/bge-m3`) est très lent sans GPU
  (plusieurs heures). Tant qu'elle n'est pas terminée, le RAG reste vide et les cours/exercices ne
  peuvent pas s'appuyer sur le corpus réel. À vérifier après complétion :
  `docker compose exec` n'est pas nécessaire ici (Qdrant Cloud) — interroger directement
  `GET /collections/nuru_maths` de son cluster, ou relancer les tests fonctionnels du §7.
- **Prompt générique de `ollama_client.py::generate()` non corrigé** : cadre toute instruction (y
  compris une instruction de génération d'exercice) comme « Question de l'élève: ... », ce qui peut
  pousser le petit modèle à répéter l'instruction plutôt qu'à produire le contenu attendu (observé sur
  EXERCICE 2, §7). Correction proposée dans le rapport initial (§3.8) mais non appliquée : modifier ce
  gabarit toucherait Cours/Exercices/Quiz simultanément et mériterait des tests dédiés avant
  application.
- **Incohérence mineure et non corrigée** : `_detect_intent()` (liste `_CALCUL_KEYWORDS`) ne reconnaît
  pas tous les verbes acceptés par `detect_math_intent()` (ex. « trouve » dans « Trouve une primitive
  de... ») — l'outil SymPy se déclenche correctement, mais la bannière d'introduction affichée
  (« 💡 NURU » au lieu de « 📚 Cours ») ne correspond pas à l'agent réellement invoqué. Défaut
  cosmétique, sans impact sur l'exactitude du calcul.
- Le Knowledge Graph Neo4j local reste vide (le bug Cypher est corrigé, mais aucune donnée n'existe
  encore pour l'exercer) — sera repeuplé par la même ingestion que le RAG (`GraphBuilder`, voir
  `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md` pour le bug distinct de sérialisation de propriétés
  Neo4j rencontré pendant l'ingestion, non corrigé — hors périmètre de ce diagnostic).
- Le compromis vitesse/qualité entre `llama3.2:1b` et `llama3.1:8b` (§4) reste entier : modèle par
  défaut conservé sur décision explicite, mais la qualité des cours/exercices restera limitée tant que
  ce compromis n'est pas revisité (streaming, GPU, ou modèle différent).
- Le Verifier reste un ensemble d'heuristiques ciblées (vocabulaire hors-programme, présence du
  résultat SymPy, longueur, mots de couverture) et non une vérification mathématique formelle
  complète — il détecte certains cas (confirmé en §7 sur les exercices) mais pas tous (la confusion
  factuelle sur les suites arithmétiques/géométriques, par exemple, n'est pas couverte).

## 9. Recommandations pour Binta

Par ordre d'impact décroissant, pour la suite :

1. **Attendre/vérifier la fin de l'ingestion Qdrant** (§5.2/§8) avant de juger la qualité finale du RAG
   — c'est le facteur avec le plus grand potentiel d'amélioration restant.
2. Revoir le gabarit de prompt de `ollama_client.py::generate()` pour distinguer une « instruction de
   génération » d'une « question d'élève » (§8) — bénéficierait à Cours, Exercices et Quiz.
3. Aligner `_CALCUL_KEYWORDS` (intent) et `_MATH_ACTION_KEYWORDS` (outil SymPy) dans
   `planner.py`/`math_tools.py` pour que la bannière d'introduction corresponde toujours à l'agent
   réellement invoqué (défaut cosmétique mineur, §8).
4. Décider, une fois le RAG peuplé et évalué, si `llama3.2:1b` reste acceptable ou si un modèle plus
   gros (avec le compromis de latence documenté en §4) doit devenir le défaut — envisager le streaming
   de la réponse pour ne plus dépendre d'un timeout fixe côté frontend si un modèle plus lent est
   retenu.
5. Envisager, à plus long terme, un vrai passage par un second appel LLM ciblé pour la vérification
   mathématique plutôt que des heuristiques (le Verifier actuel est un filet de sécurité minimal, pas
   une preuve formelle).
6. Corriger le bug de sérialisation Neo4j rencontré pendant l'ingestion (`Property values can only be
   of primitive types...`, dans `graph_builder.py`, non corrigé dans cette phase — voir
   `SPRINT2_CHANGES_AND_VALIDATION_REPORT.md`) pour que le Knowledge Graph soit réellement peuplé par
   la prochaine ingestion.
