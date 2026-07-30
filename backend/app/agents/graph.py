# backend/app/agents/graph.py
"""
Graphe multi-agents NURU, construit avec LangGraph.

Flux :

    START -> planner -> retriever -> [math_tool?] -> {cours|exercices|quiz}
          -> verifier -> progression -> END

Le routage entre cours/exercices/quiz est conditionnel, basé sur
l'intention détectée par le Planner. L'agent Math (SymPy) est appelé en
amont du nœud de contenu quand le Planner détecte une demande de calcul,
pour que l'explication du LLM s'appuie sur un résultat exact plutôt que de
"deviner" un calcul.
"""
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict

from langgraph.graph import StateGraph, END

from .state import GraphState
from .config import AgentConfig
from .planner import PlannerAgent
from .retriever_agent import RetrieverAgent
from .cours_agent import CoursAgent
from .exercices_agent import ExercicesAgent
from .quiz_agent import QuizAgent
from .verifier_agent import VerifierAgent
from .progression_agent import ProgressionAgent
from ..tools.math_tools import call_math_tool, MathToolError

logger = logging.getLogger(__name__)


def _agent_state_view(gstate: GraphState) -> SimpleNamespace:
    """Adaptateur léger : les agents historiques (Cours/Exercices/Verifier)
    n'ont besoin que de quelques attributs de AgentState. On leur fournit
    un objet minimal plutôt que de réécrire ces classes en profondeur."""
    return SimpleNamespace(
        current_level=gstate.get("level", "reformulation"),
        retrieved_docs=gstate.get("retrieved_docs", []),
        iterations=gstate.get("iterations", 0),
    )


