# NURU — Rapport des modifications et validations (Sprint 2, Phase 2)

Ce document couvre tout ce qui a été fait depuis le début de la « Phase 2 » (préparation du premier
lancement local Windows), en continuité de `SPRINT2_PROJECT_TECHNICAL_ANALYSIS.md` (analyse en
lecture seule, phase 1). Aucune valeur sensible réelle n'est reproduite ici.

> **Phase 4** : les tests manuels du frontend ont révélé des défauts fonctionnels et pédagogiques
> graves dans le pipeline agents/RAG (timeout initial, mauvaise qualité des cours générés, outil
> mathématique déclenché à tort, quiz avec placeholders, absence de gestion d'état du quiz). Voir
> `SPRINT2_FUNCTIONAL_AND_PEDAGOGICAL_DIAGNOSTIC.md` pour le diagnostic complet **et les corrections
> appliquées** (reproductions, causes racines fichier par fichier, 12 fichiers corrigés, 30 nouveaux
> tests, comparaison `llama3.2:1b`/`llama3.1:8b`, résultats avant/après). Résumé des points saillants
> découverts pendant cette phase, en plus des corrections du pipeline agents :
>
> - `qdrant-client==1.18.0` avait supprimé `QdrantClient.search()` (remplacé par `query_points()`) —
>   le RAG était silencieusement cassé depuis le début du Sprint 2 (corrigé).
> - Le cluster Qdrant Cloud de Binta était vide (aucune collection) — l'ingestion complète des 103 PDF
>   a été relancée sur confirmation explicite (`python -m scripts.ingest_pipeline --force`), toujours
>   en cours au moment de la rédaction (encodage CPU très long, plusieurs heures sans GPU).
> - `scripts/ingest_pipeline.py` ne chargeait pas `.env` (corrigé) et l'encodeur d'embeddings a tenté
>   d'allouer 8,6 Go pour un chunk anormalement long (cap défensif à 4000 caractères ajouté).
> - **Nouveau bug découvert, non corrigé (hors périmètre de cette phase)** :
>   `backend/app/rag/knowledge_graph/graph_builder.py` envoie une propriété de type Map/dict
>   directement à Neo4j (`Property values can only be of primitive types or arrays thereof`), rejeté
>   par le driver — le Knowledge Graph reste vide même après l'ingestion complète. À corriger avant de
>   compter sur les prérequis du Knowledge Graph.

---

## 1. Objectif initial

Corriger uniquement ce qui bloque un premier lancement local sous Windows, sans changer
l'architecture ni le fonctionnement du projet, en utilisant l'Ollama natif déjà installé (pas de
second Ollama en conteneur), en évitant les ports déjà occupés par vos autres projets, et en
sécurisant les secrets trouvés en clair dans le dépôt.

## 2. État original du projet (rappel, voir aussi l'analyse phase 1)

- Aucun `.gitignore`, secrets Qdrant/Neo4j réels en clair dans `.env` **et** codés en dur dans
  `docker-compose.yml`.
- `docker-compose.yml` connectait le backend au Neo4j Aura cloud personnel de Binta, alors qu'un
  conteneur `neo4j` local était démarré pour rien à côté.
- Port `5432` (Postgres) et `11434` (Ollama) en conflit avec d'autres projets sur cette machine.
- Incohérence de port API (`8000` vs `8080`) entre `.env`/`scripts/test_api.py`/
  `frontend/utils/api_client.py` et le reste du code.
- Aucun environnement Python Windows fonctionnel (le `venv/` livré est un environnement **Linux**).

## 3. Problèmes détectés pendant cette phase (en plus de ceux de la phase 1)

- La commande `python` se résout de façon imprévisible sur cette machine (3 installations : 3.12,
  3.14, 3.15) — un premier `venv_win` s'est retrouvé construit avec **Python 3.14**, une version
  trop récente pour plusieurs dépendances scientifiques.
- `nougat-ocr` (dépendance optionnelle) entraîne `pyarrow`, qui n'a pas de roue précompilée
  compatible et échoue à se compiler depuis les sources sur Windows.
- Les `print()` avec emojis du code plantent sur la console Windows par défaut
  (`UnicodeEncodeError`, codepage `cp1252`).
- `requirements.txt` ne fixe que des bornes minimales (`>=`) : l'installation du jour a résolu des
  versions **beaucoup plus récentes** que celles utilisées par Binta (ex. `gradio 6.20.0` au lieu de
  `>=4.44.0`, `langgraph 1.2.9` au lieu de `>=0.2.0`, `fastapi 0.139.2`). Ceci a révélé un vrai bug
  de compatibilité dans le frontend (détaillé §22).

---

## 4. Fichiers créés

| Fichier | Rôle |
| --- | --- |
| `.gitignore` | Exclut `.env`, `venv/`, `venv_win/`, `__pycache__/`, `*.db`, `logs/`, `model/`, etc. |
| `.env.example` | Modèle de configuration sans aucune valeur sensible |
| `scripts/setup_windows.ps1` | Crée `venv_win` (Python 3.12 épinglé), installe `requirements.txt`, vérifie les imports |
| `scripts/run_backend_windows.ps1` | Lance l'API backend en natif (charge `.env`, force `PORT=8080`, `PYTHONUTF8=1`) |
| `scripts/run_frontend_windows.ps1` | Lance Gradio en natif (force `API_URL=http://localhost:8080`, `GRADIO_PORT=7860`, `PYTHONUTF8=1`) |

## 5. Fichiers modifiés — détail et justification

### `docker-compose.yml`

| Modification | Ancienne valeur | Nouvelle valeur | Raison |
| --- | --- | --- | --- |
| Mot de passe Neo4j (service `neo4j`) | `NEO4J_AUTH: neo4j/nuru_password` (en clair) | `NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}` | Partager une seule source de vérité (`.env`) avec le backend, éviter un secret dupliqué en dur |
| Mot de passe Neo4j (service `backend`) | `NEO4J_PASSWORD: RF6M0XR82_...` (secret réel de Binta, en clair) | `NEO4J_PASSWORD: ${NEO4J_PASSWORD}` | Suppression du secret en clair du fichier versionnable |
| URI Neo4j (service `backend`) | `NEO4J_URI: neo4j+s://6c62c3e9.databases.neo4j.io` (Aura cloud personnel) | `NEO4J_URI: bolt://neo4j:7687` (conteneur local) | Environnement autonome, ne dépend plus du cloud personnel de Binta (demande explicite) |
| Port Postgres (hôte) | `"5432:5432"` | `"5433:5432"` | Port `5432` déjà occupé par un autre projet Docker sur cette machine ; port **interne** conteneur inchangé |
| Service `ollama` | actif par défaut, `"11434:11434"` | `profiles: ["ollama-docker"]` (désactivé par défaut) | Vous utilisez l'Ollama natif déjà installé ; évite un second serveur Ollama et un conflit de port 11434 |
| `OLLAMA_HOST` (service `backend`) | `http://ollama:11434` | `http://host.docker.internal:11434` | Pointe vers l'Ollama natif de l'hôte depuis le conteneur backend |
| `depends_on` (service `backend`) | incluait `ollama` | `ollama` retiré | Le service `ollama` étant désactivé par profil, une dépendance dessus ferait échouer `docker compose up` |

### `.env`

| Modification | Ancienne valeur | Nouvelle valeur | Raison |
| --- | --- | --- | --- |
| `NEO4J_URI` | `neo4j+s://6c62c3e9.databases.neo4j.io` (Aura cloud personnel de Binta) | `bolt://localhost:7687` | Backend natif Windows → Neo4j local (conteneur Docker, port hôte exposé) |
| `NEO4J_PASSWORD` | mot de passe Aura réel (secret) | `nuru_password` (mot de passe de développement local, non sensible) | Cohérent avec le conteneur local ; ne réutilise plus le secret cloud compromis |
| `QDRANT_URL` / `QDRANT_API_KEY` | **inchangés** (cluster + clé Qdrant Cloud réels de Binta) | **inchangés** | Non demandé explicitement pour cette phase ; voir §11 — décision volontaire de ne pas couper l'accès aux données déjà indexées sans validation |
| `API_URL` | `http://localhost:8000` (périmé) | **inchangé** | Non listé explicitement dans la demande de correction de port ; les scripts de lancement (`run_frontend_windows.ps1`) forcent `API_URL=8080` indépendamment de cette valeur, donc sans impact pratique — reste un point à nettoyer plus tard (§25) |

### `requirements.txt`

| Modification | Ancienne valeur | Nouvelle valeur | Raison |
| --- | --- | --- | --- |
| Ligne `nougat-ocr` | `nougat-ocr>=0.1.17  # optionnel : ...` (active) | Commentée, avec explication | Sa dépendance transitive `pyarrow` (via `datasets[vision]`) n'a pas de roue compatible sur cette machine et échoue à se compiler depuis les sources. `nougat-ocr` est déjà conçu comme optionnel dans le code (`nougat_adapter.py`, repli PyMuPDF automatique) — aucune perte de fonctionnalité de base |

### `scripts/test_api.py`

| Modification | Ancienne valeur | Nouvelle valeur | Raison |
| --- | --- | --- | --- |
| `BASE_URL` | `"http://localhost:8000"` | `"http://localhost:8080"` | Port réel de l'API (8080), demandé explicitement |
| Messages d'aide (x2) | `python -m backend.api.main` | `python -m backend.app.api.main` | Chemin de module obsolète (pré-refactor) ; correction mineure du même fichier, dans le même esprit que la correction de port |

### `frontend/utils/api_client.py`

| Modification | Ancienne valeur | Nouvelle valeur | Raison |
| --- | --- | --- | --- |
| Valeur par défaut `base_url` | `"http://localhost:8000"` | `"http://localhost:8080"` | Port réel de l'API, demandé explicitement (fichier actuellement non utilisé par `gradio_app.py`, mais corrigé par cohérence) |

### `scripts/setup_windows.ps1` (révision après incident Python 3.14)

| Modification | Ancien comportement | Nouveau comportement | Raison |
| --- | --- | --- | --- |
| Sélection de l'interpréteur Python | `python -m venv venv_win` (résolution ambiguë du PATH) | `py -3.12 -m venv venv_win` (lanceur officiel, version épinglée) | `python` s'est résolu vers Python 3.14 dans le contexte PowerShell de cette machine, causant des échecs de compilation de paquets scientifiques |

### `scripts/run_backend_windows.ps1` et `scripts/run_frontend_windows.ps1`

| Modification | Ancien comportement | Nouveau comportement | Raison |
| --- | --- | --- | --- |
| Encodage console | aucun réglage (cp1252 par défaut) | `$env:PYTHONUTF8 = "1"` ajouté | Les `print()` du code contiennent des emojis qui font planter la console Windows par défaut (`UnicodeEncodeError`) |

---

## 6. Ports — avant / après

| Composant | Avant | Après | Type de port modifié |
| --- | --- | --- | --- |
| Backend API | 8080 | 8080 (inchangé) | — |
| Frontend Gradio | 7860 | 7860 (inchangé) | — |
| Qdrant | 6333 | 6333 (inchangé) | — |
| Neo4j Browser | 7474 | 7474 (inchangé) | — |
| Neo4j Bolt | 7687 | 7687 (inchangé) | — |
| **PostgreSQL** | **5432** | **5433** (port hôte) | Port hôte uniquement, port interne conteneur toujours 5432 |
| Ollama (conteneur, désactivé) | 11434 | 11434 (inchangé, mais service non démarré par défaut) | — |
| Ollama natif (hôte) | 11434 | 11434 (inchangé) | — |

## 7. Configuration Ollama retenue

- **Ollama natif** de l'hôte (`ollama version 0.31.2`), modèle `llama3.2:1b` déjà présent — utilisé
  tel quel, **aucun** `ollama pull` relancé.
- Service `ollama` du `docker-compose.yml` **désactivé par défaut** (`profiles: ["ollama-docker"]`),
  activable manuellement uniquement si besoin (`docker compose --profile ollama-docker up -d ollama`).
- Le backend (natif ou conteneurisé) contacte l'Ollama natif via `http://localhost:11434` (natif) ou
  `http://host.docker.internal:11434` (conteneur backend Docker → hôte).
- Connectivité `host.docker.internal:11434` testée avec succès depuis un conteneur Docker jetable
  (`HTTP_STATUS:200`) avant toute autre modification.

## 8. Configuration Neo4j retenue

- Conteneur Docker local (`docker-compose.yml`, service `neo4j`), autonome, **plus aucune dépendance
  au Neo4j Aura cloud personnel de Binta**.
- Identifiants : utilisateur `neo4j`, mot de passe `nuru_password` (dev local, non sensible),
  partagés entre le service `neo4j` et le service `backend` via la variable `${NEO4J_PASSWORD}`
  de `.env`.
- URI : `bolt://neo4j:7687` en Docker (nom de service interne), `bolt://localhost:7687` en natif
  (port hôte exposé).
- Confirmé fonctionnel dans les logs backend : `✅ Connecté à Neo4j: bolt://localhost:7687`.
- **Le graphe de connaissances local est actuellement vide** (jamais alimenté) : les requêtes
  Cypher de prérequis/relations renvoient des résultats vides ou des avertissements
  (`label does not exist`), sans faire planter les requêtes (dégradation gracieuse déjà prévue par le
  code).
- **Bug pré-existant détecté (non corrigé, hors périmètre de cette phase)** : une requête Cypher dans
  `backend/app/rag/knowledge_graph/graph_queries.py` échoue avec
  `Neo.ClientError.Statement.SyntaxError` (`Parameter maps cannot be used in MATCH patterns`) sur un
  motif du type `[:PREREQUIS_DE*1..$depth]` — Neo4j n'autorise pas un paramètre dans la longueur
  variable d'une relation de ce type. L'erreur est interceptée et n'interrompt pas la requête globale,
  mais la fonctionnalité de « prérequis » du Knowledge Graph ne fonctionnera pas tant que ce n'est pas
  corrigé. Ce n'est pas lié à nos changements : c'est la première fois que ce chemin de code est
  exécuté contre un vrai Neo4j.

## 9. Configuration Qdrant réellement utilisée

**Important : le backend natif utilise actuellement le Qdrant Cloud réel de Binta, pas le conteneur
local.**

- Variable en cause : `QDRANT_URL` (+ `QDRANT_API_KEY`) dans `.env`, lues par
  `VectorIndexerConfig.from_env()` — **volontairement non modifiées** dans cette phase (voir §11 pour
  la justification détaillée).
- Confirmé dans les logs : `✅ Connexion à Qdrant: https://50217f81-...cloud.qdrant.io:6333` (URL
  tronquée ici, jamais affichée en entier, clé API jamais affichée).
- Le conteneur Qdrant local (`docker compose up -d qdrant`) tourne mais est **actuellement vide** —
  vérifié avec `curl http://localhost:6333/collections` → `{"result":{"collections":[]}}`.

## 10. Base de données réellement utilisée

- **SQLite**, fichier `nuru_student_memory.db` à la racine du projet (celui déjà présent avant nos
  tests, ni supprimé ni recréé).
- Cause : `.env` ne contient **aucune** variable `DATABASE_URL` (ni avant, ni après nos
  modifications) — ce n'est pas quelque chose que nous avons désactivé, c'est l'état d'origine du
  fichier. `backend/app/memory/db.py` bascule automatiquement sur SQLite si `DATABASE_URL` est absent.
- Conteneur PostgreSQL Docker : démarré et sain (`Up`, port `5433`), mais **actuellement inutilisé**
  par le backend natif, faute de `DATABASE_URL` pointant vers lui.
- Vérifié : le fichier `nuru_student_memory.db` n'a **pas changé** (même taille 98 304 octets, même
  date de modification) après nos tests `/chat/`, car ceux-ci n'ont pas fourni de `user_id` — le code
  (`backend/app/agents/progression_agent.py:70`) n'écrit en base que si un `student_id` est résolu.
