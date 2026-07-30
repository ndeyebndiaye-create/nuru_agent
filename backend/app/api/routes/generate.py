# backend/app/api/routes/generate.py
"""
Endpoint unifié de génération IA NURU.

Pipeline :
  Utilisateur → Classe + Chapitre
  → Recherche dans Qdrant (RAG)
  → Construction du contexte
  → Gemini API
  → Contenu structuré (cours / exercices / quiz)

Le RAG est la source principale.
Gemini structure, explique et reformule uniquement.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generate", tags=["Génération IA"])


# ─────────────────────────────────────────── Modèles Pydantic
class GenerateRequest(BaseModel):
    classe: str = Field(..., description="ex: Terminale")
    serie: Optional[str] = Field(None, description="ex: S1, S2")
    chapitre: str = Field(..., description="ex: Dérivation, Limites et continuité")
    content_type: str = Field(..., description="cours | exercices | quiz")
    num_questions: int = Field(5, ge=1, le=15)
    difficulty: str = Field("intermediate", description="easy | intermediate | hard")


class ChatGeminiRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    classe: Optional[str] = None
    chapitre: Optional[str] = None


# ─────────────────────────────────────────── Helpers RAG
def _get_retriever():
    """Retourne le retriever singleton (modèle déjà chargé si possible)."""
    try:
        from backend.app.api.dependencies.containers import get_retriever as _get_singleton
        r = _get_singleton()
        if r is not None:
            return r
    except Exception:
        pass
    # Fallback : créer un retriever local si le singleton n'est pas disponible
    from backend.app.rag.vector_indexer import HybridRetriever, VectorIndexerConfig
    return HybridRetriever(VectorIndexerConfig.from_env())


def _build_rag_context(chapitre: str, classe: str, serie: Optional[str] = None,
                       top_k: int = 8) -> tuple[str, list]:
    """Récupère les documents pertinents depuis Qdrant et construit le contexte."""
    try:
        retriever = _get_retriever()
        filters = {"classe": classe}
        if serie:
            filters["serie"] = serie

        # Recherche avec filtre classe, repli sans filtre si vide
        docs = retriever.search_by_metadata(chapitre, filters, top_k=top_k)
        if not docs:
            docs = retriever.search(chapitre, top_k=top_k)

        # Construire le contexte texte
        parts = []
        for doc in docs[:6]:
            text = doc.get("text", "").strip()
            meta = doc.get("metadata", {})
            chap = meta.get("chapitre", "")
            src = meta.get("filename", "")
            header = f"[{chap or chapitre}{' — ' + src if src else ''}]"
            if text:
                parts.append(f"{header}\n{text}")

        context = "\n\n".join(parts)[:5000]
        sources = list({doc.get("metadata", {}).get("filename", "") for doc in docs[:6] if doc.get("metadata", {}).get("filename")})
        return context, sources

    except Exception as exc:
        logger.warning("⚠️ RAG indisponible: %s", exc)
        return "", []


# ─────────────────────────────────────────── Gemini client
def _call_gemini(prompt: str) -> str:
    """Appelle Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY manquante.")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.1-pro-preview")
        response = model.generate_content(prompt)
        return response.text or ""
    except Exception as e:
        logger.error(f"Erreur Gemini: {e}")
        raise ValueError(f"Erreur de l'API Gemini: {e}")


