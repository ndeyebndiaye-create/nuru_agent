"""
Client Ollama pour LLM local - llama3.2:1b
"""
import ollama
import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model
        self.available = self._check_availability()
        
        if self.available:
            logger.info(f"✅ LLM chargé: {self.model}")
        else:
            logger.warning(f"⚠️ Ollama non disponible")
    
    def _check_availability(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            ollama.list()
            return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama non disponible: {e}")
            return False
    
    def generate(self, prompt: str, context: str = "", system_prompt: str = "") -> str:
        """Génère une réponse avec Ollama.
        
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
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": active_system},
                    {"role": "user", "content": user_content}
                ],
                options={
                    "temperature": 0.1,
                    "num_predict": 4096,
                    "top_p": 0.9,
                    "num_ctx": 8192,
                    "repeat_penalty": 1.1,
                }
            )
            
            # ollama>=0.2 retourne un objet ChatResponse (pydantic), pas un dict
            if hasattr(response, "message"):
                return response.message.content or "Je n'ai pas pu générer de réponse."
            # Fallback dict (anciennes versions)
            return response.get("message", {}).get("content", "Je n'ai pas pu générer de réponse.")
            
        except Exception as e:
            logger.error(f"❌ Erreur Ollama: {e}")
            return self._fallback_response(prompt, str(e))
    
    def _fallback_response(self, prompt: str, error: str = "") -> str:
        """Réponse de secours."""
        return f"""🤖 **NURU**

Question: *"{prompt}"*

📌 **Pour activer le LLM :**
1. Lance Ollama : `ollama serve`
2. Télécharge le modèle : `ollama pull llama3.2:1b`

💡 **En attendant**, voici quelques conseils :
- Relis ton cours attentivement
- Essaie de reformuler le problème
- Utilise les exercices pour t'entraîner"""
    
    def list_models(self) -> List[str]:
        """Liste les modèles disponibles."""
        try:
            models = ollama.list()
            return [m.get("name", "unknown") for m in models.get("models", [])]
        except:
            return []