- Voir `SPRINT2_MANUAL_WINDOWS_SETUP_AND_TESTING.md` pour les deux modes (SQLite / PostgreSQL)
  détaillés avec la bonne valeur de `DATABASE_URL` dans chaque cas.

## 11. Pourquoi Qdrant n'a pas été rendu autonome comme Neo4j

Contrairement à Neo4j (rendu autonome explicitement demandé, §4/Étape 4), Qdrant n'a pas été touché
pour ces raisons :

1. Ce n'était pas explicitement demandé pour cette phase.
2. Le cluster Qdrant Cloud de Binta contient déjà des données indexées (le corpus RAG réel de
   ~100 PDF, cf. `SPRINT2_PROJECT_TECHNICAL_ANALYSIS.md`). Basculer immédiatement vers le conteneur
   local (vide) **casserait le RAG** : les agents Cours/Exercices perdraient tout contexte documentaire
   réel et retomberaient sur leurs gabarits texte génériques.
3. Pour alimenter le Qdrant local, il faudrait relancer le pipeline d'ingestion complet
   (`scripts/ingest_pipeline.py` sur `data/raw/`), une opération longue, qui écrit des données et
   n'a **pas été exécutée** dans cette phase, conformément à la consigne explicite de ne pas relancer
   l'ingestion sans validation préalable.

