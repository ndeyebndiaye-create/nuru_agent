# backend/agents/exercices_agent.py
"""
Agent Exercices - Génère et corrige des exercices.
"""
from typing import Dict, Any, List, Optional
import logging
import re

from .config import AgentConfig
from .state import AgentState
from .llm_utils import generate_pedagogical_text

logger = logging.getLogger(__name__)

class ExercicesAgent:
    """
    Agent spécialisé dans les exercices.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
    
    def generate(self, state: AgentState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un exercice.
        
        Args:
            state: État actuel
            context: Contexte
            
        Returns:
            Exercice structuré
        """
        concept = context.get("concept", "le concept")
        level = state.current_level
        difficulty = context.get("difficulty", "intermediate")
        prompt_context = context.get("prompt_context", "")

        # Générer l'exercice
        exercise = self._create_exercise(concept, difficulty, prompt_context)
        
        return {
            "type": "exercice",
            "concept": concept,
            "difficulty": difficulty,
            "exercise": exercise,
            "hints": self._generate_hints(exercise, level),
            "solution": self._generate_solution(exercise, level)
        }
    
    def _create_exercise(self, concept: str, difficulty: str, prompt_context: str = "") -> Dict[str, Any]:
        """Crée un exercice, via le LLM si possible (en s'appuyant sur le
        contexte RAG pour rester fidèle au programme Terminale S1), sinon
        via un gabarit générique. Le LLM suit un template structuré
        (plusieurs exercices, compétences évaluées, niveaux de difficulté)."""

        difficulty_label = {
            "beginner": "Débutant",
            "intermediate": "Intermédiaire",
            "advanced": "Avancé",
        }.get(difficulty, "Intermédiaire")

        template_structure = f"""
Tu es un générateur d'exercices de mathématiques pour la plateforme NURU, destiné aux élèves de Terminale S1 (programme sénégalais). Structure IMPÉRATIVEMENT ta réponse en suivant EXACTEMENT ce plan Markdown, sans t'en écarter :

# 📝 Exercices — {concept}
> **Classe :** Terminale
>
> **Série :** S1
>
> **Chapitre :** {concept}
>
> **Niveau :** {difficulty_label}
>
> **Nombre d'exercices :** 3
---
# 🎯 Compétences évaluées
- (liste 2 à 4 compétences précises évaluées par ces exercices, en lien direct avec « {concept} »)
---
# Exercice 1
### Énoncé
(énoncé complet, autonome, sans solution)
### Niveau
🟢 Facile
### Objectif
(ce que l'exercice permet de vérifier/travailler)
### Indication (optionnelle)
💡 (un indice court, sans donner la solution)
---
# Exercice 2
### Énoncé
...
### Niveau
🟡 Moyen
### Objectif
...
### Indication (optionnelle)
💡 ...
---
# Exercice 3
### Énoncé
...
### Niveau
🔴 Difficile
### Objectif
...
### Indication (optionnelle)
💡 ...
---
# 📌 Conseils
- (2 à 3 conseils méthodologiques généraux pour aborder ce type d'exercice)

Règles strictes :
- Le contexte RAG fourni est ta SEULE et UNIQUE base de travail. Inspire-toi EXCLUSIVEMENT des méthodes, exemples ou exercices (TD) présents dans le contexte.
- N'invente pas de notions mathématiques hors du contexte RAG fourni.
- Utilise IMPÉRATIVEMENT la syntaxe MathJax / KaTeX ($, $$) pour formater toutes les formules mathématiques.
- Les 3 exercices doivent porter EXCLUSIVEMENT sur le thème « {concept} ».
- Ne donne JAMAIS la solution ou le résultat final dans les énoncés ou indications — seulement des indices.
- Reste concis dans les énoncés (pas de remplissage inutile).
"""

        llm_statement = ""
        try:
            llm_statement = generate_pedagogical_text(template_structure, prompt_context)
        except Exception as exc:  # noqa: BLE001
            logger.warning("⚠️ Génération LLM indisponible pour exercices_agent: %s", exc)

        if llm_statement:
            return {
                "title": f"Exercices — {concept}",
                "statement": llm_statement,
                "questions": [],
            }

        return {
            "title": f"Exercice sur {concept}",
            "statement": f"Applique tes connaissances sur {concept} pour résoudre ce problème.",
            "questions": [
                f"1. Définis {concept} en tes propres mots.",
                f"2. Donne un exemple d'application de {concept}.",
                f"3. Résous le problème suivant en utilisant {concept}."
            ]
        }
    
    def _generate_hints(self, exercise: Dict[str, Any], level: str) -> List[str]:
        """Génère des indices."""
        if level in ["reformulation", "rappel"]:
            return [
                "💡 Relis la définition du concept.",
                "💡 Identifie les éléments clés du problème."
            ]
        elif level == "indice":
            return [
                "💡 Commence par écrire ce que tu sais.",
                "💡 Applique la formule étape par étape."
            ]
        else:
            return [
                "💡 Voici la première étape: identifie les données.",
                "💡 Utilise la formule appropriée."
            ]
    
    def _generate_solution(self, exercise: Dict[str, Any], level: str) -> Dict[str, Any]:
        """Génère la solution."""
        if level == "solution_complete":
            return {
                "type": "complete",
                "steps": [
                    "Étape 1: Analyse du problème",
                    "Étape 2: Application du concept",
                    "Étape 3: Vérification du résultat"
                ],
                "answer": "Solution détaillée..."
            }
        else:
            return {
                "type": "guided",
                "steps": [
                    "🔍 Quelle est la première chose à faire ?",
                    "📝 Quelle formule utiliser ?"
                ]
            }