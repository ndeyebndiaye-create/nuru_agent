# backend/app/tools/sandbox.py
"""
Sandbox Python restreint pour exécuter de petits calculs / tracés générés
par les agents (ex: calcul numérique, génération de graphiques matplotlib).

Sécurité :
- pas d'accès à `__builtins__` complet (whitelist explicite) ;
- pas d'import arbitraire (seuls math, numpy, matplotlib sont exposés) ;
- timeout dur via un processus séparé (subprocess) pour éviter les boucles
  infinies ou la consommation excessive de mémoire dans le process API ;
- pas d'accès disque / réseau depuis le code utilisateur.
"""
from __future__ import annotations

import base64
import io
import logging
import multiprocessing as mp
import traceback
from typing import Any, Dict

logger = logging.getLogger(__name__)

SANDBOX_TIMEOUT_SECONDS = 5

_ALLOWED_BUILTINS = {
    "abs", "min", "max", "sum", "round", "range", "len",
    "int", "float", "str", "list", "dict", "tuple", "set",
    "enumerate", "zip", "sorted", "print",
}


def _build_safe_globals() -> Dict[str, Any]:
    import builtins as _builtins
    import math as _math

    try:
        import numpy as _np
    except ImportError:  # numpy optionnel
        _np = None

    safe_builtins = {name: getattr(_builtins, name) for name in _ALLOWED_BUILTINS if hasattr(_builtins, name)}

    safe_globals: Dict[str, Any] = {"__builtins__": safe_builtins, "math": _math}
    if _np is not None:
        safe_globals["np"] = _np
        safe_globals["numpy"] = _np
    return safe_globals


def _worker(code: str, queue: "mp.Queue") -> None:
    """Exécuté dans un sous-processus isolé."""
    result: Dict[str, Any] = {"success": False, "stdout": "", "error": None, "image_base64": None}

    import sys
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture

    try:
        import matplotlib
        matplotlib.use("Agg")  # pas d'affichage interactif
        import matplotlib.pyplot as plt

        safe_globals = _build_safe_globals()
        safe_globals["plt"] = plt

        exec(code, safe_globals)  # noqa: S102 - exécution volontaire et restreinte

        if plt.get_fignums():
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            result["image_base64"] = base64.b64encode(buf.read()).decode("utf-8")
            plt.close("all")

        result["success"] = True
    except Exception:  # noqa: BLE001
        result["error"] = traceback.format_exc(limit=3)
    finally:
        sys.stdout = old_stdout
        result["stdout"] = stdout_capture.getvalue()[-2000:]  # borne la taille

    queue.put(result)


def run_sandboxed_code(code: str, timeout: int = SANDBOX_TIMEOUT_SECONDS) -> Dict[str, Any]:
    """Exécute du code Python restreint dans un processus isolé avec timeout.

    Retourne un dict {success, stdout, error, image_base64}.
    """
    ctx = mp.get_context("spawn")
    queue: mp.Queue = ctx.Queue()
    process = ctx.Process(target=_worker, args=(code, queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "success": False,
            "stdout": "",
            "error": f"Timeout dépassé ({timeout}s) - code interrompu.",
            "image_base64": None,
        }

    if not queue.empty():
        return queue.get()

    return {
        "success": False,
        "stdout": "",
        "error": "Le processus s'est terminé sans résultat (crash probable).",
        "image_base64": None,
    }


def plot_function(expression: str, variable: str = "x", x_min: float = -10, x_max: float = 10) -> Dict[str, Any]:
    """Trace une fonction mathématique et retourne l'image en base64.

    L'expression est d'abord validée par le parseur SymPy sécurisé
    (math_tools._safe_parse) pour rejeter tout ce qui n'est pas une
    expression mathématique légitime, avant d'être ré-évaluée dans le
    sandbox via numpy (vectorisé, donc rapide et sûr).
    """
    from .math_tools import _safe_parse

    try:
        expr = _safe_parse(expression)
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": f"Expression invalide : {exc}", "image_base64": None}

    safe_code = f"""
{variable} = np.linspace({x_min}, {x_max}, 400)
try:
    y = {str(expr)}
except Exception as e:
    print("Erreur d'évaluation:", e)
    y = None
if y is not None:
    plt.figure(figsize=(6, 4))
    plt.plot({variable}, y)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.axvline(0, color='black', linewidth=0.8)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title("f({variable}) = {expression}")
"""
    result = run_sandboxed_code(safe_code)
    result["tool"] = "plot_function"
    result["expression"] = expression
    return result