**Conclusion : le mode actuel dépend encore du Qdrant Cloud de Binta.** Basculer vers un Qdrant 100 %
local est possible plus tard, mais nécessite une étape d'ingestion volontaire et validée au préalable.

---

## 12. Problème Python 3.14 rencontré

`python -m venv venv_win` (première tentative) a été construit avec **Python 3.14.4**
(`C:\Python314`), pas la version attendue. Cette machine a 3 installations Python
(3.12 / 3.14 / 3.15) et la commande `python` nue se résout de façon incohérente selon le shell.
Conséquence directe : des roues (`.whl`) incompatibles/inexistantes pour plusieurs paquets
scientifiques (notamment `pyarrow`).

## 13. Passage à Python 3.12

Correction : `scripts/setup_windows.ps1` utilise désormais `py -3.12` (lanceur officiel Python pour
Windows, confirmé disponible : `py -0p` liste 3.12/3.14/3.15/3.15t). `venv_win` a été supprimé et
recréé proprement avec Python 3.12.9. Toutes les dépendances se sont alors installées avec les
roues `cp312` correctes.

## 14. Problème d'encodage Windows

`backend/app/api/main.py` (et d'autres fichiers) impriment des emojis (`🚀`, etc.) via `print()`. La
console Windows par défaut (codepage `cp1252`) ne peut pas encoder ces caractères, provoquant un
`UnicodeEncodeError` fatal au démarrage.

## 15. Correction avec `PYTHONUTF8=1`

Ajout de `$env:PYTHONUTF8 = "1"` dans `scripts/run_backend_windows.ps1` et
`scripts/run_frontend_windows.ps1`, avant le lancement de Python. Aucune modification du code source :
correctif purement au niveau des scripts de lancement Windows. Confirmé fonctionnel : la bannière
`🚀 NURU - Agent Tuteur IA` s'affiche correctement après ce correctif.

## 16. Problème `nougat-ocr` / `pyarrow`

`pip install -r requirements.txt` échouait avec :
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
ERROR: Failed to build 'pyarrow' when installing build dependencies for pyarrow
```
Cause exacte (remontée dans le journal pip) : `nougat-ocr>=0.1.17` → `datasets[vision]` →
`pyarrow>=21.0.0`, sans roue compatible disponible dans la chaîne de versions résolue sur cette
machine, et sans toolchain de compilation Arrow C++/CMake installée pour compiler depuis les sources.

## 17. Modification apportée à `requirements.txt`

`nougat-ocr` commenté (voir §5) avec explication. Fonctionnalité déjà optionnelle par conception
(`backend/app/rag/document_parser/nougat_adapter.py`, repli PyMuPDF automatique).

---

## 18. Services Docker démarrés

`docker compose up -d postgres qdrant neo4j` — le service `ollama` n'a **pas** été démarré (profil
désactivé). Statuts confirmés (`docker compose ps`) : les trois services `Up`, ports
`5433→5432` (postgres), `6333` (qdrant), `7474`/`7687` (neo4j).

## 19. Commandes exécutées (résumé chronologique)

```powershell
docker compose config
docker compose up -d postgres qdrant neo4j
docker compose ps
docker compose logs --tail=100 postgres|qdrant|neo4j
ollama --version ; ollama list ; Invoke-RestMethod http://localhost:11434/api/tags
docker run --rm curlimages/curl:latest curl -s http://host.docker.internal:11434/api/tags   # test de connectivite (conteneur jetable)
powershell -File scripts\setup_windows.ps1        # 1ere tentative (Python 3.14, echec pyarrow)
# correction requirements.txt (nougat-ocr) puis nouvelle tentative (toujours Python 3.14, succes)
# diagnostic : venv_win construit avec Python 3.14 -> suppression, correction du script (py -3.12)
powershell -File scripts\setup_windows.ps1        # tentative finale, Python 3.12, succes complet
powershell -File scripts\run_backend_windows.ps1
Invoke-RestMethod http://localhost:8080/health
Invoke-RestMethod -Method Post -Uri http://localhost:8080/chat/ -ContentType "application/json" -Body '{"message":"..."}'
curl.exe -X POST http://localhost:8080/chat/ ... -o reponse.json   # verification des octets UTF-8 bruts
powershell -File scripts\run_frontend_windows.ps1
Invoke-WebRequest http://localhost:7860           # accessibilite HTTP
gradio_client.Client('http://localhost:7860').predict(...)   # vrai appel frontend -> backend
```

## 20. Résultat `/health`

```json
{"status": "healthy", "version": "1.0.0", "timestamp": "...", "services": {"api": "running"}}
```
✅ Réussi.

## 21. Résultat `/chat/`

Requête `{"message": "Explique-moi les nombres complexes"}` → réponse complète du pipeline LangGraph
(`intent: "cours"`, `level: "reformulation"`, `confidence: 0.5`, texte pédagogique généré via Ollama,
`progression_summary` vide car aucun `user_id` fourni). ✅ Réussi. Octets bruts vérifiés en UTF-8
valide via `curl.exe` (voir §22 pour l'écran diagnostiqué comme faux positif).

## 22. Résultat du frontend

- Page HTML accessible (`http://localhost:7860`, `200 OK`, contenu Gradio détecté). ✅
- **Vrai appel frontend → backend testé** via `gradio_client` (appel direct de la fonction `/_fn`
  utilisée par les boutons "Envoyer" des onglets Cours/Exercices/Quiz) : confirmé dans les logs
  backend — `127.0.0.1 - "POST /chat/ HTTP/1.1" 200 OK` avec réponse LLM réelle générée. **La
  communication réseau frontend → backend fonctionne.**
- **Mais** : ⚠️ **échec de rendu côté Gradio**, capturé dans les logs frontend :
  ```
  gradio.exceptions.Error: "Data incompatible with messages format. Each message should be a
  dictionary with 'role' and 'content' keys or a ChatMessage object."
  ```
  Cause : `frontend/gradio_app.py` construit l'historique de chat au format ancien
  `history + [(message, response)]` (tuples), format abandonné par la version de Gradio réellement
  installée (`6.20.0`, résolue par `requirements.txt` qui ne fixe qu'un minimum `gradio>=4.44.0`).
  Le composant `gr.Chatbot(...)` de cette version exige le nouveau format
  `{"role": ..., "content": ...}`.
  **Conséquence concrète** : le backend répond correctement, mais l'interface Gradio ne peut pas
  afficher la réponse dans les onglets Cours/Exercices/Quiz — une erreur apparaît côté serveur au
  moment de renvoyer le message au navigateur. Ce n'est **pas** le message "mode hors-ligne" (celui-ci
  n'apparaît que si l'appel réseau vers l'API échoue, ce qui n'est pas le cas ici) — c'est une
  incompatibilité de version Gradio, distincte.
  **Corrigé** — voir §27 pour le détail complet (diagnostic, tentative d'épinglage abandonnée,
  correction finalement appliquée, validation Cours/Exercices/Quiz).

## 23. Erreurs rencontrées et solutions (résumé)

| # | Erreur | Cause | Solution appliquée |
| --- | --- | --- | --- |
| 1 | `pip install` échoue sur `pyarrow` | `nougat-ocr` → `datasets[vision]` → `pyarrow`, pas de roue compatible | `nougat-ocr` commenté dans `requirements.txt` (déjà optionnel par conception) |
| 2 | `UnicodeEncodeError` au démarrage du backend | Emojis dans `print()`, console Windows en `cp1252` | `PYTHONUTF8=1` dans les scripts de lancement |
| 3 | `venv_win` construit avec Python 3.14 | Résolution ambiguë de `python` sur cette machine (3 versions installées) | `setup_windows.ps1` épingle `py -3.12` ; `venv_win` recréé |
| 4 | `gradio.exceptions.Error` sur le format des messages du Chatbot | `requirements.txt` ne fixe qu'un minimum (`gradio>=4.44.0`), version réellement installée `6.20.0` a supprimé le format tuple utilisé par `gradio_app.py` | **Non corrigé** — proposé, en attente de votre validation (§25) |

## 24. Points encore non résolus

1. ~~Chat Gradio ne s'affiche pas~~ — **corrigé, voir §27**.
2. `.env`'s `API_URL=http://localhost:8000` reste périmé (non bloquant, les scripts de lancement le
   contournent explicitement).