# ─────────────────────────────────────────── Prompts
def _build_cours_prompt(chapitre: str, classe: str, serie: Optional[str], context: str) -> str:
    level_label = f"{classe} {serie}".strip() if serie else classe

    rag_section = (
        f"## Documents du corpus RAG (programme officiel sénégalais) :\n\n{context}\n"
        if context
        else "⚠️ Aucun document RAG trouvé pour ce chapitre — complète uniquement depuis tes connaissances du programme."
    )

    return f"""Tu es NURU, un tuteur IA expert en Mathématiques pour le programme officiel sénégalais ({level_label}).
Ta mission : rédiger un **cours complet de qualité manuel scolaire** sur le chapitre demandé.

{rag_section}

---

## RÈGLES ABSOLUES

### Anti-hallucination
- Appuie-toi IMPÉRATIVEMENT sur les documents RAG fournis.
- Si une notion absente du RAG est ajoutée, indique-le par *(complément hors RAG)*.
- N'invente jamais de théorèmes, de formules ou d'exemples non justifiés.

### Règles LaTeX (OBLIGATOIRES, sans exception)
- **Variables et symboles inline** : toujours dans `$...$`  
  Exemple : la fonction $f$, l'entier $n$, l'intervalle $[a, b]$
- **Équations centrées** : sur une ligne isolée avec `$$...$$`  
  Exemple :
  $$\\int_{{a}}^{{b}} f(x)\\,dx = F(b) - F(a)$$
- **Parenthèses/crochets extensibles** : utilise systématiquement `\\left(... \\right)`, `\\left[... \\right]`, `\\left\\{{... \\right\\}}`
- **Fractions** : `\\dfrac{{numérateur}}{{dénominateur}}` (jamais a/b en texte brut)
- **Limites** : `\\lim_{{x \\to a}}`, `\\lim_{{n \\to +\\infty}}`
- **Intégrales** : `\\int_{{a}}^{{b}} f(x)\\,dx`
- **Normes, valeurs absolues** : `\\left|... \\right|`
- **Vecteurs** : `\\vec{{u}}`, `\\overrightarrow{{AB}}`
- **Ensembles** : `\\mathbb{{R}}`, `\\mathbb{{N}}`, `\\mathbb{{Z}}`, `\\mathbb{{C}}`
- **Flèches logiques** : `\\Rightarrow`, `\\Leftrightarrow`, `\\forall`, `\\exists`
- Aucun symbole mathématique ne doit apparaître en texte brut (ni →, ni ∈, ni ², ni ≤ etc.)

---

## STRUCTURE OBLIGATOIRE DU COURS

Produis un cours **très long, très détaillé**, structuré exactement ainsi :

# {chapitre}
## Programme : {level_label} — Mathématiques

---

## 📌 Introduction

*(2–3 paragraphes situant le chapitre dans le programme, expliquant son utilité et sa place dans la progression pédagogique.)*

---

## 🎯 Objectifs du chapitre

*(Liste numérotée de 4 à 6 objectifs précis et mesurables, en termes de savoir-faire.)*

---

## 📖 I. Rappels et prérequis

*(Notions déjà vues nécessaires à la compréhension du chapitre, avec formules de rappel.)*

---

## 📚 II. Définitions fondamentales

*(Au moins 3 définitions rigoureuses, chacune dans un bloc de citation Markdown `> **Définition :** ...`)*

---

## 🔬 III. Théorèmes et propriétés

*(Au moins 3 théorèmes/propriétés numérotés, chacun dans un bloc `> **Théorème X :** ...` suivi d'une démonstration ou d'une justification intuitive.)*

---

## 🛠️ IV. Méthodes et techniques de résolution

*(Pour chaque méthode : une description étape par étape numérotée, puis une application immédiate.)*

---

## ✏️ V. Exemples résolus et commentés

*(Au moins 3 exemples complets, avec énoncé, démarche détaillée, calculs intermédiaires et conclusion. Chaque étape doit être expliquée en français.)*

---

## ⚠️ VI. Pièges courants et erreurs à éviter

*(Liste des erreurs typiques d'élèves, avec contre-exemples et corrections.)*

---

## 📝 VII. Résumé — À retenir

*(Synthèse des points essentiels sous forme de liste à puces ou tableau récapitulatif.)*

---

## 📚 Sources et références

*(Mentionne les documents RAG utilisés (titres/fichiers) et indique si des compléments ont été ajoutés.)*

---

Génère maintenant le cours complet sur **{chapitre}** pour la classe {level_label} du programme sénégalais.
Le cours doit être suffisamment long et détaillé pour qu'un élève puisse l'utiliser comme seule référence pour préparer un examen.
"""


