# backend/rag/metadata_extractor/metadata_merger.py
"""
Fusion et normalisation des métadonnées provenant de différentes sources.
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from .config import MetadataConfig
from .file_metadata import FileMetadataExtractor
from .content_metadata import ContentMetadataExtractor

logger = logging.getLogger(__name__)

class MetadataMerger:
    """
    Fusionne les métadonnées provenant des fichiers et du contenu.
    """
    
    def __init__(self, config: Optional[MetadataConfig] = None):
        self.config = config or MetadataConfig()
        self.file_extractor = FileMetadataExtractor(config)
        self.content_extractor = ContentMetadataExtractor(config)
    
    def extract_metadata(
        self, 
        file_path: Path, 
        content: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extrait et fusionne les métadonnées de toutes les sources.
        
        Args:
            file_path: Chemin du fichier
            content: Contenu du document
            additional_metadata: Métadonnées supplémentaires (ex: de l'utilisateur)
            
        Returns:
            Dictionnaire complet de métadonnées
        """
        # 1. Métadonnées par défaut
        metadata = self.config.default_metadata.copy()
        
        # 2. Métadonnées du fichier
        file_metadata = self.file_extractor.extract(file_path)
        metadata.update(file_metadata)
        
        # 3. Métadonnées du contenu (complète celles du fichier)
        content_metadata = self.content_extractor.extract(content, metadata)
        metadata.update(content_metadata)
        
        # 4. Métadonnées supplémentaires
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # 5. Normalisation finale
        metadata = self._final_normalization(metadata)
        
        return metadata
    
    def _final_normalization(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalisation finale des métadonnées."""
        
        # S'assurer que les champs requis existent
        for field in self.config.required_fields:
            if field not in metadata:
                if field == "discipline":
                    metadata["discipline"] = "mathématiques"
                elif field == "classe":
                    metadata["classe"] = "Terminale"
                elif field == "serie":
                    metadata["serie"] = "S1"
                elif field == "chapitre":
                    metadata["chapitre"] = "Non spécifié"
                elif field == "type_document":
                    metadata["type_document"] = "cours"
        
        # Ajouter des métadonnées dérivées
        if "classe" in metadata and "serie" in metadata:
            classe = metadata["classe"]
            serie = metadata["serie"]
            if classe in self.config.class_mapping and serie in self.config.class_mapping[classe]:
                metadata["serie_nom"] = self.config.class_mapping[classe][serie]
        
        # Ajouter un ID unique basé sur le chemin
        if "source" in metadata:
            import hashlib
            metadata["document_id"] = hashlib.md5(
                metadata["source"].encode()
            ).hexdigest()[:16]
        
        # Ajouter la langue
        if "langue" not in metadata:
            metadata["langue"] = "français"
        
        # Ajouter le pays
        if "pays" not in metadata:
            metadata["pays"] = "Sénégal"
        
        return metadata