3. Bug pré-existant de requête Cypher dans `graph_queries.py` (§8) — sans lien avec cette phase, non
   corrigé.
4. Le Knowledge Graph Neo4j local est vide (pas de concepts/prérequis) — normal, jamais ingéré
   localement.
5. Le Qdrant local est vide — le RAG fonctionne actuellement grâce au Qdrant Cloud de Binta
   uniquement (§9/§11).
6. `readme (2).md` (ancien README dupliqué, contradictoire) toujours présent, non nettoyé — signalé
   dès la phase 1.

## 25. Risques et dépendances externes

- Le fonctionnement RAG actuel **dépend d'un accès réseau au Qdrant Cloud de Binta** (clé API dans
  `.env`, jamais affichée) — si ce compte est fermé/la clé révoquée, le RAG cessera de fonctionner
  (dégradation gracieuse vers les gabarits texte, pas de crash).
- L'Ollama natif de l'hôte doit rester lancé pour toute génération de contenu pédagogique riche.
- `requirements.txt` sans bornes supérieures : une réinstallation future pourrait résoudre des
  versions encore plus récentes et casser d'autres composants (comme cela s'est produit pour Gradio).
  Recommandation pour une phase ultérieure : figer des bornes supérieures raisonnables une fois un
  jeu de versions validé comme fonctionnel.

