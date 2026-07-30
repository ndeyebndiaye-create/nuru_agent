# backend/agents/verifier_agent.py
"""
Agent Vérificateur - Vérifie la qualité des réponses.
"""
from typing import Dict, Any, List, Optional
import logging
import re

from .config import AgentConfig
from .state import AgentState

logger = logging.getLogger(__name__)

# Vocabulaire hors-programme Terminale S1 (analyse à une variable) qui, s'il
# apparaît dans une explication SANS que le concept demandé ne relève
# explicitement de plusieurs variables, est un signe fort de confusion/
# hallucination du LLM (cf. SPRINT2_FUNCTIONAL_AND_PEDAGOGICAL_DIAGNOSTIC.md,
# Test 2 : question sur la "dérivabilité" répondue avec du gradient/f(x,y)).
_OUT_OF_SCOPE_MULTIVARIABLE_TERMS = (
    "dérivées partielles", "derivees partielles", "dérivée partielle", "derivee partielle",
    "gradient", "f(x,y)", "f(x, y)",
    "fonction à deux variables", "fonction a deux variables",
)
_MULTIVARIABLE_CONCEPT_HINTS = ("plusieurs variables", "deux variables", "gradient", "partielle")


class VerifierAgent:
    """
    Agent spécialisé dans la vérification.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()

    def verify(self, state: AgentState, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie une réponse.

        Args:
            state: État actuel
            response: Réponse à vérifier

        Returns:
            Résultat de la vérification
        """
        # 1. Vérifier la cohérence
        coherence_score = self._check_coherence(response)

        # 2. Vérifier les hallucinations
        hallucination_risk = self._check_hallucinations(response)

        # 3. Vérifier les règles pédagogiques
        pedagogical_issues = self._check_pedagogical_rules(response)
        pedagogical_issues += self._check_mathematical_consistency(response)

        # 4. Décider si la réponse est acceptable
        is_valid = (
            coherence_score > 0.7 and
            hallucination_risk < 0.3 and
            len(pedagogical_issues) == 0
        )

        return {
            "is_valid": is_valid,
            "coherence_score": coherence_score,
            "hallucination_risk": hallucination_risk,
            "pedagogical_issues": pedagogical_issues,
            "suggestions": self._generate_suggestions(pedagogical_issues)
        }

    def _check_mathematical_consistency(self, response: Dict[str, Any]) -> List[str]:
        """Validation pédagogique minimale et objective (sans second appel
        LLM) : détecte le vocabulaire hors-programme multivariable sur un
        concept mono-variable, et vérifie qu'un résultat SymPy calculé
        apparaît bien tel quel dans le texte généré (empêche le LLM de
        « recalculer » lui-même et de se tromper)."""
        issues: List[str] = []
        if not isinstance(response, dict):
            return issues

        explanation = str(response.get("explanation") or response.get("statement") or "")
        text_lower = explanation.lower()
        concept = str(response.get("concept", "")).lower()
        concept_is_multivariable = any(hint in concept for hint in _MULTIVARIABLE_CONCEPT_HINTS)

        if not concept_is_multivariable:
            for term in _OUT_OF_SCOPE_MULTIVARIABLE_TERMS:
                if term in text_lower:
                    issues.append(
                        f"Vocabulaire hors-programme détecté (« {term} ») pour un concept mono-variable « {concept or '?'} »"
                    )
                    break

        math_tool_result = response.get("math_tool_result")
        if isinstance(math_tool_result, dict):
            result_value = str(math_tool_result.get("result", "")).strip()
            if result_value and result_value not in explanation:
                issues.append(
                    f"Le résultat calculé exactement ({result_value}) n'apparaît pas dans le texte généré"
                )

        return issues
    
    def _check_coherence(self, response: Dict[str, Any]) -> float:
        """Vérifie la cohérence de la réponse."""
        # Implémentation simple
        text = str(response)
        
        # Vérifier la longueur
        if len(text) < 10:
            return 0.2
        
        # Vérifier la présence de mots-clés
        coherence_keywords = ["donc", "parce que", "en effet", "ainsi", "alors"]
        score = 0.5
        for keyword in coherence_keywords:
            if keyword in text.lower():
                score += 0.1
        
        return min(score, 1.0)
    
    def _check_hallucinations(self, response: Dict[str, Any]) -> float:
        """Vérifie le risque d'hallucination."""
        # Implémentation simple
        text = str(response).lower()
        
        # Mots pouvant indiquer une hallucination
        hallucination_indicators = [
            "peut-être", "probablement", "je pense", "il semble",
            "selon moi", "à mon avis"
        ]
        
        risk = 0.0
        for indicator in hallucination_indicators:
            if indicator in text:
                risk += 0.2
        
        return min(risk, 1.0)
    
    def _check_pedagogical_rules(self, response: Dict[str, Any]) -> List[str]:
        """Vérifie les règles pédagogiques."""
        issues = []
        text = str(response).lower()
        
        # Vérifier si la réponse donne directement la solution
        if "solution" in text and "étape" not in text:
            issues.append("Donne la solution sans étapes intermédiaires")
        
        # Vérifier si la réponse est trop complexe
        if len(text) > 500 and "résumé" not in text:
            issues.append("Réponse trop longue sans résumé")
        
        return issues
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """Génère des suggestions d'amélioration."""
        suggestions = []
        for issue in issues:
            if "solution" in issue:
                suggestions.append("Ajoute des étapes intermédiaires avant la solution")
            elif "trop longue" in issue:
                suggestions.append("Ajoute un résumé en fin de réponse")
        return suggestions