# backend/tests/test_document_parser.py
import sys
from pathlib import Path
import time
import json
import logging
from datetime import datetime

# Ajouter le backend au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.document_parser import DocumentParser, ParserConfig

# Configuration du logging
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Maintenant on peut importer depuis backend
from backend.app.rag.document_parser import DocumentParser, ParserConfig
# =====================================

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentParserTester:
    def __init__(self):
        self.parser = DocumentParser(use_nougat=True)
        self.results = []
        self.stats = {
            "total_files": 0,
            "success": 0,
            "failed": 0,
            "total_time": 0,
            "methods": {"nougat": 0, "pymupdf": 0}
        }
        
    def run_tests(self):
        """Exécute les tests sur tous les PDFs trouvés."""
        # Créer les dossiers si nécessaire
        ParserConfig.ensure_directories()
        
        # Trouver tous les PDFs
        raw_dir = ParserConfig.RAW_DIR
        pdf_files = list(raw_dir.rglob("*.pdf"))
        
        if not pdf_files:
            print("❌ Aucun PDF trouvé dans data/raw/")
            print(f"   Placez des fichiers dans: {raw_dir}")
            return
        
        print(f"\n📁 {len(pdf_files)} fichiers PDF trouvés\n")
        print("=" * 80)
        
        # Tester chaque fichier
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] 📄 {pdf_path.name}")
            print("-" * 40)
            
            start_time = time.time()
            result = self._test_single_file(pdf_path)
            elapsed = time.time() - start_time
            
            result["elapsed_time"] = elapsed
            result["file_name"] = pdf_path.name
            result["file_path"] = str(pdf_path)
            self.results.append(result)
            
            # Mettre à jour les statistiques
            self.stats["total_files"] += 1
            self.stats["total_time"] += elapsed
            if result["status"] == "success":
                self.stats["success"] += 1
                method = result.get("method", "unknown")
                if method in self.stats["methods"]:
                    self.stats["methods"][method] += 1
            else:
                self.stats["failed"] += 1
                print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
    
    def _test_single_file(self, pdf_path: Path) -> dict:
        """Teste un seul fichier."""
        result = {
            "status": "failed",
            "method": "unknown",
            "error": None,
            "char_count": 0,
            "page_count": 0,
            "has_math": False,
            "saved_file": None
        }
        
        try:
            # Extraire le texte
            extracted_text = self.parser.extract(pdf_path)
            
            # Vérifier le résultat
            if not extracted_text or len(extracted_text) < 10:
                result["error"] = "Texte extrait trop court"
                return result
            
            result["char_count"] = len(extracted_text)
            
            # Détecter la présence de mathématiques
            math_patterns = ['$$', '\\[', '\\begin', 'frac{', 'sqrt{', '^', '_']
            has_math = any(pattern in extracted_text for pattern in math_patterns)
            result["has_math"] = has_math
            
            # Estimer le nombre de pages
            page_markers = extracted_text.count("--- Page")
            result["page_count"] = page_markers if page_markers > 0 else 1
            
            # Sauvegarder le résultat
            output_file = ParserConfig.PROCESSED_DIR / f"{pdf_path.stem}_extracted.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            result["saved_file"] = str(output_file)
            
            # Afficher un aperçu
            preview = extracted_text[:300].replace('\n', ' ')
            print(f"✅ Succès: {result['char_count']} caractères, {result['page_count']} pages")
            print(f"   {'📐 Contient des maths' if has_math else '📝 Texte seulement'}")
            print(f"   💾 Sauvegardé dans: {output_file}")
            print(f"   👁️  Aperçu: {preview[:100]}...")
            
            result["status"] = "success"
            result["method"] = "nougat" if has_math else "pymupdf"
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Échec: {e}")
        
        return result
    
    def generate_report(self):
        """Génère un rapport des tests."""
        report_path = ParserConfig.PROCESSED_DIR / "test_report.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "results": self.results,
            "summary": {
                "success_rate": f"{(self.stats['success'] / max(1, self.stats['total_files']) * 100):.1f}%",
                "avg_time": f"{self.stats['total_time'] / max(1, self.stats['total_files']):.2f}s",
                "methods_used": self.stats["methods"]
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Afficher le rapport
        print("\n" + "=" * 80)
        print("📊 RAPPORT DE TEST")
        print("=" * 80)
        print(f"📁 Fichiers traités: {self.stats['total_files']}")
        print(f"✅ Succès: {self.stats['success']}")
        print(f"❌ Échecs: {self.stats['failed']}")
        print(f"📈 Taux de réussite: {report['summary']['success_rate']}")
        print(f"⏱️  Temps moyen: {report['summary']['avg_time']}")
        print(f"🔧 Méthodes utilisées: {self.stats['methods']}")
        print(f"\n📄 Rapport détaillé: {report_path}")
        
        # Afficher les fichiers avec erreurs
        failures = [r for r in self.results if r["status"] == "failed"]
        if failures:
            print("\n❌ Fichiers en échec:")
            for f in failures:
                print(f"   - {f['file_name']}: {f.get('error', 'Erreur inconnue')}")

def main():
    """Point d'entrée principal."""
    tester = DocumentParserTester()
    tester.run_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()