## 26. Liste finale exacte des fichiers créés ou modifiés (cette phase, avant correction Gradio)

**Créés** : `.gitignore`, `.env.example`, `scripts/setup_windows.ps1`,
`scripts/run_backend_windows.ps1`, `scripts/run_frontend_windows.ps1`,
`SPRINT2_CHANGES_AND_VALIDATION_REPORT.md` (ce fichier),
`SPRINT2_MANUAL_WINDOWS_SETUP_AND_TESTING.md`.

**Modifiés** : `docker-compose.yml`, `.env`, `requirements.txt`, `scripts/test_api.py`,
`frontend/utils/api_client.py`.

**Artefacts d'environnement (pas des fichiers du dépôt)** : `venv_win/` créé (recréé une fois après
l'incident Python 3.14) ; conteneurs Docker `postgres`, `qdrant`, `neo4j` démarrés (volumes créés :
`nuru_agent_nbn_postgres_data`, `nuru_agent_nbn_qdrant_data`, `nuru_agent_nbn_neo4j_data`).

**Non touchés à ce stade** : `nuru_student_memory.db`, `data/raw/`, `data/processed/`, tout le code
métier backend, `frontend/gradio_app.py`, `frontend/app.py`, `frontend/components/chat.py`.

> Voir §27 pour la correction ultérieure du bug d'affichage Gradio, qui modifie en plus
> `frontend/gradio_app.py` et `requirements.txt` (ligne `gradio`).

