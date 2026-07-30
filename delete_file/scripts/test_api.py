# scripts/test_api.py
"""
Test de l'API FastAPI.
"""
import sys
from pathlib import Path
import requests
import json
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8080"

def test_health():
    """Test l'endpoint de santé."""
    print("\n" + "=" * 80)
    print("🏥 TEST DE SANTÉ")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Réponse: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_chat():
    """Test l'endpoint de chat."""
    print("\n" + "=" * 80)
    print("💬 TEST DE CHAT")
    print("=" * 80)
    
    messages = [
        "Qu'est-ce qu'une dérivée ?",
        "Explique-moi la fonction exponentielle",
        "Donne-moi un exercice sur les dérivées"
    ]
    
    for message in messages:
        print(f"\n📝 Message: {message}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/",
                json={"message": message}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Intention: {data.get('intent', 'unknown')}")
                print(f"📊 Niveau: {data.get('level', 'unknown')}")
                print(f"📈 Confiance: {data.get('confidence', 0)}")
                print(f"\n📤 Réponse:")
                print(data.get('response', '')[:300] + "...")
            else:
                print(f"❌ Erreur: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        time.sleep(0.5)

def test_search():
    """Test l'endpoint de recherche."""
    print("\n" + "=" * 80)
    print("🔍 TEST DE RECHERCHE")
    print("=" * 80)
    
    queries = [
        "dérivée",
        "fonction exponentielle",
        "trigonométrie"
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/search",
                json={
                    "query": query,
                    "top_k": 3
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data.get('total', 0)} résultats")
                for i, result in enumerate(data.get('results', []), 1):
                    text = result.get('text', '')[:100]
                    print(f"   [{i}] {text}...")
            else:
                print(f"❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        time.sleep(0.5)

def test_session():
    """Test la gestion des sessions."""
    print("\n" + "=" * 80)
    print("📋 TEST DES SESSIONS")
    print("=" * 80)
    
    try:
        # Envoyer un message pour créer une session
        response = requests.post(
            f"{BASE_URL}/chat/",
            json={"message": "Bonjour NURU !"}
        )
        
        if response.status_code == 200:
            session_id = response.json().get('session_id')
            print(f"✅ Session créée: {session_id}")
            
            # Récupérer la session
            session_response = requests.get(
                f"{BASE_URL}/chat/session/{session_id}"
            )
            
            if session_response.status_code == 200:
                data = session_response.json()
                print(f"📊 Session: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Erreur récupération session: {session_response.status_code}")
        else:
            print(f"❌ Erreur création session: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 80)
    print("🧪 TEST DE L'API NURU")
    print("=" * 80)
    
    # Vérifier que l'API est en cours d'exécution
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ L'API n'est pas accessible")
            print("   Lancez d'abord: python -m backend.app.api.main")
            return
    except:
        print("❌ L'API n'est pas accessible")
        print("   Lancez d'abord: python -m backend.app.api.main")
        return
    
    # Menu
    while True:
        print("\n" + "=" * 80)
        print("📋 MENU DE TEST API")
        print("=" * 80)
        print("1. Test de santé")
        print("2. Test de chat")
        print("3. Test de recherche")
        print("4. Test de session")
        print("5. Tous les tests")
        print("6. Quitter")
        print("=" * 80)
        
        choice = input("\nVotre choix (1-6): ")
        
        if choice == "1":
            test_health()
        elif choice == "2":
            test_chat()
        elif choice == "3":
            test_search()
        elif choice == "4":
            test_session()
        elif choice == "5":
            test_health()
            test_chat()
            test_search()
            test_session()
        elif choice == "6":
            print("Au revoir!")
            break
        else:
            print("Choix invalide")

if __name__ == "__main__":
    main()