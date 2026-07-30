from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ChunkerConfig:
    min_chunk_size: int = 100
    max_chunk_size: int = 1500
    ideal_chunk_size: int = 800
    
    section_patterns: Dict[str, str] = field(default_factory=lambda: {
        "chapitre": r'^#{1,3}\s*(Chapitre|CHAPITRE|PARTIE)\s*[IVXLCDM\d]+\.?\s*(.+)$',
        "definition": r'^(Définition|DEFINITION)\s*(\d+\.?\s*)?',
        "theoreme": r'^(Théorème|THEOREME|Propriété|PROPRIETE)\s*(\d+\.?\s*)?',
        "exercice": r'^(Exercice|EXERCICE|Problème|PROBLEME)\s*(\d+\.?\s*)?',
        "solution": r'^(Solution|SOLUTION|Corrigé|CORRIGE)\s*(\d+\.?\s*)?',
        "exemple": r'^(Exemple|EXEMPLE)\s*(\d+\.?\s*)?',
    })
    
    math_patterns: List[str] = field(default_factory=lambda: [
        r'\$\$.+?\$\$',
        r'\\\[.+?\\\]',
        r'\\frac\{.+?\}\{.+\}',
        r'\\sqrt\{.+?\}',
    ])
    
    competence_keywords: List[str] = field(default_factory=lambda: [
        "calculer", "déterminer", "montrer", "démontrer", "résoudre",
        "simplifier", "factoriser", "développer", "tracer", "construire",
    ])
    
    default_metadata: Dict[str, str] = field(default_factory=lambda: {
        "discipline": "mathématiques",
        "classe": "Terminale",
        "serie": "S1",
        "pays": "Sénégal"
    })
    
    remove_patterns: List[str] = field(default_factory=lambda: [
        r'^\s*Page \d+\s*$',
        r'^\s*T\.?S\.?\s*\d+\s*$',
    ])
    
    difficulty_thresholds: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "basic": {"max_chars": 300, "max_formulas": 2},
        "intermediate": {"max_chars": 600, "max_formulas": 5},
        "advanced": {"max_chars": 2000, "max_formulas": 20}
    })
    
    def get_chunk_type_mapping(self) -> Dict[str, str]:
        return {
            "chapitre": "course",
            "definition": "concept",
            "theoreme": "concept",
            "exercice": "exercise",
            "solution": "solution",
            "exemple": "example",
            "text": "course"
        }
