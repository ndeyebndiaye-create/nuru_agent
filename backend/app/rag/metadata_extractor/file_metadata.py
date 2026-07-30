# backend/rag/metadata_extractor/file_metadata.py
"""
Extraction des métadonnées à partir des noms de fichiers et chemins.
"""
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from .config import MetadataConfig

logger = logging.getLogger(__name__)

class FileMetadataExtractor:
    """
    Extrait les métadonnées depuis les noms de fichiers et les chemins.
    """
    
    def __init__(self, config: Optional[MetadataConfig] = None):
        self.config = config or MetadataConfig()
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile les patterns regex."""
        self.compiled_patterns = {}
        for key, pattern in self.config.file_patterns.items():
            self.compiled_patterns[key] = re.compile(pattern, re.IGNORECASE)
    
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrait les métadonnées depuis un chemin de fichier.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Dictionnaire de métadonnées
        """
        metadata = {}
        filename = file_path.stem
        
        # Extraire du chemin complet d'abord (repli de plus basse priorité :
        # nom de dossier / mots-clés), puis du nom de fichier (plus précis,
        # écrase donc le repli du dossier s'il détecte mieux).
        metadata.update(self._extract_from_path(file_path))
        metadata.update(self._extract_from_filename(filename))
        
        # Ajouter les informations de base
        metadata["source"] = str(file_path)
        metadata["filename"] = file_path.name
        metadata["extension"] = file_path.suffix
        
        # Normaliser les métadonnées
        metadata = self._normalize_metadata(metadata)
        
        return metadata
    
    # Mots-clés de notions du programme Terminale S1, utilisés en repli
    # quand le nom de fichier ne contient pas explicitement "Chapitre N".
    # Ordre important : les motifs les plus spécifiques d'abord.
    NOTION_KEYWORDS = [
        (r"probabilit", "Probabilités"),
        (r"deriv", "Dérivation"),
        (r"integr|primitiv", "Intégration"),
        (r"limite", "Limites"),
        (r"suite", "Suites numériques"),
        (r"complexe", "Nombres complexes"),
        (r"exponentiel", "Fonction exponentielle"),
        (r"logarithm", "Fonction logarithme"),
        (r"geometrie|géométrie|espace", "Géométrie dans l'espace"),
        (r"statistique", "Statistiques"),
        (r"continuit", "Continuité"),
        (r"equation.*differentiel|différentiel", "Équations différentielles"),
        (r"denombrement|dénombrement|combinatoire", "Dénombrement"),
        (r"matrice", "Matrices"),
        (r"produit.*scalaire", "Produit scalaire"),
    ]

    def _detect_notion_from_text(self, text: str) -> Optional[str]:
        """Détecte une notion du programme à partir d'un texte libre (nom de
        fichier ou nom de dossier), en se basant sur des mots-clés simples.
        Insensible à la casse et aux accents basiques."""
        normalized = text.lower().replace("é", "e").replace("è", "e").replace("ê", "e")
        for pattern, label in self.NOTION_KEYWORDS:
            if re.search(pattern.replace("é", "e"), normalized):
                return label
        return None

    def _extract_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extrait les métadonnées depuis le nom du fichier."""
        metadata = {}
        
        # 1. Détecter la série (S1, S2, etc.)
        serie_match = self.compiled_patterns["serie_senegal"].search(filename)
        if serie_match:
            metadata["serie"] = serie_match.group(1)
        
        # 2. Détecter le chapitre
        chapitre_match = self.compiled_patterns["chapitre"].search(filename)
        if chapitre_match:
            chapitre_num = chapitre_match.group(1)
            chapitre_titre = chapitre_match.group(2) if len(chapitre_match.groups()) > 1 else ""
            metadata["chapitre_numero"] = chapitre_num
            if chapitre_titre:
                metadata["chapitre_titre"] = chapitre_titre.strip()
                metadata["chapitre"] = chapitre_titre.strip()
            else:
                metadata["chapitre"] = f"Chapitre {chapitre_num}"
        else:
            # Repli : pas de "Chapitre N" explicite dans le nom (ex: fichiers
            # "TD1-Probabilite-TS1.pdf" quand les PDF ne sont plus rangés
            # dans des sous-dossiers par chapitre). On détecte la notion via
            # des mots-clés du programme Terminale S1 directement dans le
            # nom de fichier.
            notion = self._detect_notion_from_text(filename)
            if notion:
                metadata["chapitre"] = notion
        
        # 3. Détecter le type de document
        type_match = self.compiled_patterns["type_document"].search(filename)
        if type_match:
            metadata["type_document"] = type_match.group(1)
        
        # 4. Détecter l'année
        annee_match = self.compiled_patterns["annee"].search(filename)
        if annee_match:
            metadata["annee"] = annee_match.group(0)
        
        # 5. Détecter l'auteur
        auteur_match = self.compiled_patterns["auteur"].search(filename)
        if auteur_match:
            metadata["auteur"] = auteur_match.group(1)
        
        # 6. Détecter l'établissement
        etab_match = self.compiled_patterns["etablissement"].search(filename)
        if etab_match:
            metadata["etablissement"] = etab_match.group(2)
        
        return metadata
    
    def _extract_from_path(self, file_path: Path) -> Dict[str, Any]:
        """Extrait les métadonnées depuis le chemin complet."""
        metadata = {}
        parts = file_path.parts

        # Mots-clés "structurels" à ignorer quand on cherche un nom de
        # chapitre dans les dossiers parents (ce ne sont pas des chapitres).
        structural_keywords = {
            "cours", "exercices", "td", "tp", "devoir", "composition",
            "raw", "data", "processed", "mathématiques", "maths",
            "physique", "chimie", "svt", "histoire", "géographie",
            "terminale", "tle", "1ère", "première", "2nde", "seconde",
        }

        # Analyser les dossiers parents
        for part in parts:
            part_lower = part.lower()
            if part_lower in ["cours", "exercices", "td", "tp", "devoir", "composition"]:
                metadata["type_document"] = part_lower
            elif part_lower in ["mathématiques", "maths", "physique", "chimie", "svt", "histoire", "géographie"]:
                metadata["discipline"] = part_lower
            elif part_lower in ["terminale", "tle", "1ère", "première", "2nde", "seconde"]:
                metadata["classe"] = part.capitalize()
            elif part_lower not in structural_keywords:
                # Sous-dossier "métier" potentiel, ex: "Chap1_Probabilite"
                # ou "Probabilites" (si l'organisation par chapitre existe).
                notion = self._detect_notion_from_text(part)
                if notion and "chapitre" not in metadata:
                    metadata["chapitre"] = notion

        return metadata
    
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise les métadonnées extraites."""
        # Normaliser la classe
        if "classe" in metadata:
            classe = metadata["classe"].lower()
            mapping = {
                "tle": "Terminale",
                "terminale": "Terminale",
                "1ère": "Première",
                "première": "Première",
                "2nde": "Seconde",
                "seconde": "Seconde"
            }
            if classe in mapping:
                metadata["classe"] = mapping[classe]
        
        # Normaliser la série
        if "serie" in metadata:
            serie = metadata["serie"].upper()
            if serie in ["S1", "S2", "S3", "S4", "S5"]:
                metadata["serie_nom"] = self.config.class_mapping.get("Terminale", {}).get(serie, "")
            elif serie in ["L1", "L2"]:
                metadata["serie_nom"] = self.config.class_mapping.get("Terminale", {}).get(serie, "")
        
        # Normaliser le type de document
        if "type_document" in metadata:
            type_doc = metadata["type_document"].lower()
            type_mapping = {
                "cours": "course",
                "exercice": "exercise",
                "exercices": "exercise",
                "td": "exercise",
                "tp": "practical",
                "devoir": "assessment",
                "composition": "assessment",
                "annales": "exam",
                "corrigé": "solution",
                "sujet": "exam",
                "problème": "problem"
            }
            if type_doc in type_mapping:
                metadata["type_document_normalized"] = type_mapping[type_doc]
        
        return metadata