def _build_exercices_prompt(chapitre: str, classe: str, serie: Optional[str],
                             context: str, difficulty: str) -> str:
    level_label = f"{classe} {serie}".strip() if serie else classe
    diff_label = {"easy": "facile", "intermediate": "intermédiaire", "hard": "difficile"}.get(difficulty, "intermédiaire")
    rag_section = f"## Documents du corpus RAG (programme officiel) :\n{context}" if context else "⚠️ Aucun document RAG disponible."

    return f"""Tu es NURU, tuteur IA Mathématiques pour {level_label} au Sénégal.

{rag_section}

---

## RÈGLES LATEX OBLIGATOIRES
- Variables inline : `$...$` — ex : la dérivée $f'(x)$, l'entier $n \\in \\mathbb{{N}}$
- Équations centrées : `$$...$$` sur une ligne isolée
- Parenthèses extensibles : `\\left(... \\right)`, `\\left[... \\right]`
- Fractions : `\\dfrac{{a}}{{b}}` (jamais a/b en texte brut)
- Ensembles : `\\mathbb{{R}}`, `\\mathbb{{N}}`, `\\mathbb{{Z}}`, `\\mathbb{{C}}`
- Aucun symbole brut : ni →, ni ∈, ni ², ni ≤

---

Génère 3 exercices de niveau **{diff_label}** sur le chapitre : **{chapitre}**

Chaque exercice doit :
- Être tiré du programme sénégalais {level_label}
- Avoir un énoncé clair et complet avec toutes les données
- Comporter 2 à 3 questions progressives
- Avoir une correction **très détaillée**, étape par étape, avec justification de chaque calcul

FORMAT IMPÉRATIF (JSON valide) :
```json
{{
  "chapitre": "{chapitre}",
  "difficulte": "{difficulty}",
  "exercices": [
    {{
      "numero": 1,
      "titre": "Titre descriptif de l'exercice",
      "enonce": "Énoncé complet avec contexte et données en KaTeX",
      "questions": [
        "1) Première question avec formules en $...$",
        "2) Deuxième question",
        "3) Troisième question (si applicable)"
      ],
      "correction": "**Correction complète :**\n\n**Question 1)**\nDémarche étape par étape avec tous les calculs en KaTeX.\n\n**Question 2)**\nDémarche étape par étape.",
      "notion_cle": "Notion principale testée"
    }}
  ]
}}
```

Règles strictes :
- Exercices réalistes et conformes au programme {level_label} sénégalais
- Toutes les formules en KaTeX strict
- Corrections complètes, pédagogiques, expliquant le raisonnement
- Pas d'exercices fictifs ou hors programme"""


def _build_quiz_prompt(chapitre: str, classe: str, serie: Optional[str],
                        context: str, num_questions: int) -> str:
    level_label = f"{classe} {serie}".strip() if serie else classe
    rag_section = f"## Documents du corpus RAG (programme officiel) :\n{context}" if context else "⚠️ Aucun document RAG disponible."

    return f"""Tu es NURU, tuteur IA Mathématiques pour {level_label} au Sénégal.

{rag_section}

---

## RÈGLES LATEX OBLIGATOIRES
- Formules inline : `$...$` — ex : la limite $\\lim_{{x \\to 0}} f(x)$
- Équations centrées : `$$...$$` sur une ligne isolée
- Fractions : `\\dfrac{{a}}{{b}}`
- Ensembles : `\\mathbb{{R}}`, `\\mathbb{{N}}`, `\\mathbb{{Z}}`, `\\mathbb{{C}}`
- Aucun symbole brut

---

Génère un quiz de **{num_questions} questions QCM** sur : **{chapitre}** pour le niveau {level_label}.

Chaque question doit :
- Porter sur une notion précise du chapitre
- Avoir exactement 4 propositions (A, B, C, D) plausibles et bien formulées
- Avoir une explication pédagogique détaillée de la bonne réponse

FORMAT IMPÉRATIF (JSON valide) :
```json
{{
  "chapitre": "{chapitre}",
  "nb_questions": {num_questions},
  "questions": [
    {{
      "id": 1,
      "question": "Énoncé clair de la question, formules en $...$",
      "choices": [
        {{"id": "A", "text": "Proposition A avec formule si nécessaire"}},
        {{"id": "B", "text": "Proposition B"}},
        {{"id": "C", "text": "Proposition C"}},
        {{"id": "D", "text": "Proposition D"}}
      ],
      "correct_answer": "A",
      "explanation": "Explication pédagogique complète justifiant la bonne réponse et réfutant les autres propositions."
    }}
  ]
}}
```

Règles strictes :
- Questions pertinentes et conformes au programme {level_label} sénégalais
- Une seule bonne réponse par question
- Propositions incorrectes plausibles (erreurs courantes d'élèves)
- Explications pédagogiques détaillées
- Formules en KaTeX strict"""


# ─────────────────────────────────────────── Parse JSON helper
def _extract_json_block(text: str) -> dict:
    """Extrait le premier bloc JSON valide d'une réponse Gemini."""
    import json, re
    # Chercher un bloc ```json ... ```
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Fallback : chercher { ... } directement
    match2 = re.search(r"\{[\s\S]*\}", text)
    if match2:
        try:
            return json.loads(match2.group(0))
        except json.JSONDecodeError:
            pass
    return {}


