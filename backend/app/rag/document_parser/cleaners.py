"""
Nettoyage du texte extrait
"""
import re

class TextCleaner:
    """Nettoyage du texte extrait."""
    
    @staticmethod
    def clean_newlines(text: str) -> str:
        """Nettoie les sauts de ligne excessifs."""
        text = re.sub(r'\n{4,}', '\n\n', text)
        text = re.sub(r'[ \t]+\n', '\n', text)
        return text
    
    @staticmethod
    def remove_headers_footers(text: str) -> str:
        """Supprime les en-têtes et pieds de page."""
        patterns = [
            r'^\s*Page \d+\s*$',
            r'^\s*T\.?S\.?\s*\d+\s*$',
            r'^\s*Classe de Tle S\s*$',
            r'^\s*Année scolaire \d+-\d+\s*$',
            r'^\s*Groupe scolaire.*$',
            r'^\s*Lycée.*$',
            r'^\s*Collège.*$',
            r'^\s*Professeur.*$',
            r'^\s*Profs?.*$'
        ]
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                cleaned.append(line)
                continue
            is_header = False
            for pattern in patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_header = True
                    break
            if not is_header:
                cleaned.append(line)
        return '\n'.join(cleaned)
    
    @staticmethod
    def fix_latex(text: str) -> str:
        """Corrige les notations LaTeX."""
        # $$...$$ -> \[...\]
        text = re.sub(r'\$\$(.+?)\$\$', r'\\[\1\\]', text, flags=re.DOTALL)
        # Espaces autour des $
        text = re.sub(r'\s*\$([^\$]+?)\$\s*', r' $\1$ ', text)
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Pipeline complet de nettoyage."""
        text = TextCleaner.remove_headers_footers(text)
        text = TextCleaner.clean_newlines(text)
        text = TextCleaner.fix_latex(text)
        return text.strip()
