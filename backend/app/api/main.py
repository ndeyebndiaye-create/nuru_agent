"""
API NURU - Orchestrateur multi-agents LangGraph + RAG + LLM (Gemini API)

Ce module assemble l'application FastAPI complète :
- /chat            : chatbot élève, passe par le graphe LangGraph complet
                      (planner -> retriever -> [math_tool] -> cours/exercices/quiz
                      -> verifier -> progression)
- /evaluation      : correction de quiz/exercices + mise à jour de la maîtrise
- /health          : supervision

Un endpoint /chat/simple (RAG + LLM sans agents) est conservé pour un debug
rapide sans orchestration multi-agents ni mémoire PostgreSQL.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path
import sys
import logging

# ── Charger .env dès le démarrage (avant tout import qui lit os.getenv) ──
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent.parent.parent / ".env"
    load_dotenv(dotenv_path=_env_path, override=False)
except ImportError:
    pass  # python-dotenv optionnel

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NURU - Agent Tuteur IA (Terminale S1)", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------- routers
from backend.app.api.routes import chat as chat_routes
from backend.app.api.routes import health as health_routes
from backend.app.api.routes import evaluation as evaluation_routes
from backend.app.api.routes import teacher as teacher_routes
from backend.app.api.routes import auth as auth_routes
from backend.app.api.routes import parent as parent_routes
from backend.app.api.routes import admin as admin_routes
from backend.app.api.routes import student as student_routes
from backend.app.api.routes import generate as generate_routes

app.include_router(chat_routes.router)
app.include_router(health_routes.router)
app.include_router(evaluation_routes.router)
app.include_router(teacher_routes.router)
app.include_router(auth_routes.router)
app.include_router(parent_routes.router)
app.include_router(admin_routes.router)
app.include_router(student_routes.router)
app.include_router(generate_routes.router)


@app.on_event("startup")
async def on_startup():
    """Initialise la mémoire élève et le Super-Admin au démarrage.
    L'orchestrateur (modèle d'embeddings lourd) est chargé en arrière-plan
    pour ne pas bloquer le démarrage du serveur."""
    import asyncio

    try:
        from backend.app.memory import student_profile, auth_service

        student_profile.ensure_initialized()
        auth_service.ensure_super_admin()
    except Exception as exc:  # noqa: BLE001
        logger.warning("⚠️ Mémoire élève / admin non initialisée au démarrage: %s", exc)

    async def _warm_up_orchestrator():
        """Pré-charge l'orchestrateur + le modèle d'embeddings en arrière-plan."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            from backend.app.api.dependencies.containers import get_orchestrator
            await loop.run_in_executor(None, get_orchestrator)
            logger.info("✅ Orchestrateur pré-chargé en arrière-plan")
        except Exception as exc:  # noqa: BLE001
            logger.warning("⚠️ Orchestrateur non pré-chargé (sera réessayé à la 1ère requête): %s", exc)

    asyncio.create_task(_warm_up_orchestrator())


@app.get("/")
async def root():
    return {
        "name": "NURU - Agent Tuteur IA",
        "version": "4.0.0",
        "status": "running",
        "architecture": "LangGraph multi-agents (planner, retriever, cours, exercices, quiz, verifier, evaluation, progression)",
        "docs": "/docs",
    }


# ------------------------------------------------------- mode simple (debug)
@app.post("/chat/simple")
async def chat_simple(message: str = Query(...)):
    """Mode dégradé : RAG + LLM direct, sans passer par les agents
    LangGraph. Utile pour tester rapidement Qdrant/Gemini isolément."""
    from backend.app.rag.vector_indexer import HybridRetriever, VectorIndexerConfig
    from backend.app.llm.gemini_client import GeminiClient

    model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    llm = GeminiClient(model=model_name)
    retriever = HybridRetriever(VectorIndexerConfig.from_env())

    try:
        results = retriever.search(message, top_k=3)
        context = "\n\n".join([r.get("text", "") for r in results]) if results else ""
        sources = [r.get("metadata", {}).get("filename", "Source") for r in results[:3]] if results else []

        response = llm.generate(message, context)
        if sources:
            response += "\n\n---\n**Sources:**\n" + "\n".join(f"📖 {s}" for s in sources if s)

        return {"response": response, "sources": sources, "context_used": bool(context)}
    except Exception as e:  # noqa: BLE001
        logger.error(f"❌ Erreur /chat/simple: {e}")
        return {"response": f"❌ Erreur: {str(e)}"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))

    print("\n" + "=" * 80)
    print("🚀 NURU - Agent Tuteur IA (LangGraph multi-agents)")
    print("=" * 80)
    print(f"📍 API: http://localhost:{port}")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print("=" * 80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