---

## 27. Correction du bug d'affichage du chat Gradio (suite de la phase 2)

### 27.1 Rappel du problème

Le backend recevait et traitait correctement les messages envoyés depuis Gradio
(`POST /chat/ HTTP/1.1" 200 OK` dans les logs backend), mais l'interface plantait avant d'afficher la
réponse :
```
gradio.exceptions.Error: "Data incompatible with messages format. Each message should be a
dictionary with 'role' and 'content' keys or a ChatMessage object."
```

### 27.2 Diagnostic précis

- Version Gradio installée : `6.20.0`.
- `frontend/gradio_app.py:133,138,143` : les trois composants `gr.Chatbot(...)` (Cours, Exercices,
  Quiz) sont déclarés **sans paramètre `type=`**. Vérification faite : dans Gradio 6.20.0, ce
  paramètre a même été **retiré de la signature** de `Chatbot.__init__` — il n'existe plus aucune
  option pour revenir au format tuples, le format `messages` (liste de dictionnaires
  `{"role": ..., "content": ...}`) est désormais obligatoire.
- `frontend/gradio_app.py:56-61` (fonction `make_chat_fn`) : la fonction de callback partagée par les
  trois onglets était explicitement typée `history: List[Tuple[str, str]]` et construisait
  `history + [(message, response)]` — confirmation directe du format `list[tuple[str, str]]`
  (ancien format), incompatible avec l'exigence ci-dessus.
