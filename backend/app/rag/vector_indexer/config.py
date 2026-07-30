# backend/rag/vector_indexer/config.py
"""
Configuration pour l'indexeur vectoriel.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
from pathlib import Path

@dataclass
class VectorIndexerConfig:
    """Configuration de l'indexeur vectoriel."""
    
    # Qdrant Cloud
    qdrant_url: str = "https://your-qdrant-cluster.cloud.qdrant.io"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "nuru_maths"
    
    # Embeddings
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimension: int = 1024
    embedding_batch_size: int = 32
    
    # Collection
    collection_size: int = 100000
    shard_number: int = 1
    replication_factor: int = 1
    write_consistency_factor: int = 1
    
    # Indexing
    index_vector_size: int = 1024
    index_metric: str = "Cosine"  # Cosine, DotProduct, Euclidean
    
    # Retriever
    top_k: int = 10
    # Seuil de similarité : les embeddings BGE-M3 normalisés produisent des
    # scores cosinus réels autour de 0.40–0.50 sur ce corpus scolaire.
    # Un seuil de 0.7 filtrerait la quasi-totalité des résultats pertinents.
    score_threshold: float = 0.30
    
    # Hybrid search
    use_hybrid_search: bool = True
    bm25_weight: float = 0.4
    dense_weight: float = 0.6
    
    # Metadata
    metadata_fields: list = field(default_factory=lambda: [
        "chunk_type",
        "chunk_category",
        "discipline",
        "classe",
        "serie",
        "chapitre",
        "difficulty_level",
        "has_formulas",
        "source"
    ])
    
    @classmethod
    def from_env(cls):
        """Crée une configuration à partir des variables d'environnement."""
        config = cls(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            qdrant_collection_name=os.getenv("QDRANT_COLLECTION", "nuru_maths")
        )
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "qdrant_url": self.qdrant_url,
            "qdrant_collection_name": self.qdrant_collection_name,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "top_k": self.top_k,
            "use_hybrid_search": self.use_hybrid_search
        }