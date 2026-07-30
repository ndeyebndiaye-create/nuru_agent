"""
Client Gemini API pour LLM - Remplacement de Ollama
"""
import logging
import os
import google.generativeai as genai
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, model: str = "gemini-1.5-pro"):
        self.model_name = model
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.available = self._check_availability()
        
        if self.available:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"✅ LLM chargé: {self.model_name} (Gemini API)")
        else:
            logger.warning(f"⚠️ Gemini API non disponible (clé manquante)")
    
    def _check_availability(self) -> bool:
        """Vérifie si la clé API Gemini est configurée."""
        return bool(self.api_key)
    
    def generate(self, prompt: str, context: str = "", system_prompt: str = "") -> str:
        """Génère une réponse avec Gemini API.
        
        Args:
            prompt:        Instruction / question principale.
            context:       Contexte RAG injecté avant le prompt.
            system_prompt: Instruction système personnalisée. Si vide, utilise
                           le système par défaut (NURU tuteur générique).
        """
        if not self.available:
            return self._fallback_response(prompt)
        
        try:
            # Utiliser le system_prompt personnalisé si fourni, sinon le défaut.
            if system_prompt:
                active_system = system_prompt
            else:
                active_system = (
                    "Tu es NURU Tuteur IA, un assistant pédagogique spécialisé en Mathématiques "
                    "pour le programme de Terminale S1/S2 au Sénégal.\n"
                    "RÈGLE FONDAMENTALE : Tu dois te baser EXCLUSIVEMENT sur le contexte RAG fourni. "
                    "Ne complète JAMAIS avec tes connaissances générales. "
                    "Si une information n'est pas dans le contexte, ne l'invente pas et ne l'écris pas.\n"
                    "- Reformule et structure le contenu du contexte RAG en explications pédagogiques fluides.\n"
                    "- Développe les explications, ajoute des transitions naturelles entre les sections.\n"
                    "- N'invente jamais de formules, définitions, théorèmes ou exemples.\n"
                    "- N'UTILISE JAMAIS le format LaTeX (pas de $, $$, \\dfrac, \\int, \\lim, etc.). "
                    "Utilise une notation textuelle épurée avec symboles standards : "
                    "x², e^x, lim(x->0), int_a^b f(x)dx, u_n, f'(x), R, N, Z, C.\n"
                    "Réponds toujours en français, de manière pédagogique et structurée."
                )

            if context:
                user_content = (
                    f"Contexte RAG (extraits de cours Terminale S1/S2 Mathématiques):\n"
                    f"{context[:7000]}\n\n"
                    f"Instruction: {prompt}"
                )
            else:
                user_content = f"Instruction: {prompt}"
            
            # Use system_instruction parameter for Gemini
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=active_system
            )
            
            response = model.generate_content(
                user_content,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                    top_p=0.9,
                )
            )
            
            if response.text:
                return response.text
            return "Je n'ai pas pu générer de réponse."
            
        except Exception as e:
            logger.error(f"❌ Erreur Gemini API: {e}")
            return self._fallback_response(prompt, str(e))
    
    def _fallback_response(self, prompt: str, error: str = "") -> str:
        """Réponse de secours."""
        return f"""🤖 **NURU**

Question: *"{prompt}"*

📌 **Pour activer le LLM :**
1. Ajoute une clé API valide dans `.env` : `GEMINI_API_KEY=ta_cle_ici`
2. Relance l'API.

💡 **En attendant**, voici quelques conseils :
- Relis ton cours attentivement
- Essaie de reformuler le problème
- Utilise les exercices pour t'entraîner"""
    
    def list_models(self) -> List[str]:
        """Liste les modèles disponibles (mock pour compatibilité)."""
        return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