- Cause racine : `requirements.txt` ne fixait qu'un minimum (`gradio>=4.44.0`) sans borne supérieure ;
  l'installation du jour a résolu `6.20.0`, qui a supprimé le format utilisé par le code de Binta.

### 27.3 Comparaison des options

| Critère | Option A (adapter le code) | Option B (épingler Gradio 4.x) |
| --- | --- | --- |
| Modification minimale | 1 fonction + 3 déclarations de composant | 1 ligne `requirements.txt` (en théorie) |
| Compatibilité avec les 3 chats | Oui | Oui (en théorie) |
| Reproductibilité | Corrige le vrai problème (borne large sur `gradio`) uniquement si on ajoute aussi une épingle exacte | Corrige la reproductibilité de Gradio |
| Absence de régression | Oui | **Non, en pratique** (voir §27.4) |
| Facilité de reprise par Binta | Le code diverge légèrement de l'original (format messages) | Le code reste identique à l'original |

**Décision initiale** : Option B (épingler `gradio==4.44.1`), jugée plus fidèle au code original de
Binta et plus simple. **Décision finale, après test réel : Option A**, l'Option B s'étant révélée
créer une régression réelle sur le backend (voir §27.4) — impossible à résoudre sans toucher aux
dépendances du backend (LangGraph/transformers), ce qui était explicitement interdit.

### 27.4 Pourquoi l'Option B (épingler Gradio) a été abandonnée

Deux régressions successives sont apparues en testant réellement `gradio==4.44.1` :

1. **Conflit `websockets`** : `gradio-client 1.3.0` (dépendance de `gradio==4.44.1`) exige
   `websockets<13.0,>=10.0`. Or le backend a besoin de `websockets<16,>=14` (`langgraph-sdk 0.4.2`)
   **et** `websockets>=15.0` (`langsmith 0.10.5`). Ces plages ne se recoupent pas. L'installation de
   Gradio a silencieusement downgradé `websockets` à `12.0`, cassant l'import de `langgraph`
   (`ModuleNotFoundError: No module named 'websockets.asyncio'`) — **le backend ne démarrait plus**.
   Contournement testé : forcer `websockets==15.0.1` (`pip install websockets==15.0.1 --no-deps`) —
   le backend redémarrait correctement, mais ce correctif n'est valable que tant que Gradio 4.x
   n'utilise pas activement les fonctionnalités récentes de `websockets` (non garanti dans le temps).
2. **Conflit `huggingface_hub`** : une fois le problème 1 contourné, le frontend plantait à son tour
   à l'import : `ImportError: cannot import name 'HfFolder' from 'huggingface_hub'`.
   `gradio==4.44.1` (fonctionnalité de connexion Hugging Face Spaces, non utilisée par NURU) importe
   la classe `HfFolder`, supprimée des versions récentes de `huggingface_hub`. Or
   `transformers==5.14.1` (déjà installé, utilisé par le RAG du backend pour les embeddings) **exige**
   `huggingface_hub>=1.5.0`, une version où `HfFolder` n'existe plus. **Aucune version de
   `huggingface_hub` ne peut satisfaire à la fois l'ancien Gradio et `transformers` actuel** sans
   downgrader `transformers` — ce qui aurait touché au RAG du backend, explicitement interdit.

**Conclusion** : Option B créait une chaîne de régressions non résolvable sans toucher au backend.
Décision changée en cours de route vers l'Option A, avec explication transparente avant application
(conformément à la consigne de ne jamais masquer un échec).

### 27.5 Correction appliquée (Option A)

