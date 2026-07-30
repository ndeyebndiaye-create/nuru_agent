# Suivi après stabilisation

## Terminé

- [x] Supprimer complètement Neo4j du runtime, de l'ingestion et de l'infrastructure déclarée.
- [x] Nettoyer Docker Compose, `requirements.txt` et les variables d'environnement.
- [x] Valider le Retriever avec Qdrant uniquement.
- [x] Corriger la cohérence entre l'option correcte, la réponse élève et l'explication du quiz.
- [x] Corriger les filtres Qdrant `classe` et `serie` et créer les index payload requis.
- [x] Exécuter la validation automatisée et fonctionnelle finale.
- [x] Corriger la copie Docker obsolète du dossier `config/` absent.
- [x] Archiver les anciens scripts, interfaces, caches et logs dans `delete_file/`.

## Restant / évolutions futures

- [ ] Valider une ingestion complète optimisée lors d'une campagne dédiée.
- [ ] Corriger le découpage des chunks longs et la gestion des checkpoints/UUID.
- [ ] Améliorer les prompts pédagogiques et le Verifier.
- [ ] Évaluer un modèle LLM plus robuste que `llama3.2:1b`.
- [ ] Réduire la latence des réponses RAG et des générations.
- [ ] Exécuter et valider le build Docker complet lors d'une campagne dédiée.
