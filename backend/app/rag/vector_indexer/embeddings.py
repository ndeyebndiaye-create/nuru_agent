# backend/rag/vector_indexer/embeddings.py
"""
Génération d'embeddings vectoriels.
"""
from typing import List, Optional, Dict, Any
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Générateur d'embeddings vectoriels.
    Supporte plusieurs modèles.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle d'embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"🔄 Chargement du modèle: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"✅ Modèle chargé avec succès")
            
            # Tester le modèle
            test_embedding = self.model.encode("test")
            logger.info(f"📐 Dimension des embeddings: {len(test_embedding)}")
            
        except ImportError:
            logger.warning("⚠️ sentence-transformers non installé")
            logger.info("   Installez avec: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
            raise
    
    # Cap defensif de longueur avant tokenisation : BGE-M3 accepte jusqu'a
    # 8192 tokens, et un chunk anormalement long (bug de chunking en amont,
    # document mal decoupe...) fait exploser la memoire du batch qui le
    # contient (l'un des batches par defaut a deja tente d'allouer 8 Go lors
    # de l'ingestion complete du corpus). Un chunk pedagogique normal fait au
    # plus quelques centaines de mots ; 4000 caracteres est tres large pour ce
    # cas d'usage tout en restant tres en-dessous de la limite du modele.
    _MAX_CHARS_PER_TEXT = 4000

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode une liste de textes en embeddings.

        Args:
            texts: Liste de textes
            batch_size: Taille du batch

        Returns:
            Matrice d'embeddings (n x dimension)
        """
        if not texts:
            return np.array([])

        try:
            logger.info(f"📊 Encodage de {len(texts)} textes")

            truncated = [t[: self._MAX_CHARS_PER_TEXT] if len(t) > self._MAX_CHARS_PER_TEXT else t for t in texts]
            n_truncated = sum(1 for t in texts if len(t) > self._MAX_CHARS_PER_TEXT)
            if n_truncated:
                logger.warning(
                    "⚠️ %d texte(s) tronqué(s) à %d caractères avant encodage (chunk anormalement long)",
                    n_truncated, self._MAX_CHARS_PER_TEXT,
                )

            embeddings = self.model.encode(
                truncated,
                batch_size=batch_size,
                normalize_embeddings=True,  # Normalisation pour similarité cosinus
                show_progress_bar=True
            )
            
            logger.info(f"✅ Encodage terminé: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'encodage: {e}")
            raise
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode un seul texte."""
        return self.encode([text])[0]
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode une requête pour la recherche.
        Identique à encode_single mais avec des traitements spécifiques.
        """
        # Pour BGE, ajouter le prefix "query: " pour les requêtes
        if "bge" in self.model_name.lower():
            query = f"query: {query}"
        
        return self.encode_single(query)
    
    def get_dimension(self) -> int:
        """Retourne la dimension des embeddings."""
        if self.model is None:
            return 1024
        return self.model.get_sentence_embedding_dimension()