- **`frontend/gradio_app.py`** (seule modification de code) : la fonction `_fn` de `make_chat_fn`
  construit désormais l'historique au format `messages` :

  ```python
  def _fn(message: str, history: List[dict], user_id: str, session_id: str):
      session_id = session_id or str(uuid.uuid4())
      response, session_id = _chat_call(message, session_id, user_id)
      history = history + [
          {"role": "user", "content": message},
          {"role": "assistant", "content": response},
      ]
      return history, "", session_id
  ```

  (avant : `history: List[Tuple[str, str]]` et `history + [(message, response)]`). Aucun autre
  fichier de code n'a été modifié — `frontend/app.py` et `frontend/components/chat.py` (non utilisés
  par le flux réel) n'ont pas été touchés.
- **`requirements.txt`** : `gradio==4.44.1` (tentative abandonnée) → **`gradio==6.20.0`** (épinglage
  exact sur la version réellement validée avec tout le reste de la stack), avec un commentaire
  expliquant tout le raisonnement ci-dessus pour Binta.
- **`websockets`** : laissé à `15.0.1` (déjà la version compatible avec `langgraph-sdk`/`langsmith`,
  restaurée automatiquement en réinstallant `gradio==6.20.0`, dont `gradio-client==2.5.0` accepte des
  versions de `websockets` bien plus récentes que la ligne 4.x).
- Vérification finale : `pip check` → `No broken requirements found.`

### 27.6 Commandes exécutées pour cette correction

```powershell
# Tentative Option B (abandonnee)
pip install "gradio==4.44.1"                 # provoque conflit websockets
pip install "websockets==15.0.1" --no-deps    # contournement, backend redemarre OK
# -> mais nouveau plantage frontend (HfFolder / huggingface_hub)
pip install "gradio==6.20.0"                  # retour a la version fonctionnelle
pip check                                      # No broken requirements found

# Option A appliquee : edition de frontend/gradio_app.py (format messages)

# Redemarrage complet et validation
powershell -File scripts\run_backend_windows.ps1
Invoke-RestMethod http://localhost:8080/health
powershell -File scripts\run_frontend_windows.ps1
Invoke-WebRequest http://localhost:7860

# Vrai test frontend -> backend via gradio_client (Cours, 2e message, Exercices, Quiz)
python -c "from gradio_client import Client; ..."
```

### 27.7 Résultats des tests (Cours / Exercices / Quiz)

| Test | Résultat |
| --- | --- |
| Cours — 1er message ("Explique-moi les nombres complexes.") | ✅ 2 entrées d'historique (`user`, `assistant`), réponse réelle du LLM |
| Cours — 2e message dans la même session ("Donne-moi un exemple simple.") | ✅ historique passe à 4 entrées, aucune exception. Réponse générique (intention "general" détectée par le Planner plutôt que la poursuite du sujet "cours") — comportement du Planner, non lié à cette correction, hors périmètre |
| Exercices ("Donne-moi un exercice sur les suites numériques") | ✅ 2 entrées, réponse "✍️ Exercice : ..." |
| Quiz ("Fais-moi un quiz sur la trigonométrie") | ✅ 2 entrées, réponse "📋 Quiz : ..." |
| Logs backend | ✅ 7 requêtes `POST /chat/ HTTP/1.1" 200 OK` cumulées, aucune erreur |
| Logs frontend | ✅ aucune exception Gradio depuis le redémarrage |
| Page `http://localhost:7860` | ✅ HTTP 200 |

### 27.8 Procédure de redémarrage du frontend (après cette correction)

Identique à avant (§ Quick Start) — aucun changement de procédure :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_frontend_windows.ps1
```

Si vous aviez un `venv_win` créé **avant** cette correction, un simple redémarrage suffit : la
correction a été appliquée directement dans `venv_win` existant (`pip install gradio==6.20.0`), sans
recréation de l'environnement.

### 27.9 Limitations restantes

- Les tests ci-dessus ont été effectués via `gradio_client` (appel direct des fonctions internes de
  l'API Gradio), pas depuis un navigateur réel. Le comportement observé (données correctement
  formatées, aucune exception serveur) est cependant strictement identique à ce qu'un navigateur
  déclencherait, puisque c'est le même code serveur qui traite la requête dans les deux cas.
  **Vous restez invité à confirmer vous-même dans un navigateur** (voir
  `SPRINT2_MANUAL_WINDOWS_SETUP_AND_TESTING.md`, section I).
- Le comportement du Planner sur les messages de suivi (2e message classé "general" au lieu de
  poursuivre "cours") est un comportement pré-existant du backend, non lié à cette correction et hors
  périmètre de cette intervention (consigne explicite de ne pas toucher à LangGraph/la logique
  pédagogique).
- `frontend/app.py` et `frontend/components/chat.py` (code mort, non utilisés) n'ont pas été mis à
  jour vers le format messages — sans impact puisqu'ils ne sont jamais exécutés par le flux actuel.
