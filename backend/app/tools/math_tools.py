# backend/app/tools/math_tools.py
"""
Outils mathématiques basés sur SymPy.

Le LLM ne doit jamais faire de calcul "à la main". Ces fonctions
fournissent des calculs exacts et vérifiables (dérivées, intégrales,
résolution d'équations, simplification...) que les agents peuvent
appeler comme des "tools" avant de rédiger leur réponse pédagogique.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

logger = logging.getLogger(__name__)

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Symbole par défaut utilisé dans le programme Terminale S1
X = sp.symbols("x")

# Fonctions mathématiques usuelles reconnues dans une expression en langage
# naturel (ex: "la dérivée de sin(x)").
_KNOWN_FUNCTIONS = ("asin", "acos", "atan", "sin", "cos", "tan", "ln", "log", "exp", "sqrt", "abs")

_SUPERSCRIPT_DIGITS = {"⁰": "^0", "¹": "^1", "²": "^2", "³": "^3", "⁴": "^4", "⁵": "^5", "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9"}

# Préfixe de définition de fonction explicite très fréquent dans les énoncés
# français ("f(x)=...", "g(t)=..."), y compris quand le nom de la fonction a
# déjà été retiré en amont par extract_math_expression (qui ne capture que
# les caractères mathématiques, pas les lettres de nom de fonction) et qu'il
# ne reste plus que "(x)=..." : on ne garde que le membre de droite.
_FUNCTION_DEF_PATTERN = re.compile(r"^[a-zA-Z]?\s*\([a-zA-Z]\)\s*=\s*")


class MathToolError(Exception):
    """Erreur levée quand une expression ne peut pas être traitée."""


def _normalize_superscripts(text: str) -> str:
    """Convertit les exposants unicode (x² -> x^2) utilisés dans la notation
    mathématique française courante, avant tout parsing."""
    return "".join(_SUPERSCRIPT_DIGITS.get(ch, ch) for ch in text)


def _strip_function_definition(expression: str) -> str:
    """Retire un préfixe de définition de fonction explicite (ex: 'f(x)=')
    pour ne garder que l'expression à droite du signe égal."""
    return _FUNCTION_DEF_PATTERN.sub("", expression.strip())


def _looks_like_natural_language(expression: str) -> bool:
    """Rejette les chaînes qui ressemblent à du texte naturel plutôt qu'à une
    expression mathématique exploitable : aucun chiffre, aucun opérateur,
    aucune variable isolée ni fonction connue (ex: le mot "dérivées" seul,
    seulement des lettres accentuées assemblées, ne doit jamais être envoyé
    à SymPy — il serait interprété comme un produit de lettres isolées)."""
    stripped = expression.strip()
    if not stripped:
        return True
    has_digit = any(ch.isdigit() for ch in stripped)
    has_operator = any(ch in "+-*/^=" for ch in stripped)
    # Les lettres accentuees (À-ÿ) comptent comme des lettres pour la
    # detection d'isolement : sinon "dérivées" serait lu comme "d" isole
    # (suivi de "é", hors de la classe [a-zA-Z]) et rejete a tort comme une
    # "variable isolee" alors que c'est un mot francais ordinaire.
    has_single_letter_var = bool(re.search(r"(?<![a-zA-ZÀ-ÿ])[a-zA-Z](?![a-zA-ZÀ-ÿ])", stripped))
    has_known_function = bool(re.search(r"\b(?:" + "|".join(_KNOWN_FUNCTIONS) + r")\s*\(", stripped, re.IGNORECASE))
    return not (has_digit or has_operator or has_single_letter_var or has_known_function)


def _safe_parse(expression: str) -> sp.Expr:
    """Parse une expression utilisateur en expression SymPy, de façon sécurisée.

    On n'utilise jamais `eval()` : sympy_parser tourne dans un espace de noms
    restreint et rejette tout ce qui n'est pas une expression mathématique.
    Une validation stricte précède le parsing : toute chaîne qui ressemble à
    du texte naturel (aucun chiffre/opérateur/variable/fonction reconnue) est
    rejetée avant d'atteindre SymPy, plutôt que de produire silencieusement un
    résultat absurde (ex: dérivée nulle d'un "produit" de lettres isolées).
    """
    expression = _strip_function_definition(_normalize_superscripts(expression))

    if _looks_like_natural_language(expression):
        raise MathToolError(
            f"'{expression}' ne ressemble pas à une expression mathématique exploitable."
        )

    try:
        expr = parse_expr(
            expression.replace("^", "**"),
            transformations=_TRANSFORMATIONS,
            evaluate=True,
        )
        return expr
    except Exception as exc:  # noqa: BLE001
        raise MathToolError(f"Expression invalide : '{expression}' ({exc})") from exc


