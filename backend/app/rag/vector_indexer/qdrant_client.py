"""
Client Qdrant - Version corrigée (sans import circulaire)
"""
import logging
import numpy as np
import re
from typing import Optional, List, Dict, Any
from .config import VectorIndexerConfig
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


_FILTER_PAYLOAD_FIELDS = ("classe", "serie")


def _series_filter_values(value: str) -> List[str]:
    """Retourne les variantes réellement présentes pour une même série."""
    normalized = value.strip().upper()
    canonical = normalized[1:] if normalized.startswith("TS") else normalized
    variants = [canonical, canonical.lower()]

    if re.fullmatch(r"[SL]\d*", canonical):
        prefixed = f"T{canonical}"
        variants.extend([prefixed, prefixed.lower(), prefixed.title()])

    return list(dict.fromkeys(variants))


def _build_query_filter(filter_conditions: Optional[Dict[str, Any]]):
    """Construit un filtre Qdrant typé à partir des métadonnées demandées."""
    if not filter_conditions:
        return None

    from qdrant_client.http import models

    conditions = []
    for key, value in filter_conditions.items():
        if key == "serie" and isinstance(value, str):
            match = models.MatchAny(any=_series_filter_values(value))
        else:
            match = models.MatchValue(value=value)
        conditions.append(models.FieldCondition(key=key, match=match))

    return models.Filter(must=conditions)


class QdrantClientWrapper:
    """
    Wrapper pour le client Qdrant.
    """
    
    def __init__(self, config: Optional[VectorIndexerConfig] = None):
        self.config = config or VectorIndexerConfig.from_env()
        self.client = None
        self.embedder = EmbeddingGenerator(self.config.embedding_model)
        self.collection_name = self.config.qdrant_collection_name
        self._init_client()
    
    def _init_client(self):
        """Initialise le client Qdrant."""
        try:
            from qdrant_client import QdrantClient
            # Client Qdrant
            self.client = QdrantClient(
                url=self.config.qdrant_url,
                api_key=self.config.qdrant_api_key,
                timeout=60
            )
            
            # Tester la connexion
            self.client.get_collections()
            self.ensure_filter_payload_indexes()
            logger.info("✅ Connexion à Qdrant établie")
            
        except ImportError:
            logger.warning("⚠️ qdrant-client non installé")
            logger.info("   Installez avec: pip install qdrant-client")
            raise
        except Exception as e:
            logger.warning(f"⚠️ Erreur de connexion à Qdrant: {e}")
            logger.info("   Utilisation du mode sans Qdrant")

    def ensure_filter_payload_indexes(self) -> List[str]:
        """Crée uniquement les index keyword manquants pour les filtres pédagogiques.

        La lecture préalable du schéma rend l'opération idempotente : un
        index existant n'est jamais recréé.
        """
        if self.client is None:
            return []

        from qdrant_client.http import models

        try:
            info = self.client.get_collection(self.collection_name)
            payload_schema = info.payload_schema or {}
            created = []

            for field_name in _FILTER_PAYLOAD_FIELDS:
                if field_name in payload_schema:
                    continue
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=models.PayloadSchemaType.KEYWORD,
                    wait=True,
                )
                created.append(field_name)

            if created:
                logger.info("✅ Index payload Qdrant créés: %s", ", ".join(created))
            return created
        except Exception as exc:
            logger.warning("⚠️ Impossible de vérifier/créer les index payload Qdrant: %s", exc)
            return []
    
    def create_collection(self, force_recreate: bool = False):
        """Crée la collection Qdrant."""
        if self.client is None:
            logger.warning("⚠️ Client Qdrant non disponible")
            return
        
        from qdrant_client.http import models
        
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name in collection_names:
                if force_recreate:
                    logger.info(f"🗑️ Suppression: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"ℹ️ Collection existe: {self.collection_name}")
                    return
            
            vector_size = self.embedder.get_dimension() or self.config.vector_size
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                )
            )
            
            logger.info(f"✅ Collection créée: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur création: {e}")
    
    def upsert_points(self, points: List[Dict[str, Any]], batch_size: int = 100):
        """Ajoute ou met à jour des points."""
        if self.client is None:
            logger.warning("⚠️ Client Qdrant non disponible")
            return
        
        if not points:
            logger.warning("⚠️ Aucun point à indexer")
            return
        
        from qdrant_client.http import models
        
        total = len(points)
        logger.info(f"📊 Indexation de {total} points")
        
        for i in range(0, total, batch_size):
            batch = points[i:i+batch_size]
            
            qdrant_points = []
            for point in batch:
                qdrant_points.append(
                    models.PointStruct(
                        id=point["id"],
                        vector=point["vector"],
                        payload=point["payload"]
                    )
                )
            
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=qdrant_points,
                )
                logger.info(f"   ✅ Batch {i//batch_size + 1}: {len(qdrant_points)} points")
            except Exception as e:
                logger.error(f"   ❌ Erreur batch: {e}")
                raise
        
        logger.info(f"✅ Indexation terminée: {total} points")
    
    def search(self, query_vector: np.ndarray, limit: int = 10,
               filter_conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Recherche des points similaires."""
        if self.client is None:
            logger.warning("⚠️ Client Qdrant non disponible")
            return []
        
        query_filter = _build_query_filter(filter_conditions)
        
        try:
            # qdrant-client >= 1.10 a supprime QdrantClient.search() au profit de
            # query_points() (meme resultat, structure de reponse differente : la
            # liste de points est dans .points).
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector.tolist(),
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
                with_vectors=True
            )
            results = response.points

            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "vector": result.vector
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return []
    
    def delete_collection(self):
        """Supprime la collection."""
        if self.client:
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"🗑️ Collection supprimée: {self.collection_name}")
            except Exception as e:
                logger.error(f"❌ Erreur suppression: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Retourne des informations sur la collection."""
        if self.client is None:
            return {"status": "not_connected"}
        
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "status": info.status,
                "vector_size": info.config.params.vectors.size
            }
        except Exception as e:
            return {"error": str(e)}

    