
"""
Test du chunker pédagogique.
"""
import sys
from pathlib import Path
import json

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# IMPORT CORRECT : backend.app.rag.chunker
try:
    from backend.app.rag.chunker import PedagogicalChunker, ChunkingPipeline, ChunkerConfig
    print("✅ Importation réussie")
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    print("\n📁 Structure attendue:")
    print("   backend/")
    print("   └── app/")
    print("       └── rag/")
    print("           └── chunker/")
    print("               ├── __init__.py")
    print("               ├── config.py")
    print("               └── pedagogical_chunker.py")
    sys.exit(1)

def test_chunker():
    """Test du chunker."""
    print("\n" + "=" * 80)
    print("🧪 TEST DU CHUNKER PÉDAGOGIQUE - NURU")
    print("=" * 80)
    
    # Texte de test
    test_text = """
# Chapitre 1 : Les Nombres Réels

## 1.1 Définition

**Définition 1 :** Un nombre réel est un nombre qui peut être représenté par un point sur une droite graduée.

**Propriété 1 :** L'ensemble des nombres réels est noté ℝ.

### Exemple 1 :
Les nombres -3, 0, 1/2, π sont des nombres réels.

## 1.2 Opérations sur les nombres réels

**Théorème 1 :** Pour tous nombres réels a, b, c, on a :
- a + b = b + a (commutativité)
- (a + b) + c = a + (b + c) (associativité)

**Exercice 1 :**
Calculer les expressions suivantes :
1) 3 + (-5) × 2
2) (7 - 3) ÷ 2

**Solution :**
1) 3 + (-5) × 2 = 3 - 10 = -7
2) (7 - 3) ÷ 2 = 4 ÷ 2 = 2
"""
    
    metadata = {
        "source": "test.md",
        "chapitre": "Les Nombres Réels",
        "chapitre_numero": 1,
        "discipline": "mathématiques",
        "classe": "Terminale",
        "serie": "S1"
    }
    
    # Configuration
    config = ChunkerConfig(
        min_chunk_size=50,
        max_chunk_size=1000,
        ideal_chunk_size=400
    )
    
    print("\n📋 Configuration:")
    print(f"   Taille min: {config.min_chunk_size}")
    print(f"   Taille max: {config.max_chunk_size}")
    
    # Exécuter le chunking
    pipeline = ChunkingPipeline(config)
    chunks = pipeline.process(test_text, metadata)
    
    print(f"\n📊 Résultats: {len(chunks)} chunks créés\n")
    print("-" * 80)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[{i}] TYPE: {chunk.get('chunk_type', 'unknown')}")
        print(f"    CATÉGORIE: {chunk.get('metadata', {}).get('chunk_category', 'unknown')}")
        print(f"    DIFFICULTÉ: {chunk.get('metadata', {}).get('difficulty_level', 'unknown')}")
        print(f"    COMPÉTENCES: {chunk.get('metadata', {}).get('competences', [])}")
        print(f"    TEXTE: {chunk.get('text', '')[:150]}...")
        print("-" * 40)
    
    # Sauvegarder
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "chunks_demo.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés: {output_file}")
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_chunker()