def derivee(expression: str, variable: str = "x", ordre: int = 1) -> Dict[str, Any]:
    """Calcule la dérivée (ou dérivée n-ième) d'une expression."""
    var = sp.symbols(variable)
    expr = _safe_parse(expression)
    result = sp.diff(expr, var, ordre)
    result_simpl = sp.simplify(result)
    return {
        "tool": "derivee",
        "input": expression,
        "variable": variable,
        "ordre": ordre,
        "result": str(result_simpl),
        "result_latex": sp.latex(result_simpl),
        "steps_hint": f"On dérive {sp.latex(expr)} par rapport à {variable}.",
    }


def integrale(
    expression: str,
    variable: str = "x",
    borne_inf: Optional[str] = None,
    borne_sup: Optional[str] = None,
) -> Dict[str, Any]:
    """Calcule une primitive, ou une intégrale définie si les bornes sont fournies."""
    var = sp.symbols(variable)
    expr = _safe_parse(expression)

    if borne_inf is not None and borne_sup is not None:
        a = _safe_parse(borne_inf)
        b = _safe_parse(borne_sup)
        result = sp.integrate(expr, (var, a, b))
        kind = "definie"
    else:
        result = sp.integrate(expr, var)
        kind = "primitive"

    result_simpl = sp.simplify(result)
    return {
        "tool": "integrale",
        "input": expression,
        "variable": variable,
        "type": kind,
        "bornes": [borne_inf, borne_sup] if kind == "definie" else None,
        "result": str(result_simpl),
        "result_latex": sp.latex(result_simpl),
    }


def resoudre_equation(expression: str, variable: str = "x") -> Dict[str, Any]:
    """Résout une équation. Accepte 'lhs = rhs' ou une expression égalée à 0."""
    var = sp.symbols(variable)
    if "=" in expression and "==" not in expression:
        lhs_str, rhs_str = expression.split("=", 1)
        lhs, rhs = _safe_parse(lhs_str), _safe_parse(rhs_str)
        equation = sp.Eq(lhs, rhs)
    else:
        equation = sp.Eq(_safe_parse(expression), 0)

    solutions = sp.solve(equation, var)
    return {
        "tool": "resoudre_equation",
        "input": expression,
        "variable": variable,
        "solutions": [str(s) for s in solutions],
        "solutions_latex": [sp.latex(s) for s in solutions],
        "nb_solutions": len(solutions),
    }


def simplifier(expression: str) -> Dict[str, Any]:
    """Simplifie une expression algébrique."""
    expr = _safe_parse(expression)
    simplified = sp.simplify(expr)
    return {
        "tool": "simplifier",
        "input": expression,
        "result": str(simplified),
        "result_latex": sp.latex(simplified),
    }


def developper(expression: str) -> Dict[str, Any]:
    """Développe une expression algébrique."""
    expr = _safe_parse(expression)
    expanded = sp.expand(expr)
    return {
        "tool": "developper",
        "input": expression,
        "result": str(expanded),
        "result_latex": sp.latex(expanded),
    }


def factoriser(expression: str) -> Dict[str, Any]:
    """Factorise une expression algébrique."""
    expr = _safe_parse(expression)
    factored = sp.factor(expr)
    return {
        "tool": "factoriser",
        "input": expression,
        "result": str(factored),
        "result_latex": sp.latex(factored),
    }


def limite(expression: str, variable: str = "x", vers: str = "oo", direction: str = "+") -> Dict[str, Any]:
    """Calcule la limite d'une expression."""
    var = sp.symbols(variable)
    expr = _safe_parse(expression)
    point = _safe_parse(vers)
    result = sp.limit(expr, var, point, dir=direction)
    return {
        "tool": "limite",
        "input": expression,
        "variable": variable,
        "vers": vers,
        "result": str(result),
        "result_latex": sp.latex(result),
    }


def etudier_fonction(expression: str, variable: str = "x") -> Dict[str, Any]:
    """Étude rapide d'une fonction : dérivée, racines de la dérivée (extrema
    candidats), domaine de définition approximatif (via sympy)."""
    var = sp.symbols(variable)
    expr = _safe_parse(expression)
    deriv = sp.diff(expr, var)
    deriv_simpl = sp.simplify(deriv)

    try:
        critical_points = sp.solve(sp.Eq(deriv_simpl, 0), var)
    except Exception:  # noqa: BLE001
        critical_points = []

    try:
        domain = sp.calculus.util.continuous_domain(expr, var, sp.S.Reals)
    except Exception:  # noqa: BLE001
        domain = None

    return {
        "tool": "etudier_fonction",
        "input": expression,
        "derivee": str(deriv_simpl),
        "derivee_latex": sp.latex(deriv_simpl),
        "points_critiques": [str(p) for p in critical_points],
        "domaine_definition": str(domain) if domain is not None else "non calculé",
    }


