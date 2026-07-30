import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from backend.app.rag.vector_indexer import VectorIndexer, VectorIndexerConfig

config = VectorIndexerConfig.from_env()
indexer = VectorIndexer(config)

# Search for something
print("Testing Qdrant connection and search...")
try:
    results = indexer.search("limites et continuité", limit=3)
    print(f"Found {len(results)} results.")
    for res in results:
        meta = res.get("metadata", {})
        print(f"- {meta.get('filename')} | Score: {res.get('score')} | Type: {meta.get('doc_type', 'unknown')}")
except Exception as e:
    print(f"Error: {e}")

