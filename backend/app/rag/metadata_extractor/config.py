# backend/rag/metadata_extractor/config.py
"""
Configuration pour l'extraction des métadonnées.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Pattern
import re

@dataclass
class MetadataConfig:
    """Configuration pour l'extraction des métadonnées."""
    
    # Patterns pour les noms de fichiers
    file_patterns: Dict[str, str] = field(default_factory=lambda: {
        # Classe et série
        "classe_serie": r'(Terminale|Tle|1ère|Première|2nde|Seconde)\s*(S|L|A|D|C|G)?\s*(\d+)?',
        
        # Chapitres (gère les séparateurs "_" des noms de fichiers, et évite
        # que "Chap" ne matche accidentellement à l'intérieur de "Chapitre"
        # quand le groupe numéro échoue juste après, via la lookahead négative)
        "chapitre": r'(?:Chapitre|Chap(?!itre))\.?[\s_]*([0-9]+|[IVXLCDM]+)[\s_]*[:.\-]?[\s_]*(.*?)(?:\s*\(|$|\.pdf|\.docx)',
        "chapitre_num": r'Chapitre\s*(\d+)',
        
        # Années
        "annee": r'(19|20)\d{2}',
        "annee_scolaire": r'(\d{4})-(\d{4})',
        
        # Types de documents
        "type_document": r'(cours|exercices?|td|tp|ds|devoir|composition|annales|problème|corrigé|sujet)',
        
        # Séries Sénégal — inclut TS1/TS2/TS (Terminale Scientifique, très
        # courant dans les noms de fichiers sénégalais) et utilise une
        # lookbehind/lookahead pour éviter de matcher une sous-chaîne d'un
        # autre mot (ex: "D1" à l'intérieur de "TD1" ne doit pas matcher).
        "serie_senegal": r'(?<![A-Za-z])(TS1|TS2|TS|S1|S2|S3|S4|S5|L1|L2|A1|A2|C1|C2|D1|D2|G1|G2)(?![A-Za-z])',
        
        # Auteurs
        "auteur": r'(?:par|de|Mr|Mme|M\.|Professeur)\s+([A-Z][a-zÀ-ÿ]+\s+[A-Z][a-zÀ-ÿ]+)',
        
        # Établissements
        "etablissement": r'(Lycée|Collège|École|Groupe Scolaire|IA)\s+([A-Za-zÀ-ÿ\s]+)',
    })
    
    # Patterns pour le contenu
    content_patterns: Dict[str, str] = field(default_factory=lambda: {
        "titre": r'^#\s*(.+)$',
        # Groupe 1 = numéro du chapitre, groupe 2 = titre (le séparateur
        # ":"/"."/"-" entre les deux est maintenant consommé, il ne polluait
        # plus le titre capturé).
        "chapitre_titre": r'^#\s*(?:Chapitre|CHAPITRE)\s*([IVXLCDM\d]+)\.?\s*[:.\-]?\s*(.+)$',
        # "Classe de" est maintenant un préfixe optionnel non-capturant : le
        # groupe 1 est bien le nom de la classe ("Terminale"), le groupe 2 la
        # série ("S1"), au lieu de capturer "Classe de" comme classe.
        "classe_contenu": r'(?:Classe de\s+)?(Terminale|Tle|Première|1ère|Seconde|2nde)\s+([A-Z]\d?)',
        "annee_contenu": r'(Année scolaire|Année)\s*[:.]?\s*(\d{4}-\d{4})',
        # Le titre de civilité (M./Mme/Mr) est inclus dans le groupe capturé
        # (l'appelant attend le nom complet tel quel), et le nom de famille
        # peut être tout en majuscules (ex: "DJITTE").
        "auteur_contenu": r'(Professeur|Prof|Enseignant|Auteur)\s*[:.]?\s*((?:M\.|Mme|Mr\.?)?\s*[A-ZÀ-Ÿ][a-zà-ÿ]*\s+[A-Za-zÀ-ÿ]+)',
        "chapitre_numero": r'(Chapitre|CHAPITRE)\s*[:.]?\s*([IVXLCDM\d]+)',
        "competence": r'(Compétences?|Capacités?)\s*[:.]?\s*\**\s*(.+?)\**\s*(?:\n|$)',
    })
    
    # Mapping des classes/séries sénégalaises
    class_mapping: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "Terminale": {
            "S1": "Sciences Mathématiques",
            "S2": "Sciences Physiques",
            "S3": "Sciences de la Vie et de la Terre",
            "S4": "Sciences Agricoles",
            "S5": "Sciences et Technologies de l'Ingénieur",
            "L1": "Littérature",
            "L2": "Langues Vivantes",
            "A1": "Arts Plastiques",
            "A2": "Arts Appliqués",
            "C1": "Comptabilité",
            "C2": "Gestion",
            "D1": "Droit",
            "D2": "Économie",
            "G1": "Gestion des Ressources Humaines",
            "G2": "Gestion Commerciale"
        },
        "Première": {
            "S": "Scientifique",
            "L": "Littéraire",
            "A": "Artistique",
            "D": "Droit et Économie",
            "G": "Gestion"
        },
        "Seconde": {
            "C": "Classe de Seconde"
        }
    })
    
    # Champs de métadonnées obligatoires
    required_fields: List[str] = field(default_factory=lambda: [
        "discipline",
        "classe",
        "serie",
        "chapitre",
        "type_document"
    ])
    
    # Métadonnées par défaut
    default_metadata: Dict[str, str] = field(default_factory=lambda: {
        "discipline": "mathématiques",
        "pays": "Sénégal",
        "langue": "français"
    })