# Registre utilisé par les agents / le graphe LangGraph pour appeler
# dynamiquement un outil par son nom.
MATH_TOOLS = {
    "derivee": derivee,
    "integrale": integrale,
    "resoudre_equation": resoudre_equation,
    "simplifier": simplifier,
    "developper": developper,
    "factoriser": factoriser,
    "limite": limite,
    "etudier_fonction": etudier_fonction,
}


def call_math_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Point d'entrée générique pour appeler un outil mathématique par nom."""
    if tool_name not in MATH_TOOLS:
        raise MathToolError(f"Outil mathématique inconnu : {tool_name}")
    try:
        return MATH_TOOLS[tool_name](**kwargs)
    except MathToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error("Erreur outil math %s: %s", tool_name, exc)
        raise MathToolError(str(exc)) from exc


def extract_math_expression(message: str) -> Optional[str]:
    """Extrait la sous-chaîne ressemblant à une expression mathématique
    dans un message en langage naturel (ex: "dérive la fonction x^2 + 3x"
    -> "x^2 + 3x", "calcule la dérivée de sin(x)" -> "sin(x)"). Heuristique
    basée sur un pattern de caractères + une liste de fonctions usuelles
    reconnues ; le parseur SymPy validera/rejettera ensuite le résultat.

    Retourne None si aucune sous-chaîne exploitable n'est trouvée (ex: un
    message purement conceptuel comme "Explique-moi les dérivées") — ce None
    est le signal qui empêche `detect_math_intent` de déclencher l'outil.
    """
    message = _normalize_superscripts(message)

    function_pattern = r"(?:" + "|".join(_KNOWN_FUNCTIONS) + r")\s*\([^)\n]{0,40}\)"
    candidates = re.findall(function_pattern, message, flags=re.IGNORECASE)
    candidates += re.findall(r"[0-9x\+\-\*/\^\(\)\.= ]{2,}", message)

    scored = []
    for c in candidates:
        c = c.strip(" .,")
        if not c:
            continue
        is_function_call = bool(re.match(function_pattern, c, flags=re.IGNORECASE))
        score = sum(c.count(op) for op in "+-*/^=()") + c.count("x") + (5 if is_function_call else 0)
        scored.append((score, c))

    if not scored:
        return None

    scored.sort(key=lambda t: (-t[0], -len(t[1])))
    best = scored[0][1]
    return best if scored[0][0] > 0 else None


# Mots-clés qui indiquent une DEMANDE D'ACTION explicite (verbe d'imperatif ou
# locution verbale), par opposition aux noms de concept seuls ("dérivée",
# "intégrale", "limite", "primitive") qui apparaissent aussi bien dans des
# questions purement conceptuelles ("qu'est-ce qu'une primitive ?") — ces
# derniers ne doivent JAMAIS déclencher l'outil à eux seuls.
_MATH_ACTION_KEYWORDS = {
    "dérive": "derivee",
    "derive": "derivee",
    "calcule la dérivée": "derivee",
    "calcule la derivee": "derivee",
    "trouve la dérivée": "derivee",
    "trouve la derivee": "derivee",
    "intègre": "integrale",
    "integre": "integrale",
    "calcule une primitive": "integrale",
    "calcule la primitive": "integrale",
    "trouve une primitive": "integrale",
    "trouve la primitive": "integrale",
    "résous": "resoudre_equation",
    "resous": "resoudre_equation",
    "résoudre": "resoudre_equation",
    "simplifie": "simplifier",
    "développe": "developper",
    "developpe": "developper",
    "factorise": "factoriser",
    "calcule la limite": "limite",
    "étudie la fonction": "etudier_fonction",
    "etudie la fonction": "etudier_fonction",
}


def detect_math_intent(user_message: str) -> Optional[Dict[str, Any]]:
    """Détection d'une demande de calcul explicite, pour décider si
    l'orchestrateur doit router vers les outils SymPy avant de répondre.

    Deux conditions cumulatives sont exigées (validation stricte) :
    1. un verbe/locution d'action mathématique est présent (limite de mot,
       pour ne pas matcher une forme conjuguée/plurielle comme "dérivées") ;
    2. une expression mathématique réellement exploitable est extraite du
       message (`extract_math_expression`) — sinon, on ne déclenche rien,
       même si un mot-clé d'action a été trouvé (ex: un mot-clé isolé sans
       aucune expression ne doit jamais atteindre SymPy).

    Retourne un dict {tool, expression} ou None si aucun calcul exploitable
    n'est détecté.
    """
    text = user_message.lower()

    for keyword, tool in _MATH_ACTION_KEYWORDS.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            expression = extract_math_expression(user_message)
            if not expression:
                # Mot-clé d'action présent mais aucune expression exploitable
                # (ex: "Explique-moi les dérivées") : ne pas déclencher SymPy,
                # continuer à chercher un autre mot-clé au cas où.
                continue
            return {
                "tool": tool,
                "raw_message": user_message,
                "expression": expression,
            }

    return None
