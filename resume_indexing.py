import sys
import json
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from backend.app.rag.vector_indexer import VectorIndexer, VectorIndexerConfig
from scripts.ingest_config import IngestConfig

def main():
    print("Loading chunks from data/processed/chunks...")
    chunks_dir = Path("data/processed/chunks")
    
    latest_chunks = {}
    for p in chunks_dir.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                src = data.get("source")
                timestamp = data.get("timestamp")
                chunks = data.get("chunks", [])
                
                if src not in latest_chunks or timestamp > latest_chunks[src]["timestamp"]:
                    latest_chunks[src] = {
                        "timestamp": timestamp,
                        "chunks": chunks,
                        "file": str(p)
                    }
        except Exception as e:
            pass

    all_chunks = []
    for info in latest_chunks.values():
        all_chunks.extend(info["chunks"])
        
    print(f"Total files to index: {len(latest_chunks)}")
    print(f"Total chunks to index: {len(all_chunks)}")
    
    if not all_chunks:
        print("No chunks to index.")
        return

    print("Initializing VectorIndexer...")
    vector_config = VectorIndexerConfig.from_env()
    ingest_config = IngestConfig()
    vector_config.qdrant_collection = ingest_config.qdrant_collection
    
    indexer = VectorIndexer(vector_config)
    
    print("Indexing chunks into Qdrant...")
    try:
        stats = indexer.index_chunks(all_chunks)
        print(f"Indexation complete. Stats: {stats}")
    except Exception as e:
        print(f"Error during indexation: {e}")

if __name__ == "__main__":
    main()
