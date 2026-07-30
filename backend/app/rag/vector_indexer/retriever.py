# backend/rag/vector_indexer/retriever.py
"""
Retriever avec recherche hybride et priorisation des documents de cours.

Stratégie :
  1. Rechercher d'abord parmi les documents typés "cours", "chapitre", "lecon".
  2. Si trop peu de résultats, compléter avec d'autres types (TD, exercices…).
  3. Appliquer un reranking qui booste les documents de cours et pénalise les
     fascicules de TD, afin que les cours restent toujours en tête.
"""
from typing import List, Dict, Any, Optional
import logging
import numpy as np

from .config import VectorIndexerConfig
from .qdrant_client import QdrantClientWrapper
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

# Types de documents considérés comme "cours principal"
COURSE_DOC_TYPES = {
    "cours", "course", "chapitre", "chapter", "lecon", "leçon",
    "lesson", "concept", "definition", "theoreme",
}

# Types considérés comme "compléments" (TD, exercices, etc.)
SUPPLEMENT_DOC_TYPES = {
    "exercise", "exercice", "td", "tp", "exercices", "travaux_diriges",
    "solution", "corrige", "assessment", "exam", "practical", "problem",
}

# Bonus de score appliqué aux documents de cours lors du reranking
COURSE_PRIORITY_BONUS = 0.25


def _classify_doc_type(payload: Dict[str, Any]) -> str:
    """Retourne la catégorie normalisée du document ('course', 'supplement', 'unknown')."""
    raw = (
        payload.get("chunk_type")
        or payload.get("type_document")
        or payload.get("chunk_category")
        or payload.get("type")
        or ""
    ).lower().strip()

    # Normalisation partielle : "td_integrale" → "td"
    for supplement_key in SUPPLEMENT_DOC_TYPES:
        if supplement_key in raw:
            return "supplement"
    for course_key in COURSE_DOC_TYPES:
        if course_key in raw:
            return "course"
    return "unknown"