# ─────────────────────────────────────────── Routes
@router.post("/content")
async def generate_content(payload: GenerateRequest):
    """
    Génération unifiée : cours, exercices ou quiz.
    Pipeline : Classe+Chapitre → RAG → Gemini → Contenu structuré.
    """
    if payload.content_type not in ("cours", "exercices", "quiz"):
        raise HTTPException(400, "content_type doit être : cours | exercices | quiz")

    # 1. RAG — top_k plus élevé pour les cours afin d'avoir un maximum de contexte
    top_k = 12 if payload.content_type == "cours" else 8
    context, sources = _build_rag_context(
        payload.chapitre, payload.classe, payload.serie, top_k=top_k
    )

    # 2. Construire le prompt selon le type
    if payload.content_type == "cours":
        prompt = _build_cours_prompt(payload.chapitre, payload.classe, payload.serie, context)
    elif payload.content_type == "exercices":
        prompt = _build_exercices_prompt(payload.chapitre, payload.classe, payload.serie,
                                         context, payload.difficulty)
    else:
        prompt = _build_quiz_prompt(payload.chapitre, payload.classe, payload.serie,
                                     context, payload.num_questions)

    # 3. Gemini
    try:
        raw = _call_gemini(prompt)
    except ValueError as e:
        raise HTTPException(503, f"Gemini API non configurée : {e}")
    except Exception as e:
        raise HTTPException(503, f"Erreur Gemini : {e}")

    # 4. Formater la réponse
    if payload.content_type == "cours":
        return {
            "content_type": "cours",
            "classe": payload.classe,
            "serie": payload.serie,
            "chapitre": payload.chapitre,
            "markdown": raw,
            "sources": sources,
            "rag_used": bool(context),
        }
    else:
        parsed = _extract_json_block(raw)
        if not parsed:
            # Fallback si JSON non parsé
            parsed = {"raw": raw}
        return {
            "content_type": payload.content_type,
            "classe": payload.classe,
            "serie": payload.serie,
            "chapitre": payload.chapitre,
            "sources": sources,
            "rag_used": bool(context),
            **parsed,
        }


@router.post("/chat")
async def chat_with_gemini(payload: ChatGeminiRequest):
    """
    Chatbot corrigé : RAG → Gemini.
    Récupère le contexte depuis Qdrant, construit un prompt et appelle Gemini.
    """
    # 1. RAG
    query = payload.message
    chapitre_hint = payload.chapitre or ""
    classe = payload.classe or "Terminale"

    context, sources = _build_rag_context(
        f"{chapitre_hint} {query}".strip(), classe, top_k=5
    )

    # 2. Prompt chatbot
    rag_section = f"## Contexte RAG (programme officiel) :\n{context}" if context else ""
    prompt = f"""Tu es NURU, un tuteur IA spécialisé en Mathématiques pour le programme sénégalais de Terminale S1/S2.

{rag_section}

---

Question de l'élève : {payload.message}

INSTRUCTIONS :
- Réponds en t'appuyant PRIORITAIREMENT sur le contexte RAG fourni
- Si l'information est dans le RAG, cite-la et développe à partir de celle-ci
- Si la notion n'est pas dans le RAG, utilise tes connaissances du programme de Terminale et indique que tu complétes au-delà du RAG
- Formules en KaTeX : $...$ (inline) et $$...$$ (bloc)
- Réponds en français, style pédagogique, concis et clair
- Tu peux donner des définitions, résumés, expliquer des notions du programme

Réponds maintenant :"""

    try:
        response_text = _call_gemini(prompt)
    except ValueError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        logger.error("Erreur Gemini chat : %s", e)
        raise HTTPException(503, f"Erreur Gemini : {e}")

    return {
        "response": response_text,
        "sources": sources,
        "rag_used": bool(context),
        "session_id": payload.session_id,
    }


@router.get("/chapitres")
async def get_chapitres():
    """Retourne la liste des chapitres disponibles dans le corpus RAG."""
    return {
        "chapitres": [
            "Révisions de trigonométrie",
            "Dérivabilité",
            "Limites et continuité",
            "Fonctions exponentielles",
            "Fonctions logarithmes",
            "Calcul intégral",
            "Suites numériques",
            "Nombres complexes",
            "Similitudes planes directes",
            "Probabilités",
            "Dénombrement",
            "Courbes paramétrées",
            "Arithmétique",
            "Équations différentielles",
            "Géométrie dans l'espace",
            "Transformations et isométries",
            "Les angles",
            "Fonctions scalaires et vectorielles — Leibniz",
            "Coniques",
            "Étude de fonctions",
            "Primitives",
            "Dérivation et étude de fonctions",
        ],
        "classes": ["Terminale"],
        "series": ["S1", "S2", "S3", "L1", "L2"],
    }
