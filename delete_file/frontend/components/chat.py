# frontend/components/chat.py
"""
Composant de chat Gradio.
"""
import gradio as gr
from typing import Tuple, Optional, Dict, Any
import json

from frontend.utils.api_client import APIClient

class ChatComponent:
    """
    Composant de chat pour NURU.
    """
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.chat_history = []
    
    def create_interface(self):
        """Crée l'interface de chat."""
        with gr.Tab("💬 Chat avec NURU"):
            gr.Markdown("""
            ## 🤖 NURU - Ton Tuteur IA Sénégalais
            
            **Discipline:** Mathématiques | **Classe:** Terminale S1
            
            Pose ta question et NURU te guidera pas à pas ! 📚
            """)
            
            # Historique du chat
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                bubble_full_width=False,
                avatar_images=("🧑‍🎓", "🤖")
            )
            
            # Input
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Écris ta question ici...",
                    label="Ta question",
                    scale=4
                )
                send_btn = gr.Button("🚀 Envoyer", scale=1, variant="primary")
            
            # Contrôles supplémentaires
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎯 Intention")
                    intent_display = gr.Textbox(label="", value="En attente...", interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Niveau d'aide")
                    level_display = gr.Textbox(label="", value="", interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📈 Confiance")
                    confidence_display = gr.Textbox(label="", value="", interactive=False)
            
            # Feedback
            with gr.Row():
                with gr.Column(scale=1):
                    rating = gr.Slider(
                        minimum=1, maximum=5, value=3, step=1,
                        label="⭐ Note la réponse"
                    )
                with gr.Column(scale=1):
                    helpful = gr.Checkbox(label="✅ Cette réponse t'a-t-elle aidé ?")
                with gr.Column(scale=2):
                    feedback = gr.Textbox(label="Commentaire (optionnel)", placeholder="Tes retours nous aident à nous améliorer...")
                with gr.Column(scale=1):
                    feedback_btn = gr.Button("📤 Envoyer feedback", variant="secondary")
            
            # Boutons rapides
            with gr.Row():
                quick_questions = [
                    "Explique-moi les dérivées",
                    "Qu'est-ce qu'une fonction exponentielle ?",
                    "Donne-moi un exercice sur les suites"
                ]
                for q in quick_questions:
                    gr.Button(q, size="sm")
            
            # Fonctions
            def process_message(message, history):
                if not message:
                    return history, "", "", "", ""
                
                # Ajouter le message utilisateur
                history = history or []
                history.append([message, None])
                
                # Appeler l'API
                response = self.api_client.chat(message)
                
                # Mettre à jour l'historique
                if history:
                    history[-1][1] = response.get("response", "Désolé, je n'ai pas compris.")
                
                # Mettre à jour les métadonnées
                intent = response.get("intent", "Inconnue")
                level = response.get("level", "")
                confidence = response.get("confidence", 0)
                
                confidence_text = f"{confidence*100:.1f}%" if confidence else ""
                
                return history, intent, level, confidence_text, ""
            
            def quick_question_click(q, history):
                return q, history
            
            def send_feedback(rating, helpful, comment):
                success = self.api_client.send_feedback(
                    rating=rating,
                    comment=comment,
                    helpful=helpful
                )
                if success:
                    return gr.update(value="✅ Merci pour ton feedback !")
                else:
                    return gr.update(value="❌ Erreur lors de l'envoi")
            
            # Événements
            msg.submit(
                process_message,
                [msg, chatbot],
                [chatbot, intent_display, level_display, confidence_display, msg]
            )
            
            send_btn.click(
                process_message,
                [msg, chatbot],
                [chatbot, intent_display, level_display, confidence_display, msg]
            )
            
            # Boutons rapides
            for btn in quick_questions:
                btn.click(
                    quick_question_click,
                    [gr.State(btn), chatbot],
                    [msg, chatbot]
                ).then(
                    process_message,
                    [msg, chatbot],
                    [chatbot, intent_display, level_display, confidence_display, msg]
                )
            
            feedback_btn.click(
                send_feedback,
                [rating, helpful, feedback],
                [feedback]
            )
        
        return chatbot