class NuruGraph:
    """Construit et expose le graphe LangGraph de NURU."""

    def __init__(self, config: AgentConfig = None, retriever=None):
        self.config = config or AgentConfig()

        self.planner = PlannerAgent(self.config)
        self.retriever_agent = RetrieverAgent(self.config, retriever=retriever)
        self.cours_agent = CoursAgent(self.config)
        self.exercices_agent = ExercicesAgent(self.config)
        self.quiz_agent = QuizAgent(self.config)
        self.verifier_agent = VerifierAgent(self.config)
        self.progression_agent = ProgressionAgent(self.config)

        self.graph = self._build_graph()

    # ---------------------------------------------------------------- nodes

    def _node_planner(self, state: GraphState) -> Dict[str, Any]:
        agent_state = _agent_state_view(state)
        agent_state.user_message = state["user_message"]
        plan = self.planner.plan(agent_state)
        return {
            "intent": plan["intent"],
            "level": plan["level"],
            "required_agents": plan["required_agents"],
            "required_tools": plan["required_tools"],
            "parameters": plan["parameters"],
        }

    def _node_retriever(self, state: GraphState) -> Dict[str, Any]:
        concept = state.get("parameters", {}).get("concept")
        result = self.retriever_agent.retrieve(query=state["user_message"], concept=concept)
        prompt_context = self.retriever_agent.build_prompt_context(result)
        return {
            "retrieved_docs": result.get("documents", []),
            "course_docs": result.get("course_docs", []),
            "supplement_docs": result.get("supplement_docs", []),
            "has_course": result.get("has_course", False),
            "prompt_context": prompt_context,
        }

    def _node_math_tool(self, state: GraphState) -> Dict[str, Any]:
        tools = state.get("required_tools", [])
        if not tools:
            return {}
        tool_name = tools[0]
        params = state.get("parameters", {})
        expression = params.get("math_expression")
        if not expression:
            # Le Planner ne doit normalement jamais ajouter un outil sans
            # expression valide (voir planner.py), mais on refuse par
            # prudence de retomber sur le concept/message brut : ce ne sont
            # pas des expressions mathematiques et produiraient un calcul
            # SymPy absurde plutot qu'une absence propre de resultat.
            logger.info("Outil math '%s' requis sans expression valide, ignore.", tool_name)
            return {"math_tool_result": None}
        try:
            result = call_math_tool(tool_name, expression=expression)
            return {"math_tool_result": result}
        except MathToolError as exc:
            logger.info("Outil math non applicable ('%s'): %s", expression, exc)
            return {"math_tool_result": None}

    def _node_cours(self, state: GraphState) -> Dict[str, Any]:
        agent_state = _agent_state_view(state)
        response = self.cours_agent.explain(agent_state, {
            "concept": state.get("parameters", {}).get("concept", ""),
            "retrieved_docs": state.get("retrieved_docs", []),
            "course_docs": state.get("course_docs", []),
            "supplement_docs": state.get("supplement_docs", []),
            "has_course": state.get("has_course", False),
            "prompt_context": state.get("prompt_context", ""),
            "math_tool_result": state.get("math_tool_result"),
        })
        return {"agent_responses": {**state.get("agent_responses", {}), "cours": response}}

    def _node_exercices(self, state: GraphState) -> Dict[str, Any]:
        agent_state = _agent_state_view(state)
        response = self.exercices_agent.generate(agent_state, {
            "concept": state.get("parameters", {}).get("concept", ""),
            "difficulty": state.get("parameters", {}).get("difficulty", "intermediate"),
            "prompt_context": state.get("prompt_context", ""),
        })
        return {"agent_responses": {**state.get("agent_responses", {}), "exercices": response}}

    def _node_quiz(self, state: GraphState) -> Dict[str, Any]:
        agent_state = _agent_state_view(state)
        response = self.quiz_agent.generate(agent_state, {
            "concept": state.get("parameters", {}).get("concept", ""),
            "quiz_type": state.get("parameters", {}).get("quiz_type", "qcm"),
            "prompt_context": state.get("prompt_context", ""),
        })
        return {"agent_responses": {**state.get("agent_responses", {}), "quiz": response}}

    def _node_verifier(self, state: GraphState) -> Dict[str, Any]:
        agent_state = _agent_state_view(state)
        agent_responses = state.get("agent_responses", {})
        verifications = {}
        for name, response in agent_responses.items():
            verifications[name] = self.verifier_agent.verify(agent_state, response)

        final_response = self._build_final_response(state, agent_responses)

        # Le verdict du Verifier doit avoir un effet visible : jusqu'ici,
        # `is_valid` était calculé puis ignoré par _build_final_response.
        # On avertit l'utilisateur uniquement quand un probleme *concret et
        # nommable* a ete detecte (pedagogical_issues, y compris la
        # coherence mathematique) — pas simplement parce que le score de
        # coherence generique (heuristique a base de connecteurs francais,
        # peu fiable pour de courtes reponses de reformulation) est bas :
        # sinon l'avertissement se declenche presque systematiquement, avec
        # une liste de raisons vide, ce qui n'apporte rien a l'eleve.
        issues: list[str] = []
        for verification in verifications.values():
            issues.extend(verification.get("pedagogical_issues", []))
        if issues:
            logger.warning("Problème(s) détecté(s) par le Verifier: %s", issues)
            warning = "⚠️ **Cette réponse n'a pas pu être entièrement vérifiée** (" + "; ".join(issues) + ").\n\n"
            final_response = warning + final_response

        confidence = (
            sum(v.get("coherence_score", 0.0) for v in verifications.values()) / len(verifications)
            if verifications else 0.5
        )
        return {
            "verification": verifications,
            "final_response": final_response,
            "confidence_score": round(confidence, 2),
        }

    def _node_progression(self, state: GraphState) -> Dict[str, Any]:
        student_id = state.get("student_id")
        concept = state.get("parameters", {}).get("concept")
        self.progression_agent.log_interaction(
            student_id=student_id,
            user_message=state["user_message"],
            intent=state.get("intent", "general"),
            level=state.get("level", "reformulation"),
            concept=concept,
            response=state.get("final_response", ""),
            session_id=state.get("session_id"),
        )
        summary = self.progression_agent.get_profile_summary(student_id)
        return {"progression_summary": summary}

    # ------------------------------------------------------------ routing

    def _route_after_planner(self, state: GraphState) -> str:
        intent = state.get("intent", "general")
        return {"cours": "cours", "exercice": "exercices", "quiz": "quiz"}.get(intent, "cours")

    def _route_after_retriever(self, state: GraphState) -> str:
        return "math_tool" if state.get("required_tools") else "content"

    # --------------------------------------------------------------- build

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("planner", self._node_planner)
        workflow.add_node("retriever", self._node_retriever)
        workflow.add_node("math_tool", self._node_math_tool)
        workflow.add_node("dispatch", self._node_passthrough)
        workflow.add_node("cours", self._node_cours)
        workflow.add_node("exercices", self._node_exercices)
        workflow.add_node("quiz", self._node_quiz)
        workflow.add_node("verifier", self._node_verifier)
        workflow.add_node("progression", self._node_progression)

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "retriever")

        workflow.add_conditional_edges(
            "retriever",
            self._route_after_retriever,
            {"math_tool": "math_tool", "content": "dispatch"},
        )
        workflow.add_conditional_edges(
            "math_tool",
            self._route_after_planner,
            {"cours": "cours", "exercices": "exercices", "quiz": "quiz"},
        )
        workflow.add_conditional_edges(
            "dispatch",
            self._route_after_planner,
            {"cours": "cours", "exercices": "exercices", "quiz": "quiz"},
        )

        for node_name in ("cours", "exercices", "quiz"):
            workflow.add_edge(node_name, "verifier")

        workflow.add_edge("verifier", "progression")
        workflow.add_edge("progression", END)

        return workflow.compile()

    def _node_passthrough(self, state: GraphState) -> Dict[str, Any]:
        """Nœud neutre utilisé uniquement pour le routage conditionnel."""
        return {}

    # --------------------------------------------------------------- utils

    def _build_final_response(self, state: GraphState, agent_responses: Dict[str, Any]) -> str:
        parts = []
        intent = state.get("intent", "general")

        intros = {
            "cours": "📚 **Cours :** Voici une explication claire et structurée.",
            "exercice": "✍️ **Exercice :** Essayons de résoudre ensemble.",
            "quiz": "📋 **Quiz :** Testons tes connaissances.",
            "general": "💡 **NURU :** Je suis là pour t'aider.",
        }
        parts.append(intros.get(intent, intros["general"]))

        if "cours" in agent_responses:
            response = agent_responses["cours"]
            parts.append(f"\n{response.get('explanation', '')}")
        if "exercices" in agent_responses:
            exercise = agent_responses["exercices"].get("exercise", {})
            parts.append(f"\n📝 **{exercise.get('title', 'Exercice')}**")
            parts.append(exercise.get("statement", ""))
            if exercise.get("questions"):
                parts.append("\n".join(exercise["questions"]))
            hints = agent_responses["exercices"].get("hints", [])
            if hints:
                parts.append("\n💡 **Indices :**\n" + "\n".join(hints))
        if "quiz" in agent_responses:
            quiz_response = agent_responses["quiz"]
            questions = quiz_response.get("questions", [])
            if not questions:
                # Le LLM n'a pas produit de quiz valide (voir QuizAgent) :
                # on l'indique clairement, on n'affiche jamais de contenu
                # placeholder de repli.
                parts.append("\n" + quiz_response.get("instructions", "⚠️ Quiz indisponible pour le moment."))
            else:
                parts.append("\n📋 **Quiz :**")
                for q in questions:
                    parts.append(f"\n{q.get('question', '')}")
                    # QCM / Vrai-Faux (format {choices: [{id, text}], correct_answer}) :
                    # la bonne reponse n'est jamais affichee avant que l'eleve reponde.
                    for choice in q.get("choices", []):
                        parts.append(f"   {choice.get('id', '')}. {choice.get('text', '')}")

        return "\n".join(p for p in parts if p)

    # ---------------------------------------------------------------- run

    def invoke(self, user_message: str, student_id: str = None, session_id: str = None,
               context: Dict[str, Any] = None, iterations: int = 0) -> Dict[str, Any]:
        initial_state: GraphState = {
            "user_message": user_message,
            "context": context or {},
            "student_id": student_id,
            "session_id": session_id,
            "agent_responses": {},
            "iterations": iterations,
        }
        result = self.graph.invoke(initial_state)
        return result
