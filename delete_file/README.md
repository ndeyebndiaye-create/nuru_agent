# Fichiers mis à l'écart lors de l'audit final

Ce dossier est une zone de quarantaine réversible. Aucun élément n'a été supprimé :
chaque fichier conserve ici son chemin relatif d'origine.

## Anciens points d'entrée et composants frontend

| Emplacement original | Raison | Sort final conseillé |
|---|---|---|
| `frontend/app.py` | Ancienne interface Flask, remplacée par `frontend/gradio_app.py` et non référencée par le lancement actif. | Suppression définitive possible après la démonstration. |
| `frontend/components/chat.py` | Ancien composant Gradio au format historique, non utilisé par l'interface active. | Suppression définitive possible. |
| `frontend/utils/api_client.py` | Client utilisé uniquement par l'ancien composant; contient en plus une route `/chat/search` absente du backend actuel. | Suppression définitive possible. |

## Scripts anciens ou trompeurs

| Emplacement original | Raison | Sort final conseillé |
|---|---|---|
| `get-docker.sh` | Copie du script tiers d'installation Docker pour Linux, sans lien avec la procédure Windows du projet. | Suppression définitive possible. |
| `scripts/ingest_to_qdrant.py` | Ancien pipeline parallèle en mémoire, non référencé et utilisant `LiteEmbedder`, qui n'existe plus. | Suppression définitive possible. |
| `scripts/run_all_tests.py` | Lance d'anciens scripts manuels au lieu de la suite maintenue `pytest tests/`. | Suppression définitive possible. |
| `scripts/test_agents.py` | Ancien menu interactif couvert par les tests automatisés actuels et susceptible de solliciter le runtime réel. | Conserver temporairement comme archive, puis supprimer si aucun besoin pédagogique. |
| `scripts/test_api.py` | Test manuel ancien contenant l'endpoint inexistant `/chat/search`. | Suppression définitive possible. |
| `scripts/test_ingest.py` | Script nommé « test » mais lançant une ingestion réelle de PDF; doublon dangereux du pipeline officiel. | Suppression définitive recommandée. |
| `backend/tests/test_document_parser.py` | Ancien test manuel hors de `tests/`, écrit dans les données traitées et duplique les tests maintenus. | Suppression définitive possible. |
| `backend/app/rag/chunker/tests/test_chunker.py` | Démonstration historique en doublon avec les tests unitaires et `scripts/test_chunker.py`. | Suppression définitive possible. |

## Copies, résultats et logs générés

| Emplacement original | Raison | Sort final conseillé |
|---|---|---|
| `readme (2).md` | Ancienne copie de README contenant des points d'entrée obsolètes. | Suppression définitive possible; le README racine est la source de vérité. |
| `cours_test_result.json` | Résultat généré par un ancien test manuel. | Suppression définitive possible. |
| `data/ingestion_logs/pipeline.log` | Log d'ingestion généré, non nécessaire à l'exécution et volumineux. | Suppression définitive possible après archivage externe si une trace détaillée est souhaitée. |

## Caches techniques

Les chemins suivants ont été déplacés en conservant leur arborescence :

- `.pytest_cache/` ;
- tous les dossiers `__pycache__/` situés sous `backend/`, `frontend/`,
  `scripts/` et `tests/`, hors environnements virtuels.

Ces caches sont entièrement régénérables et peuvent être supprimés définitivement.
Ils ne doivent jamais être restaurés dans le dépôt.

## Éléments volontairement non déplacés

- les rapports Sprint 2, changelogs, revue Claude et plan Neo4j : archives importantes ;
- `.env` et `nuru_student_memory.db` : configuration locale et mémoire applicative ;
- `data/raw/` et `data/processed/` : documents et résultats d'ingestion ;
- `model/` : données locales du modèle Ollama ;
- `venv/` et `venv_win/` : environnements nécessaires aux usages locaux actuels ;
- les tests sous `tests/` : suite automatisée de référence.
