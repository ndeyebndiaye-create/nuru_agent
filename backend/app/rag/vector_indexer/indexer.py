# backend/rag/vector_indexer/indexer.py
"""
Indexeur vectoriel principal.
"""
from typing import List, Dict, Any, Optional
import logging
import uuid
from pathlib import Path

from .config import VectorIndexerConfig
from .qdrant_client import QdrantClientWrapper

logger = logging.getLogger(__name__)

class VectorIndexer:
    """
    Indexeur vectoriel pour les chunks pédagogiques.
    """
    
    def __init__(self, config: Optional[VectorIndexerConfig] = None):
        self.config = config or VectorIndexerConfig()
        self.client_wrapper = QdrantClientWrapper(self.config)
        self.embedder = self.client_wrapper.embedder
    
    def index_chunks(self, chunks: List[Dict[str, Any]], 
                     batch_size: int = 32) -> Dict[str, Any]:
        """
        Indexe une liste de chunks.
        
        Args:
            chunks: Liste de chunks (avec text, metadata, chunk_type)
            batch_size: Taille du batch pour l'encodage
            
        Returns:
            Statistiques d'indexation
        """
        if not chunks:
            logger.warning("⚠️ Aucun chunk à indexer")
            return {"indexed": 0, "errors": 0}
        
        logger.info(f"📊 Indexation de {len(chunks)} chunks")
        
        # 1. Vérifier/Créer la collection
        self.client_wrapper.create_collection()
        
        # 2. Extraire les textes
        texts = [chunk["text"] for chunk in chunks]
        
        # 3. Générer les embeddings
        try:
            embeddings = self.embedder.encode(texts, batch_size)
        except Exception as e:
            logger.error(f"❌ Erreur d'encodage: {e}")
            return {"indexed": 0, "errors": len(chunks), "error": str(e)}
        
        # 4. Préparer les points
        points = []
        errors = 0
        
        for i, chunk in enumerate(chunks):
            try:
                # Générer un ID unique
                point_id = chunk.get("id", str(uuid.uuid4()))
                
                # Préparer le payload
                payload = chunk.get("metadata", {}).copy()
                payload["text"] = chunk["text"]
                payload["chunk_type"] = chunk.get("chunk_type", "unknown")
                
                # Ajouter les métadonnées supplémentaires
                if "chunk_category" in chunk.get("metadata", {}):
                    payload["chunk_category"] = chunk["metadata"]["chunk_category"]
                
                point = {
                    "id": point_id,
                    "vector": embeddings[i].tolist(),
                    "payload": payload
                }
                points.append(point)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur sur le chunk {i}: {e}")
                errors += 1
        
        # 5. Indexer dans Qdrant
        if points:
            self.client_wrapper.upsert_points(points)
        
        logger.info(f"✅ Indexation terminée: {len(points)} points")
        
        return {
            "indexed": len(points),
            "errors": errors,
            "total": len(chunks)
        }
    
    def index_file(self, chunks: List[Dict[str, Any]], 
                   source: str) -> Dict[str, Any]:
        """
        Indexe les chunks d'un fichier.
        
        Args:
            chunks: Liste de chunks
            source: Source du fichier
            
        Returns:
            Statistiques d'indexation
        """
        logger.info(f"📁 Indexation du fichier: {source}")
        
        # Ajouter la source dans les métadonnées
        for chunk in chunks:
            if "metadata" not in chunk:
                chunk["metadata"] = {}
            chunk["metadata"]["source"] = source
        
        return self.index_chunks(chunks)
    
    def batch_index_files(self, file_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Indexe plusieurs fichiers.
        
        Args:
            file_chunks: Liste de dicts avec "source" et "chunks"
            
        Returns:
            Statistiques globales
        """
        total_stats = {"indexed": 0, "errors": 0, "files": 0}
        
        for file_data in file_chunks:
            source = file_data.get("source", "unknown")
            chunks = file_data.get("chunks", [])
            
            if not chunks:
                continue
            
            stats = self.index_file(chunks, source)
            total_stats["indexed"] += stats.get("indexed", 0)
            total_stats["errors"] += stats.get("errors", 0)
            total_stats["files"] += 1
            
            logger.info(f"✅ Fichier {source}: {stats}")
        
        return total_stats