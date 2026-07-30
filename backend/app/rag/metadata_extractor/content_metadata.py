# backend/rag/metadata_extractor/content_metadata.py
"""
Extraction des métadonnées à partir du contenu des documents.
"""
import re
from typing import Dict, Any, Optional, List
import logging
from .config import MetadataConfig

logger = logging.getLogger(__name__)

class ContentMetadataExtractor:
    """
    Extrait les métadonnées depuis le contenu textuel.
    """
    
    def __init__(self, config: Optional[MetadataConfig] = None):
        self.config = config or MetadataConfig()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile les patterns regex."""
        self.compiled_patterns = {}
        for key, pattern in self.config.content_patterns.items():
            self.compiled_patterns[key] = re.compile(pattern, re.MULTILINE)
    
    def extract(self, text: str, existing_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrait les métadonnées depuis le contenu.
        
        Args:
            text: Texte du document
            existing_metadata: Métadonnées existantes (à compléter)
            
        Returns:
            Métadonnées extraites
        """
        metadata = existing_metadata or {}
        lines = text.split('\n')[:100]  # Analyser les 100 premières lignes
        
        # Analyser les premières lignes (où se trouve généralement les métadonnées)
        first_lines = '\n'.join(lines[:50])
        
        # 1. Extraire le titre
        title_match = self.compiled_patterns["titre"].search(first_lines)
        if title_match and "titre" not in metadata:
            metadata["titre"] = title_match.group(1).strip()
        
        # 2. Extraire le chapitre
        chapitre_match = self.compiled_patterns["chapitre_titre"].search(first_lines)
        if chapitre_match and "chapitre" not in metadata:
            metadata["chapitre"] = chapitre_match.group(2).strip()
            if "chapitre_numero" not in metadata:
                metadata["chapitre_numero"] = chapitre_match.group(1)
        
        # 3. Extraire la classe
        classe_match = self.compiled_patterns["classe_contenu"].search(first_lines)
        if classe_match and "classe" not in metadata:
            metadata["classe"] = classe_match.group(1).strip()
            if len(classe_match.groups()) > 1 and classe_match.group(2):
                metadata["serie"] = classe_match.group(2).strip()
        
        # 4. Extraire l'année
        annee_match = self.compiled_patterns["annee_contenu"].search(first_lines)
        if annee_match and "annee" not in metadata:
            metadata["annee_scolaire"] = annee_match.group(2)
        
        # 5. Extraire l'auteur
        auteur_match = self.compiled_patterns["auteur_contenu"].search(first_lines)
        if auteur_match and "auteur" not in metadata:
            metadata["auteur"] = auteur_match.group(2).strip()
        
        # 6. Extraire le numéro de chapitre
        chapitre_num_match = self.compiled_patterns["chapitre_numero"].search(first_lines)
        if chapitre_num_match and "chapitre_numero" not in metadata:
            metadata["chapitre_numero"] = chapitre_num_match.group(2)
        
        # 7. Extraire les compétences
        competence_matches = self.compiled_patterns["competence"].findall(text)
        if competence_matches:
            competences = []
            for match in competence_matches:
                if isinstance(match, tuple):
                    competences.append(match[-1].strip())
                else:
                    competences.append(match.strip())
            metadata["competences"] = competences[:5]  # Limiter à 5
        
        return metadata