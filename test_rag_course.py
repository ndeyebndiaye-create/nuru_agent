import os
import sys

sys.path.insert(0, os.path.abspath("."))

from backend.app.agents.orchestrator import OrchestratorAgent

def main():
    print("Testing RAG and course generation...")
    orchestrator = OrchestratorAgent()
    
    # Query for a math concept
    response = orchestrator.process(
        user_message="Génère un cours sur la dérivation"
    )
        
    print("\n=== RESPONSE ===\n")
    print(response.get("response", ""))
    print("\n=== SOURCES ===\n")
    print(response.get("retrieved_docs", []))
    print("\n=== INTENT ===\n")
    print(response.get("intent", ""))

if __name__ == "__main__":
    main()
