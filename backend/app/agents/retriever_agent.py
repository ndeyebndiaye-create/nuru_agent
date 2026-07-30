# backend/app/agents/retriever_agent.py
"""
Agent Retriever - récupère dans Qdrant le contexte documentaire nécessaire
avant toute génération par les autres agents.

Conformément au cahier des charges : toute question de cours/exercice
doit obligatoirement récupérer notion, méthode, exercice similaire et
correction de référence avant que le LLM ne réponde.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .config import AgentConfig

logger = logging.getLogger(__name__)


class RetrieverAgent:
    """Agent spécialisé dans la recherche documentaire et graphe."""

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        retriever: Optional[Any] = None,
    ):
        self.config = config or AgentConfig()
        self._retriever = retriever

    def _get_retriever(self):
        if self._retriever is not None:
            return self._retriever
        try:
            from backend.app.rag.vector_indexer import HybridRetriever, VectorIndexerConfig

            self._retriever = HybridRetriever(VectorIndexerConfig.from_env())
        except Exception as exc:  # noqa: BLE001
            logger.warning("⚠️ Retriever Qdrant indisponible: %s", exc)
            self._retriever = None
        return self._retriever

    def retrieve(
        self,
        query: str,
        concept: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Récupère le contexte documentaire depuis Qdrant en priorisant les cours.

        Retourne toujours une structure exploitable avec identification claire
        des documents de cours vs compléments (TD).
        """
        course_docs: List[Dict[str, Any]] = []
        supplement_docs: List[Dict[str, Any]] = []

        retriever = self._get_retriever()
        if retriever is not None:
            filters = filters or {"classe": "Terminale"}
            try:
                if hasattr(retriever, "search_course_first"):
                    res = retriever.search_course_first(query, filters=filters, top_k=top_k, supplement_quota=2)
                    course_docs = res.get("course_docs", [])
                    supplement_docs = res.get("supplement_docs", [])
                elif hasattr(retriever, "search_by_metadata"):
                    docs = retriever.search_by_metadata(query, filters, top_k=top_k)
                    course_docs = [d for d in docs if d.get("metadata", {}).get("doc_category") == "course"]
                    supplement_docs = [d for d in docs if d.get("metadata", {}).get("doc_category") != "course"]
                else:
                    docs = retriever.search(query, top_k=top_k)
                    course_docs = [d for d in docs if d.get("metadata", {}).get("doc_category") == "course"]
                    supplement_docs = [d for d in docs if d.get("metadata", {}).get("doc_category") != "course"]
            except Exception as exc:  # noqa: BLE001
                logger.error("❌ Erreur recherche Qdrant filtrée: %s", exc)

            if not course_docs and not supplement_docs:
                try:
                    if hasattr(retriever, "search_course_first"):
                        res = retriever.search_course_first(query, filters=None, top_k=top_k, supplement_quota=2)
                        course_docs = res.get("course_docs", [])
                        supplement_docs = res.get("supplement_docs", [])
                    else:
                        docs = retriever.search(query, top_k=top_k)
                        course_docs = [d for d in docs if d.get("metadata", {}).get("doc_category") == "course"]
                        supplement_docs = [d for d in docs if d.get("metadata", {}).get("doc_category") != "course"]
                except Exception as exc:  # noqa: BLE001
                    logger.error("❌ Erreur recherche Qdrant non filtrée: %s", exc)

        all_docs = course_docs + supplement_docs

        return {
            "type": "retrieval",
            "query": query,
            "concept": concept,
            "documents": all_docs,
            "course_docs": course_docs,
            "supplement_docs": supplement_docs,
            "has_course": bool(course_docs),
            "has_context": bool(all_docs),
        }

    def build_prompt_context(self, retrieval_result: Dict[str, Any], max_chars: int = 8000) -> str:
        """Construit un bloc de texte de contexte structuré à injecter dans le prompt LLM."""
        parts: List[str] = []

        course_docs = retrieval_result.get("course_docs", [])
        supplement_docs = retrieval_result.get("supplement_docs", [])

        if course_docs:
            parts.append("=== DOCUMENTS DE COURS PRINCIPAUX ===")
            for i, doc in enumerate(course_docs, 1):
                text = doc.get("text", "").strip()
                if not text:
                    continue
                meta = doc.get("metadata", {})
                chapitre = meta.get("chapitre", "")
                source = meta.get("source", meta.get("filename", ""))
                score = doc.get("score", 0.0)
                header = f"[COURS {i} | {chapitre or 'Général'}{' | ' + source if source else ''} | score={score:.2f}]"
                parts.append(f"{header}\n{text}")

        if supplement_docs:
            parts.append("=== COMPLÉMENTS ET TD (EXERCICES / EXEMPLES SEULEMENT) ===")
            for i, doc in enumerate(supplement_docs, 1):
                text = doc.get("text", "").strip()
                if not text:
                    continue
                meta = doc.get("metadata", {})
                chapitre = meta.get("chapitre", "")
                source = meta.get("source", meta.get("filename", ""))
                header = f"[TD/EXERCICE {i} | {chapitre or 'Général'}{' | ' + source if source else ''}]"
                parts.append(f"{header}\n{text}")

        full_context = "\n\n".join(parts)
        return full_context[:max_chars]
