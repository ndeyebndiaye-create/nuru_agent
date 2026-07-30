# frontend/gradio_app.py
"""
Interface Gradio NURU — remplace le prototype Flask comme interface
principale, conformément au cahier des charges (Gradio -> FastAPI ->
LangGraph -> Qdrant -> LLM local).

Structure :
- Espace Élève : Tableau de bord, Cours, Exercices, Quiz, Progression,
  Carte des compétences, Profil (chaque section a son propre chatbot pour
  Cours/Exercices/Quiz, comme demandé).
- Espace Enseignant : authentification séparée, génération de cours,
  suivi des élèves liés, statistiques de classe.
"""
from __future__ import annotations

import os
import uuid
from typing import List, Tuple

import gradio as gr
import requests

API_URL = os.getenv("API_URL", "http://localhost:8080")
TIMEOUT = 180


# --------------------------------------------------------------------- API

def _post(path: str, json: dict | None = None) -> dict:
    try:
        resp = requests.post(f"{API_URL}{path}", json=json or {}, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _get(path: str) -> dict:
    try:
        resp = requests.get(f"{API_URL}{path}", timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _chat_call(message: str, session_id: str, user_id: str) -> Tuple[str, str]:
    result = _post("/chat/", {"message": message, "session_id": session_id, "user_id": user_id or None})
    if "error" in result:
        return f"⚠️ NURU n'a pas pu joindre l'API ({result['error']}). Vérifie que l'API tourne (`python -m backend.app.api.main`).", session_id
    return result.get("response", ""), result.get("session_id", session_id)


# ---------------------------------------------------------- Espace Élève

def make_chat_fn(user_id_state: gr.State, session_state: gr.State):
    def _fn(message: str, history: List[dict], user_id: str, session_id: str):
        session_id = session_id or str(uuid.uuid4())
        response, session_id = _chat_call(message, session_id, user_id)
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
        ]
        return history, "", session_id
    return _fn


def refresh_progression(user_id: str):
    if not user_id:
        return "Renseigne ton identifiant dans l'onglet Profil pour voir ta progression.", "—"
    data = _get(f"/chat/progression/{user_id}")
    if "error" in data or not data:
        return "Pas encore de données de progression (commence par discuter avec NURU !).", "—"

    mastery = data.get("mastery", [])
    if not mastery:
        rows = "Aucune notion travaillée pour l'instant."
    else:
        rows = "\n".join(
            f"- **{m['concept']}** ({m.get('chapitre') or '—'}) : {int(m['mastery_score']*100)}% de maîtrise "
            f"({m['attempts']} tentative(s))"
            for m in mastery
        )
    next_step = data.get("next_step", {})
    next_text = f"👉 **Prochaine étape suggérée :** {next_step.get('reason', '')}"
    return rows, next_text


def refresh_badges(user_id: str):
    if not user_id:
        return "Renseigne ton identifiant dans l'onglet Profil."
    data = _get(f"/chat/badges/{user_id}")
    badges = data.get("badges", [])
    if not badges:
        return "🏅 Aucun badge débloqué pour l'instant. Continue à t'entraîner !"
    return "\n".join(f"### {b['label']}\n{b['description']}" for b in badges)


def refresh_competency_map(user_id: str):
    if not user_id:
        return "Renseigne ton identifiant dans l'onglet Profil."
    data = _get(f"/chat/competency-map/{user_id}")
    nodes = data.get("nodes", [])
    if not nodes:
        return "Carte des compétences vide pour l'instant — elle se remplit au fil de tes échanges avec NURU."

    status_emoji = {"maitrise": "🟢", "en_cours": "🟡", "faible": "🟠", "non_commence": "⚪"}
    lines = ["| Chapitre | Notion | Maîtrise | Statut |", "|---|---|---|---|"]
    for n in nodes:
        lines.append(
            f"| {n.get('chapitre') or '—'} | {n['concept']} | {int(n['mastery_score']*100)}% | "
            f"{status_emoji.get(n['status'], '')} {n['status']} |"
        )
    return "\n".join(lines)


def build_student_space() -> gr.Blocks:
    with gr.Blocks(title="NURU — Espace Élève") as student_app:
        gr.Markdown("# 🇸🇳 NURU — Tuteur IA · Mathématiques Terminale S1")

        user_id_state = gr.State("")
        session_state = gr.State(str(uuid.uuid4()))

        with gr.Tabs():
            with gr.Tab("🏠 Tableau de bord"):
                gr.Markdown(
                    "Bienvenue sur NURU ! Utilise les onglets **Cours**, **Exercices** et "
                    "**Quiz** pour discuter avec ton tuteur IA, puis suis ta **Progression**, "
                    "ta **Carte des compétences** et tes badges."
                )
                dash_progression = gr.Markdown()
                dash_badges = gr.Markdown()
                refresh_dash_btn = gr.Button("🔄 Actualiser")

            with gr.Tab("📚 Cours"):
                cours_chat = gr.Chatbot(label="Chatbot Cours", height=420, type="messages")
                cours_msg = gr.Textbox(placeholder="Ex: Explique-moi les nombres complexes", label="Ta question")
                cours_send = gr.Button("Envoyer", variant="primary")

            with gr.Tab("✍️ Exercices"):
                exo_chat = gr.Chatbot(label="Chatbot Exercices", height=420, type="messages")
                exo_msg = gr.Textbox(placeholder="Ex: Génère-moi un exercice sur les intégrales", label="Ta demande")
                exo_send = gr.Button("Envoyer", variant="primary")

            with gr.Tab("📋 Quiz"):
                quiz_chat = gr.Chatbot(label="Chatbot Quiz", height=420, type="messages")
                quiz_msg = gr.Textbox(placeholder="Ex: Crée-moi un quiz sur les suites numériques", label="Ta demande")
                quiz_send = gr.Button("Envoyer", variant="primary")

            with gr.Tab("📈 Progression"):
                prog_md = gr.Markdown()
                prog_next = gr.Markdown()
                prog_refresh = gr.Button("🔄 Actualiser ma progression")

            with gr.Tab("🗺️ Carte des compétences"):
                map_md = gr.Markdown()
                map_refresh = gr.Button("🔄 Actualiser la carte")

            with gr.Tab("🏅 Badges"):
                badges_md = gr.Markdown()
                badges_refresh = gr.Button("🔄 Actualiser mes badges")

            with gr.Tab("👤 Profil"):
                gr.Markdown("Renseigne un identifiant (ex: ton nom ou email) pour que NURU retienne ta progression d'une session à l'autre.")
                user_id_input = gr.Textbox(label="Mon identifiant élève", placeholder="ex: binta.ndiaye")
                save_profile_btn = gr.Button("Enregistrer")
                profile_status = gr.Markdown()

        # ------------------------------------------------------------ wiring

        def _save_profile(uid):
            return uid, f"✅ Identifiant enregistré : **{uid}**" if uid else "⚠️ Identifiant vide."

        save_profile_btn.click(_save_profile, inputs=[user_id_input], outputs=[user_id_state, profile_status])

        chat_fn = make_chat_fn(user_id_state, session_state)
        cours_send.click(chat_fn, [cours_msg, cours_chat, user_id_state, session_state], [cours_chat, cours_msg, session_state])
        cours_msg.submit(chat_fn, [cours_msg, cours_chat, user_id_state, session_state], [cours_chat, cours_msg, session_state])

        exo_send.click(chat_fn, [exo_msg, exo_chat, user_id_state, session_state], [exo_chat, exo_msg, session_state])
        exo_msg.submit(chat_fn, [exo_msg, exo_chat, user_id_state, session_state], [exo_chat, exo_msg, session_state])

        quiz_send.click(chat_fn, [quiz_msg, quiz_chat, user_id_state, session_state], [quiz_chat, quiz_msg, session_state])
        quiz_msg.submit(chat_fn, [quiz_msg, quiz_chat, user_id_state, session_state], [quiz_chat, quiz_msg, session_state])

        prog_refresh.click(refresh_progression, [user_id_state], [prog_md, prog_next])
        map_refresh.click(refresh_competency_map, [user_id_state], [map_md])
        badges_refresh.click(refresh_badges, [user_id_state], [badges_md])

        def _refresh_dashboard(uid):
            rows, _ = refresh_progression(uid)
            badges = refresh_badges(uid)
            return rows, badges

        refresh_dash_btn.click(_refresh_dashboard, [user_id_state], [dash_progression, dash_badges])

    return student_app


# ------------------------------------------------------- Espace Enseignant

def build_teacher_space() -> gr.Blocks:
    with gr.Blocks(title="NURU — Espace Enseignant") as teacher_app:
        gr.Markdown("# 👩🏾‍🏫 NURU — Espace Enseignant")

        teacher_id_state = gr.State("")

        with gr.Tabs():
            with gr.Tab("🔐 Connexion / Inscription"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Se connecter")
                        login_email = gr.Textbox(label="Email")
                        login_password = gr.Textbox(label="Mot de passe", type="password")
                        login_btn = gr.Button("Se connecter", variant="primary")
                    with gr.Column():
                        gr.Markdown("### Créer un compte")
                        reg_email = gr.Textbox(label="Email")
                        reg_password = gr.Textbox(label="Mot de passe (6+ caractères)", type="password")
                        reg_name = gr.Textbox(label="Nom")
                        reg_btn = gr.Button("Créer mon compte")
                auth_status = gr.Markdown()

            with gr.Tab("👥 Mes élèves"):
                link_student_id = gr.Textbox(label="Identifiant élève à suivre")
                link_btn = gr.Button("Lier cet élève")
                students_md = gr.Markdown()
                refresh_students_btn = gr.Button("🔄 Actualiser la liste")

            with gr.Tab("📊 Statistiques de classe"):
                stats_md = gr.Markdown()
                stats_refresh_btn = gr.Button("🔄 Actualiser les statistiques")

            with gr.Tab("📖 Génération de cours"):
                gen_concept = gr.Textbox(label="Concept / chapitre", placeholder="ex: Dérivation")
                gen_btn = gr.Button("Générer le cours", variant="primary")
                gen_output = gr.Markdown()

        def _login(email, password):
            result = _post("/teacher/login", {"email": email, "password": password})
            if "error" in result or "id" not in result:
                return "", f"❌ Connexion échouée : {result.get('detail', result.get('error', 'erreur inconnue'))}"
            return result["id"], f"✅ Connecté·e en tant que {result.get('name') or result['email']}"

        def _register(email, password, name):
            result = _post("/teacher/register", {"email": email, "password": password, "name": name})
            if "error" in result or "teacher_id" not in result:
                return "", f"❌ Inscription échouée : {result.get('detail', result.get('error', 'erreur inconnue'))}"
            return result["teacher_id"], f"✅ Compte créé pour {email}. Tu es maintenant connecté·e."

        login_btn.click(_login, [login_email, login_password], [teacher_id_state, auth_status])
        reg_btn.click(_register, [reg_email, reg_password, reg_name], [teacher_id_state, auth_status])

        def _link_student(teacher_id, student_external_id):
            if not teacher_id:
                return "⚠️ Connecte-toi d'abord."
            _post("/teacher/link-student", {"teacher_id": teacher_id, "student_external_id": student_external_id})
            return f"✅ Élève « {student_external_id} » lié à ton compte."

        def _list_students(teacher_id):
            if not teacher_id:
                return "⚠️ Connecte-toi d'abord."
            data = _get(f"/teacher/students/{teacher_id}")
            students = data.get("students", [])
            if not students:
                return "Aucun élève lié pour l'instant."
            return "\n".join(f"- {s.get('name') or s['external_user_id']} ({s['classe']} {s['serie']})" for s in students)

        link_btn.click(_link_student, [teacher_id_state, link_student_id], [students_md])
        refresh_students_btn.click(_list_students, [teacher_id_state], [students_md])

        def _class_stats(teacher_id):
            if not teacher_id:
                return "⚠️ Connecte-toi d'abord."
            data = _get(f"/teacher/class-stats/{teacher_id}")
            if "error" in data:
                return f"⚠️ {data['error']}"
            summary = data.get("class_summary", {})
            lines = [
                f"**Nombre d'élèves suivis :** {data.get('nb_students', 0)}",
                f"**Score moyen de la classe :** {int(summary.get('average_score', 0) * 100)}%",
            ]
            weak = summary.get("weak_chapters", [])
            if weak:
                lines.append("\n**⚠️ Chapitres à renforcer :**")
                lines += [f"- {w['chapitre']} ({int(w['average_score']*100)}%)" for w in weak]
            return "\n".join(lines)

        stats_refresh_btn.click(_class_stats, [teacher_id_state], [stats_md])

        def _generate_course(concept):
            if not concept:
                return "⚠️ Renseigne un concept."
            result = _post("/teacher/generate-course", {"concept": concept})
            if "error" in result:
                return f"⚠️ {result['error']}"
            return result.get("explanation", "Pas de contenu généré.")

        gen_btn.click(_generate_course, [gen_concept], [gen_output])

    return teacher_app


# ------------------------------------------------------------------- main

def build_app() -> gr.Blocks:
    with gr.Blocks(title="NURU — Agent Tuteur IA") as app:
        gr.Markdown("## 🇸🇳 NURU — Plateforme d'apprentissage IA (Terminale S1)")
        with gr.Tabs():
            with gr.Tab("🎓 Espace Élève"):
                build_student_space()
            with gr.Tab("👩🏾‍🏫 Espace Enseignant"):
                build_teacher_space()
    return app


# Instance de niveau module : permet `gradio frontend/gradio_app.py` (hot-reload)
# et le déploiement Hugging Face Spaces (qui exécute app.py et cherche `demo`).
demo = build_app()
demo.queue()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("GRADIO_PORT", 7860)))
