# backend/agents/cours_agent.py
"""
Agent Cours — rédige un chapitre de manuel scolaire à partir du contexte RAG.

Règles absolues :
  • Le LLM ne reformule QUE le contenu présent dans le contexte RAG.
  • Si aucun document de cours n'est trouvé, l'agent le signale sans inventer.
  • Les formules doivent utiliser la syntaxe MathJax / KaTeX ($, $$).
  • Aucun template, aucun placeholder, aucune section vide.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .config import AgentConfig
from .state import AgentState
from .llm_utils import generate_pedagogical_text

logger = logging.getLogger(__name__)


class CoursAgent:
    """
    Agent spécialisé dans la rédaction de cours pédagogiques sous forme de
    chapitre de manuel scolaire (Programme Sénégalais Terminale S1/S2).
    Toute génération est ancrée sur les documents RAG récupérés par le Retriever.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()

    # ------------------------------------------------------------------ public

    def explain(self, state: AgentState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un cours complet fondé sur le contexte RAG.

        Args:
            state:   État courant (niveau d'aide, etc.)
            context: Résultats du Retriever + paramètres de la requête.

        Returns:
            Dict contenant l'explication rédigée, les sources et les métadonnées.
        """
        concept = context.get("concept") or "ce concept"
        level = getattr(state, "current_level", "reformulation")

        # ── Documents RAG ──────────────────────────────────────────────────
        course_docs: List[Dict[str, Any]] = context.get("course_docs", [])
        supplement_docs: List[Dict[str, Any]] = context.get("supplement_docs", [])
        retrieved_docs: List[Dict[str, Any]] = context.get("retrieved_docs", [])
        prompt_context: str = context.get("prompt_context", "")
        math_tool_result = context.get("math_tool_result")

        # Si course_docs vide, tenter de les extraire de retrieved_docs
        if not course_docs and retrieved_docs:
            try:
                from ..rag.vector_indexer.retriever import _classify_doc_type
                course_docs = [d for d in retrieved_docs if _classify_doc_type(d.get("metadata", {})) == "course"]
                supplement_docs = [d for d in retrieved_docs if _classify_doc_type(d.get("metadata", {})) != "course"]
            except Exception:
                course_docs = retrieved_docs

        has_course: bool = context.get("has_course", bool(course_docs))

        # ── Sources réelles ────────────────────────────────────────────────
        all_docs = course_docs + supplement_docs
        sources = self._extract_sources(all_docs)

        # ── Aucun cours disponible ─────────────────────────────────────────
        if not has_course and not prompt_context:
            msg = (
                f"⚠️ **Aucun document de cours sur « {concept} » n'a été trouvé dans la base documentaire.**\n\n"
                "Conformément aux consignes pédagogiques de NURU, aucun contenu inventé ne sera généré.\n"
                "Veuillez vérifier que les manuels correspondants ont bien été indexés, "
                "ou reformulez votre requête avec des mots-clés différents."
            )
            return self._build_result(concept, level, msg, [], math_tool_result, sources_used=False)

        # ── Reconstruction du contexte si manquant ─────────────────────────
        if not prompt_context and (course_docs or supplement_docs):
            prompt_context = self._build_context_block(course_docs, supplement_docs)

        # ── Génération LLM ─────────────────────────────────────────────────
        explanation = self._generate_llm_explanation(
            concept=concept,
            level=level,
            prompt_context=prompt_context,
            math_tool_result=math_tool_result,
            has_course=has_course,
            sources=sources,
        )

        # ── Repli : synthèse brute RAG (sans LLM) ─────────────────────────
        if not explanation:
            explanation = self._rag_synthesis_fallback(concept, course_docs, supplement_docs, sources)

        return self._build_result(concept, level, explanation, all_docs, math_tool_result, sources_used=True, sources=sources)

    # ----------------------------------------------------------------- helpers

    def _build_result(
        self,
        concept: str,
        level: str,
        explanation: str,
        docs: List[Dict[str, Any]],
        math_tool_result: Optional[Any],
        sources_used: bool = True,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "type": "cours",
            "concept": concept,
            "level": level,
            "explanation": explanation,
            "summary": self._build_summary(concept, docs),
            "next_steps": self._suggest_next_steps(concept),
            "math_tool_result": math_tool_result,
            "sources_used": sources_used,
            "sources": sources or [],
        }

    def _extract_sources(self, docs: List[Dict[str, Any]]) -> List[str]:
        """Retourne les sources réellement présentes dans les documents récupérés."""
        seen: set[str] = set()
        result: List[str] = []
        for doc in docs:
            meta = doc.get("metadata", {})
            src = meta.get("source") or meta.get("filename") or meta.get("title")
            chap = meta.get("chapitre")
            if src:
                entry = f"{src} — Chapitre : {chap}" if chap else src
            elif chap:
                entry = f"Chapitre : {chap}"
            else:
                continue
            if entry not in seen:
                seen.add(entry)
                result.append(entry)
        return sorted(result)

    def _build_context_block(
        self,
        course_docs: List[Dict[str, Any]],
        supplement_docs: List[Dict[str, Any]],
    ) -> str:
        """Construit un bloc contexte brut quand le retriever_agent n'en a pas fourni."""
        parts: List[str] = []
        if course_docs:
            parts.append("=== DOCUMENTS DE COURS PRINCIPAUX ===")
            for i, doc in enumerate(course_docs, 1):
                text = doc.get("text", "").strip()
                if not text:
                    continue
                meta = doc.get("metadata", {})
                chap = meta.get("chapitre", "")
                src = meta.get("source", meta.get("filename", ""))
                header = f"[COURS {i} | {chap or 'Général'}{' | ' + src if src else ''}]"
                parts.append(f"{header}\n{text}")
        if supplement_docs:
            parts.append("=== COMPLÉMENTS ET TD ===")
            for i, doc in enumerate(supplement_docs, 1):
                text = doc.get("text", "").strip()
                if not text:
                    continue
                meta = doc.get("metadata", {})
                chap = meta.get("chapitre", "")
                src = meta.get("source", meta.get("filename", ""))
                header = f"[TD {i} | {chap or 'Général'}{' | ' + src if src else ''}]"
                parts.append(f"{header}\n{text}")
        return "\n\n".join(parts)[:8000]

    # ------------------------------------------------------------ LLM prompt

    def _generate_llm_explanation(
        self,
        concept: str,
        level: str,
        prompt_context: str,
        math_tool_result: Optional[Any],
        has_course: bool,
        sources: List[str],
    ) -> str:
        """
        Construit le prompt LLM et appelle le modèle.

        Le prompt impose :
          - De travailler UNIQUEMENT à partir du contexte RAG fourni.
          - D'adopter le style d'un chapitre de manuel scolaire (pas une liste, pas un template).
          - De ne jamais inventer de formules, définitions, théorèmes ou références absents du contexte.
          - D'utiliser impérativement MathJax / KaTeX pour le rendu des formules.
        """
        if not prompt_context:
            # Pas de contexte = pas de génération
            return ""

        # ── Instruction système ────────────────────────────────────────────
        system_instructions = (
            "Tu es le rédacteur principal des manuels scolaires de Mathématiques "
            "pour les classes de Terminale S1 et S2 au Sénégal (Programme officiel).\n\n"

            "═══════════════════════════════════════════\n"
            "RÈGLE ABSOLUE N°1 — SOURCE DE VÉRITÉ UNIQUE\n"
            "═══════════════════════════════════════════\n"
            "Le contexte RAG ci-dessous est ta SEULE et UNIQUE source d'information.\n"
            "Priorise ABSOLUMENT les documents marqués comme COURS. N'utilise les documents TD "
            "que comme compléments si des exemples sont pertinents.\n"
            "Tu ne dois JAMAIS inventer, compléter de mémoire, ni ajouter des éléments "
            "absents du contexte (définitions, théorèmes, formules, propriétés, exemples, références).\n"
            "Si une information n'est pas dans le contexte RAG, ne l'écris pas.\n\n"

            "═══════════════════════════════════\n"
            "RÈGLE ABSOLUE N°2 — NOTATION MATHÉMATIQUE\n"
            "═══════════════════════════════════\n"
            "Utilise IMPÉRATIVEMENT la syntaxe MathJax / KaTeX pour toutes les formules et symboles mathématiques.\n"
            "  • Les formules en ligne doivent être encadrées par $...$.\n"
            "  • Les formules centrées ou complexes doivent être encadrées par $$...$$.\n"
            "  • Utilise les commandes LaTeX standards (\\dfrac, \\sum, \\int, \\mathbb, \\lim, etc.).\n\n"

            "═══════════════════════════════════\n"
            "RÈGLE ABSOLUE N°3 — STYLE RÉDACTIONNEL ET STRUCTURE\n"
            "═══════════════════════════════════\n"
            "Rédige un véritable chapitre de manuel scolaire, de façon fluide, sans afficher aucun "
            "texte de consigne, sans crochets ni parenthèses d'instruction (ex. pas de \"2-3 paragraphes\").\n"
            "Exigences :\n"
            "  • De vrais paragraphes de texte explicatif avec des phrases de liaison.\n"
            "  • Des transitions logiques entre les sections.\n"
            "  • Les définitions et théorèmes extraits du RAG sont mis en évidence.\n"
            "  • Les démonstrations/justifications sont développées, pas résumées en une ligne.\n"
            "  • Les exemples sont entièrement résolus, étape par étape.\n"
            "  • NE PAS inclure de sections vides, ni inventer des sections si le contenu manque.\n\n"
            
            "Organise ton chapitre EXACTEMENT selon la structure suivante (uniquement si le contenu RAG le permet) :\n\n"
            "# {Titre du chapitre}\n\n"
            "## Compétence visée\n"
            "Compétence développée par ce chapitre selon le programme sénégalais.\n\n"
            "## Objectifs d'apprentissage\n"
            "À la fin de ce chapitre, l'élève sera capable de :\n"
            "- ...\n"
            "- ...\n"
            "- ...\n\n"
            "---\n\n"
            "# 1. Rappels\n\n"
            "Présenter uniquement les notions indispensables.\n"
            "Formules utiles.\n"
            "Propriétés déjà étudiées.\n\n"
            "---\n\n"
            "# 2. Nouvelles notions\n\n"
            "Introduire progressivement les nouvelles définitions.\n"
            "Chaque définition doit être expliquée avec un langage simple.\n"
            "Les notations mathématiques doivent être écrites en LaTeX.\n\n"
            "---\n\n"
            "# 3. Propriétés et théorèmes\n\n"
            "Présenter uniquement les propriétés utiles au chapitre.\n"
            "Pour chaque propriété :\n"
            "- énoncé\n"
            "- explication\n"
            "- interprétation\n\n"
            "---\n\n"
            "# 4. Méthodes de résolution\n\n"
            "Présenter les différentes méthodes utilisées.\n"
            "Pour chaque méthode :\n"
            "- Principe\n"
            "- Étapes\n"
            "- Astuces\n\n"
            "---\n\n"
            "# 5. Exemples entièrement résolus\n\n"
            "Minimum 3 exemples.\n"
            "Pour chaque exemple :\n"
            "Énoncé\n"
            "Résolution détaillée\n"
            "Justification de chaque étape\n"
            "Conclusion\n\n"
            "---\n\n"
            "# 6. Exercices d'application\n\n"
            "Du plus simple au plus difficile.\n\n"
            "---\n\n"
            "# 7. Erreurs fréquentes\n\n"
            "Présenter les erreurs classiques des élèves.\n"
            "Expliquer pourquoi elles sont fausses.\n\n"
            "---\n\n"
            "# 8. À retenir\n\n"
            "Résumé du chapitre.\n"
            "Formules importantes.\n"
            "Méthodes importantes.\n\n"
            "---\n\n"
            "# Sources utilisées\n\n"
            "Lister uniquement les documents RAG réellement utilisés.\n"
            "Ne jamais inventer de références.\n"
            "Prioriser :\n"
            "- Cours\n"
            "- Leçons\n"
            "- Fascicules officiels\n"
            "Utiliser les TD uniquement pour construire des exemples.\n"
            "Ne jamais utiliser les TD comme source principale du cours.\n\n"
            "RAPPEL FINAL : Ton rendu final doit être propre, fluide et structuré exactement comme demandé."
        )

        if not has_course:
            system_instructions += (
                "\n\n⚠️ ATTENTION : Les documents RAG fournis sont principalement des TD/exercices, "
                "sans cours explicite. Extrais uniquement les éléments de cours que ces documents "
                "contiennent (énoncés de propriétés, rappels de cours en début de TD, etc.) "
                "et signale clairement en introduction que le cours complet n'est pas disponible."
            )

        # ── Prompt utilisateur ─────────────────────────────────────────────
        prompt_lines = [
            f"Rédige le chapitre de cours sur : « {concept} »",
            f"Niveau d'explication : {level}",
        ]

        if math_tool_result:
            prompt_lines.append(
                f"\nRésultat de calcul exact (SymPy) à intégrer dans la démonstration : {math_tool_result}"
            )

        if sources:
            prompt_lines.append(f"\nSources disponibles dans le RAG : {', '.join(sources)}")

        prompt_lines.append(
            "\nIMPORTANT : Base-toi EXCLUSIVEMENT sur le contexte RAG fourni. "
            "Ne complète pas avec tes connaissances générales. "
            "Si une information est absente du contexte, ne l'écris pas."
        )

        prompt = "\n".join(prompt_lines)

        try:
            text = generate_pedagogical_text(
                prompt=prompt,
                context=prompt_context,
                system_prompt=system_instructions,
            )
            # S'assurer que les sources sont présentes en fin de document
            if sources and "Sources" not in text:
                sources_block = "\n\n---\n**📚 Sources consultées :**\n" + "\n".join(f"- {s}" for s in sources)
                text += sources_block
            return text
        except Exception as exc:  # noqa: BLE001
            logger.warning("⚠️ Génération LLM échouée dans cours_agent : %s", exc)
            return ""

    # --------------------------------------------------- fallback (sans LLM)

    def _rag_synthesis_fallback(
        self,
        concept: str,
        course_docs: List[Dict[str, Any]],
        supplement_docs: List[Dict[str, Any]],
        sources: List[str],
    ) -> str:
        """
        Synthèse brute des documents RAG quand le LLM est indisponible.
        Aucun contenu inventé : le texte affiché est directement extrait des chunks RAG.
        """
        parts: List[str] = [f"# Cours : {concept} (Terminale S1/S2)\n"]

        if not course_docs and not supplement_docs:
            return (
                f"⚠️ **Aucun document de cours sur « {concept} » n'a été trouvé dans le RAG.**\n"
                "Veuillez indexer un document de cours pour obtenir une explication."
            )

        if course_docs:
            parts.append("## Contenu extrait des cours officiels\n")
            for doc in course_docs:
                text = doc.get("text", "").strip()
                if text:
                    meta = doc.get("metadata", {})
                    chap = meta.get("chapitre", "")
                    if chap:
                        parts.append(f"### {chap}\n")
                    parts.append(text + "\n")

        if supplement_docs:
            parts.append("\n## Exemples et exercices complémentaires (TD)\n")
            for doc in supplement_docs:
                text = doc.get("text", "").strip()
                if text:
                    parts.append(text + "\n")

        if sources:
            parts.append("\n---\n**📚 Sources consultées :**\n" + "\n".join(f"- {s}" for s in sources))

        return "\n".join(parts)

    # ---------------------------------------------------------------- utils

    def _build_summary(self, concept: str, docs: List[Dict[str, Any]]) -> str:
        """Extrait un résumé depuis le meilleur document RAG disponible."""
        if not docs:
            return f"📋 **Résumé — {concept} :** Consulter le manuel officiel pour approfondir."
        best = max(docs, key=lambda d: d.get("score", 0.0))
        text = best.get("text", "").strip()
        if not text:
            return f"📋 **Résumé — {concept} :** Consulter le manuel officiel pour approfondir."
        snippet = text[:400]
        return f"📋 **Synthèse :**\n\n{snippet}{'...' if len(text) > 400 else ''}"

    def _suggest_next_steps(self, concept: str) -> List[str]:
        return [
            "📖 Étudier les démonstrations des théorèmes principaux du chapitre",
            "✍️ S'entraîner sur les exercices d'application guidée",
            "💡 Consulter les fiches de synthèse pour les épreuves du Bac",
        ]