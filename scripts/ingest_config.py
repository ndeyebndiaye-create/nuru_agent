# scripts/ingest_config.py
"""
Configuration du pipeline d'ingestion.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

@dataclass
class IngestConfig:
    """Configuration du pipeline d'ingestion."""
    
    # Chemins
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    chunks_dir: Path = Path("data/processed/chunks")
    reports_dir: Path = Path("data/processed/reports")
    logs_dir: Path = Path("data/ingestion_logs")
    
    # Filtres
    file_extensions: List[str] = field(default_factory=lambda: [".pdf"])
    max_file_size_mb: int = 50
    skip_existing: bool = True
    
    # Pipeline
    use_nougat: bool = False  # False par défaut pour éviter les problèmes
    batch_size: int = 32
    max_chunks_per_file: int = 1000
    
    # Chunking
    chunk_min_size: int = 100
    chunk_max_size: int = 1500
    chunk_ideal_size: int = 800
    
    # Embeddings
    embedding_model: str = "BAAI/bge-m3"
    embedding_batch_size: int = 32
    
    # Indexation
    qdrant_collection: str = "nuru_maths"
    index_batch_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    save_chunks: bool = True
    save_report: bool = True
    
    def __post_init__(self):
        """Crée les dossiers nécessaires."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls):
        """Crée une configuration à partir des variables d'environnement."""
        return cls(
            raw_dir=Path(os.getenv("RAW_DIR", "data/raw")),
            processed_dir=Path(os.getenv("PROCESSED_DIR", "data/processed")),
            use_nougat=os.getenv("USE_NOUGAT", "False").lower() == "true",
            batch_size=int(os.getenv("BATCH_SIZE", "32")),
            qdrant_collection=os.getenv("QDRANT_COLLECTION", "nuru_maths"),
        )