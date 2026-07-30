# scripts/test_ingest.py
"""
Test du pipeline d'ingestion.
"""
import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.ingest_pipeline import IngestPipeline
from scripts.ingest_config import IngestConfig

def test_pipeline():
    """Test le pipeline sur un petit nombre de fichiers."""
    
    print("\n" + "=" * 80)
    print("🧪 TEST DU PIPELINE D'INGESTION")
    print("=" * 80)
    
    # Configuration de test
    config = IngestConfig(
        max_file_size_mb=100,
        skip_existing=False,
        save_chunks=True,
        max_chunks_per_file=100
    )
    
    # Exécuter le pipeline
    pipeline = IngestPipeline(config)
    pipeline.run(limit=2)  # Tester sur 2 fichiers

def test_components():
    """Test chaque composant individuellement."""
    print("\n" + "=" * 80)
    print("🧪 TEST DES COMPOSANTS")
    print("=" * 80)
    
    from backend.app.rag.document_parser import DocumentParser
    from backend.app.rag.chunker import ChunkingPipeline
    from backend.app.rag.metadata_extractor import MetadataMerger
    
    # 1. Document Parser
    print("\n📖 Test du Document Parser...")
    parser = DocumentParser(use_nougat=False)
    raw_dir = Path("data/raw")
    pdf_files = list(raw_dir.rglob("*.pdf"))
    
    if pdf_files:
        text = parser.extract(pdf_files[0])
        print(f"   ✅ {len(text)} caractères extraits")
    else:
        print("   ⚠️ Aucun PDF trouvé")
    
    # 2. Metadata Extractor
    print("\n📋 Test du Metadata Extractor...")
    merger = MetadataMerger()
    metadata = merger.extract_metadata(pdf_files[0], text) if pdf_files else {}
    print(f"   ✅ Métadonnées: {', '.join(metadata.keys())}")
    
    # 3. Chunker
    print("\n✂️ Test du Chunker...")
    chunker = ChunkingPipeline()
    chunks = chunker.process(text, metadata) if pdf_files else []
    print(f"   ✅ {len(chunks)} chunks créés")
    
    print("\n✅ Test des composants terminé!")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("📋 MENU DE TEST - PIPELINE")
    print("=" * 80)
    print("1. Tester le pipeline complet (2 fichiers)")
    print("2. Tester les composants individuellement")
    print("3. Quitter")
    print("=" * 80)
    
    choice = input("\nVotre choix (1-3): ")
    
    if choice == "1":
        test_pipeline()
    elif choice == "2":
        test_components()
    else:
        print("Au revoir!")