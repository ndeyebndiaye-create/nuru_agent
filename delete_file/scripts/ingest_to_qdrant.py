#!/usr/bin/env python3
"""
Pipeline d'ingestion - Version locale (sans Docker)
Utilise Qdrant en mémoire ou en mode fichier
"""
import sys
from pathlib import Path
import logging
import time
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.rag.document_parser import DocumentParser
from backend.app.rag.chunker import ChunkingPipeline, ChunkerConfig
from backend.app.rag.metadata_extractor import MetadataMerger
from backend.app.rag.vector_indexer import VectorIndexer, VectorIndexerConfig
from backend.app.rag.vector_indexer.embeddings import LiteEmbedder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IngestPipelineLocal:
    def __init__(self):
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        print("🔧 Initialisation...")
        
        self.parser = DocumentParser(use_nougat=False)
        self.chunker = ChunkingPipeline(ChunkerConfig(
            min_chunk_size=100, max_chunk_size=1500, ideal_chunk_size=800
        ))
        self.metadata_extractor = MetadataMerger()
        
        # Embedder simple
        self.embedder = LiteEmbedder(dimension=384)
        
        # Config Qdrant - Mode mémoire
        self.qdrant_config = VectorIndexerConfig()
        self.qdrant_config.qdrant_url = ":memory:"  # Mode mémoire
        self.qdrant_config.qdrant_api_key = None
        self.qdrant_config.qdrant_collection_name = "nuru_maths"
        self.qdrant_config.vector_size = 384
        
        self.indexer = VectorIndexer(self.qdrant_config)
        self.indexer.embedder = self.embedder
        self.indexer.client_wrapper.embedder = self.embedder
        
        self.stats = {
            "total_files": 0, "processed": 0, "chunks_created": 0,
            "indexed": 0, "errors": 0, "files": []
        }
        
        print("✅ Prêt")
    
    def run(self, limit=None):
        print("\n" + "=" * 80)
        print("📊 PIPELINE D'INGESTION - MODE LOCAL")
        print("=" * 80)
        print("🔧 Utilisation de Qdrant en mémoire")
        print("=" * 80)
        
        if not self.raw_dir.exists():
            print(f"❌ Dossier non trouvé: {self.raw_dir}")
            return
        
        pdf_files = list(self.raw_dir.rglob("*.pdf"))
        if not pdf_files:
            print(f"❌ Aucun PDF trouvé")
            return
        
        if limit:
            pdf_files = pdf_files[:limit]
        
        self.stats["total_files"] = len(pdf_files)
        print(f"\n📁 {len(pdf_files)} fichiers PDF\n")
        
        all_chunks = []
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"[{i}/{len(pdf_files)}] 📄 {pdf_path.name}")
            try:
                text = self.parser.extract(pdf_path)
                if not text or len(text) < 50:
                    continue
                
                metadata = self.metadata_extractor.extract_metadata(pdf_path, text)
                metadata["source"] = str(pdf_path)
                metadata["filename"] = pdf_path.name
                
                chunks = self.chunker.process(text, metadata)
                if chunks:
                    all_chunks.extend(chunks)
                    self.stats["processed"] += 1
                    self.stats["chunks_created"] += len(chunks)
                    self.stats["files"].append({
                        "name": pdf_path.name,
                        "chunks": len(chunks),
                        "status": "success"
                    })
                    print(f"   ✅ {len(chunks)} chunks")
                else:
                    print(f"   ⚠️ Aucun chunk")
            except Exception as e:
                self.stats["errors"] += 1
                print(f"   ❌ Erreur: {e}")
        
        if all_chunks:
            print(f"\n📊 Indexation de {len(all_chunks)} chunks...")
            try:
                self.indexer.client_wrapper.create_collection(force_recreate=True)
                stats = self.indexer.index_chunks(all_chunks)
                self.stats["indexed"] = stats.get("indexed", 0)
                print(f"✅ Indexation: {stats.get('indexed', 0)} points")
            except Exception as e:
                print(f"❌ Erreur d'indexation: {e}")
        
        self._generate_report()
    
    def _generate_report(self):
        print("\n" + "=" * 80)
        print("📊 RAPPORT")
        print("=" * 80)
        print(f"📁 Fichiers: {self.stats['total_files']}")
        print(f"✅ Traités: {self.stats['processed']}")
        print(f"❌ Erreurs: {self.stats['errors']}")
        print(f"📝 Chunks: {self.stats['chunks_created']}")
        print(f"📈 Indexés: {self.stats['indexed']}")
        print("=" * 80)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    IngestPipelineLocal().run(limit=args.limit)
