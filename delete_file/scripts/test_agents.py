# scripts/test_agents.py
"""
Test des agents.
"""
import sys
from pathlib import Path
import json
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.agents import OrchestratorAgent, AgentConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_orchestrator():
    """Test l'orchestrateur."""
    
    print("\n" + "=" * 80)
    print("🧪 TEST DES AGENTS - NURU")
    print("=" * 80)
    
    # Configuration
    config = AgentConfig()
    orchestrator = OrchestratorAgent(config)
    
    # Messages de test
    test_messages = [
        "Qu'est-ce qu'une dérivée ?",
        "Explique-moi les fonctions exponentielles",
        "Donne-moi un exercice sur les dérivées",
        "Fais-moi un quiz sur la trigonométrie"
    ]
    
    print("\n📋 Tests avec différents types de requêtes:\n")
    print("=" * 80)
    
    for message in test_messages:
        print(f"\n📝 Utilisateur: {message}")
        print("-" * 40)
        
        try:
            result = orchestrator.process(message)
            
            print(f"🎯 Intention: {result.get('intent', 'unknown')}")
            print(f"📊 Niveau: {result.get('level', 'unknown')}")
            print(f"📈 Confiance: {result.get('confidence', 0.0):.2f}")
            
            response = result.get('response', '')
            print(f"\n📤 Réponse:")
            print("-" * 40)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print()
    
    print("=" * 80)
    print("✅ Test terminé!")

def test_agent_state():
    """Test l'état des agents."""
    print("\n" + "=" * 80)
    print("🧪 TEST DE L'ÉTAT DES AGENTS")
    print("=" * 80)
    
    from backend.app.agents.state import AgentState
    
    state = AgentState(
        user_message="Explique-moi les dérivées",
        context={"chapitre": "Dérivabilité"}
    )
    
    state.add_to_history("user", "Explique-moi les dérivées")
    state.add_to_history("assistant", "La dérivée est...")
    
    print("\n📊 État:")
    print(json.dumps(state.to_dict(), indent=2, ensure_ascii=False))

def test_planning():
    """Test le planificateur."""
    print("\n" + "=" * 80)
    print("🧪 TEST DU PLANIFICATEUR")
    print("=" * 80)
    
    from backend.app.agents.planner import PlannerAgent
    from backend.app.agents.state import AgentState
    
    planner = PlannerAgent()
    messages = [
        "Explique-moi les fonctions",
        "Résous cet exercice sur les dérivées",
        "Fais-moi un quiz",
        "Aide-moi, je suis bloqué"
    ]
    
    print("\n📋 Analyse des intentions:\n")
    
    for message in messages:
        state = AgentState(user_message=message)
        plan = planner.plan(state)
        
        print(f"📝 {message}")
        print(f"   Intention: {plan['intent']}")
        print(f"   Niveau: {plan['level']}")
        print(f"   Agents: {plan['required_agents']}")
        print(f"   Paramètres: {plan['parameters']}")
        print()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("📋 MENU DE TEST - AGENTS")
    print("=" * 80)
    print("1. Tester l'orchestrateur")
    print("2. Tester l'état des agents")
    print("3. Tester le planificateur")
    print("4. Quitter")
    print("=" * 80)
    
    choice = input("\nVotre choix (1-4): ")
    
    if choice == "1":
        test_orchestrator()
    elif choice == "2":
        test_agent_state()
    elif choice == "3":
        test_planning()
    else:
        print("Au revoir!")