class HybridRetriever:
    """
    Retriever hybride (dense + sparse/TF-IDF) avec priorisation des cours.
    """

    def __init__(self, config: Optional[VectorIndexerConfig] = None):
        self.config = config or VectorIndexerConfig.from_env()
        self.client_wrapper = QdrantClientWrapper(self.config)
        self.embedder = self.client_wrapper.embedder
        self.bm25_enabled = self.config.use_hybrid_search

    # ------------------------------------------------------------------ public

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Recherche hybride avec reranking priorisant fortement les cours."""
        top_k = top_k or self.config.top_k

        query_vector = self.embedder.encode_query(query)

        # Récupérer plus de candidats pour avoir une bonne marge de reranking.
        dense_results = self.client_wrapper.search(
            query_vector,
            limit=top_k * 4,
            filter_conditions=filters,
        )

        if not dense_results:
            return []

        # Reranking hybride (TF-IDF + bonus cours)
        results = self._hybrid_rerank(query, dense_results, len(dense_results))

        # Trier en mettant en tête tous les documents de type cours
        course_results = [r for r in results if _classify_doc_type(r.get("payload", {})) == "course"]
        supplement_results = [r for r in results if _classify_doc_type(r.get("payload", {})) != "course"]

        # Combiner : d'abord les cours, puis les compléments (TD, exercices)
        ordered_results = course_results + supplement_results
        return self._format_results(ordered_results[:top_k])

    def search_by_metadata(
        self,
        query: str,
        metadata_filters: Dict[str, Any],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Recherche avec filtres metadata, reranking cours inclus."""
        return self.search(query, top_k, filters=metadata_filters)

    def search_course_first(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        supplement_quota: int = 2,
    ) -> Dict[str, Any]:
        """
        Recherche à deux niveaux :
          - Priorité 1 : documents de type cours/chapitre/leçon.
          - Priorité 2 (quota) : TD/exercices utilisés uniquement comme
            compléments d'exemples et d'exercices.

        Retourne un dict avec :
          - 'course_docs'     : documents de cours triés par pertinence
          - 'supplement_docs' : documents complémentaires (TD, exercices)
          - 'has_course'      : True si au moins un doc de cours trouvé
        """
        top_k = top_k or self.config.top_k
        query_vector = self.embedder.encode_query(query)

        # Récupérer un grand ensemble de candidats
        candidates = self.client_wrapper.search(
            query_vector,
            limit=top_k * 4,
            filter_conditions=filters,
        )

        if not candidates:
            return {"course_docs": [], "supplement_docs": [], "has_course": False}

        # Reranker sur tout le pool
        reranked = self._hybrid_rerank(query, candidates, len(candidates))

        # Séparer cours et compléments
        course_docs = []
        supplement_docs = []

        for r in reranked:
            cat = _classify_doc_type(r.get("payload", {}))
            if cat == "course":
                course_docs.append(r)
            else:
                supplement_docs.append(r)

        # Tronquer selon les quotas
        course_docs = course_docs[:top_k]
        supplement_docs = supplement_docs[:supplement_quota]

        formatted_courses = self._format_results(course_docs)
        formatted_supplements = self._format_results(supplement_docs)

        return {
            "course_docs": formatted_courses,
            "supplement_docs": formatted_supplements,
            "has_course": bool(formatted_courses),
        }

    # --------------------------------------------------------------- internal

    def _hybrid_rerank(
        self,
        query: str,
        dense_results: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Reranking combinant score dense, TF-IDF sparse et bonus de type document.

        Score final = dense_weight * dense_score
                    + bm25_weight * tfidf_score
                    + COURSE_PRIORITY_BONUS  (si document de cours)
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            texts = [r.get("payload", {}).get("text", "") for r in dense_results]
            if not any(texts):
                return self._apply_course_bonus(dense_results)[:top_k]

            vectorizer = TfidfVectorizer(max_features=5000)
            tfidf_matrix = vectorizer.fit_transform(texts)
            query_tfidf = vectorizer.transform([query])
            bm25_scores = cosine_similarity(query_tfidf, tfidf_matrix).flatten()

            for i, result in enumerate(dense_results):
                dense_score = result.get("score", 0.0)
                bm25_score = float(bm25_scores[i]) if i < len(bm25_scores) else 0.0
                doc_bonus = (
                    COURSE_PRIORITY_BONUS
                    if _classify_doc_type(result.get("payload", {})) == "course"
                    else 0.0
                )
                result["score"] = (
                    self.config.dense_weight * dense_score
                    + self.config.bm25_weight * bm25_score
                    + doc_bonus
                )

        except ImportError:
            logger.warning("⚠️ sklearn non installé, application du bonus cours seul")
            dense_results = self._apply_course_bonus(dense_results)

        dense_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return dense_results[:top_k]

    def _apply_course_bonus(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applique uniquement le bonus de type cours (sans TF-IDF)."""
        for r in results:
            if _classify_doc_type(r.get("payload", {})) == "course":
                r["score"] = r.get("score", 0.0) + COURSE_PRIORITY_BONUS
        return results

    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formate les résultats Qdrant en dicts exploitables par les agents."""
        formatted = []
        for result in results:
            payload = result.get("payload", {})
            doc_type = (
                payload.get("chunk_type")
                or payload.get("type_document")
                or payload.get("type")
                or "inconnu"
            )
            metadata = {k: v for k, v in payload.items() if k != "text"}
            metadata["type"] = doc_type
            metadata["doc_category"] = _classify_doc_type(payload)
            formatted.append({
                "id": result.get("id"),
                "score": result.get("score", 0.0),
                "text": payload.get("text", ""),
                "metadata": metadata,
            })
        return formatted

    # --------------------------------------------------------- legacy aliases

    def search_by_chapitre(
        self, query: str, chapitre: str, top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return self.search(query, top_k, filters={"chapitre": chapitre})

    def search_by_classe(
        self, query: str, classe: str, serie: Optional[str] = None, top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        filters: Dict[str, Any] = {"classe": classe}
        if serie:
            filters["serie"] = serie
        return self.search(query, top_k, filters=filters)