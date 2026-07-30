# scripts/test_parser_adapted.py
"""
Test du parser adapté à ta structure data/raw/
"""
import sys
import os
from pathlib import Path
import logging
import time

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from backend.app.rag.document_parser import DocumentParser, ParserConfig

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_parser():
    """Test adapté à ta structure."""
    print("\n" + "=" * 80)
    print("🧪 TEST DU DOCUMENT PARSER - NURU")
    print("=" * 80)
    
    # Configurer les chemins
    ParserConfig.ensure_directories()
    
    # Récupérer tous les PDFs
    raw_dir = ParserConfig.RAW_DIR
    pdf_files = list(raw_dir.rglob("*.pdf"))
    
    if not pdf_files:
        print(f"\n❌ Aucun PDF trouvé dans: {raw_dir}")
        print("\n📁 Structure attendue:")
        print("   data/")
        print("   └── raw/")
        print("       ├── cours/       ← 31 PDFs de cours")
        print("       └── exercices/   ← Exercices")
        return
    
    print(f"\n📁 {len(pdf_files)} fichiers PDF trouvés\n")
    print("-" * 80)
    
    # Initialiser le parser
    parser = DocumentParser(use_nougat=False)
    results = []
    
    # Fonction pour traiter un fichier
    def process_file(pdf_path, index, total):
        rel_path = pdf_path.relative_to(raw_dir)
        print(f"\n[{index}/{total}] 📄 {rel_path}")
        
        try:
            start_time = time.time()
            text = parser.extract(pdf_path)
            elapsed = time.time() - start_time
            char_count = len(text)
            
            if char_count < 10:
                print(f"   ⚠️ Texte trop court ({char_count} caractères)")
                return None
            
            # Sauvegarder
            output_file = ParserConfig.PROCESSED_DIR / f"{pdf_path.stem}_extracted.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Aperçu
            preview = text[:200].replace('\n', ' ')
            
            print(f"   ✅ {char_count:,} caractères en {elapsed:.2f}s")
            print(f"   💾 Sauvegardé: {output_file.name}")
            print(f"   👁️ {preview[:150]}...")
            
            return {
                "file": str(rel_path),
                "characters": char_count,
                "time": elapsed,
                "status": "success"
            }
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return {
                "file": str(rel_path),
                "status": "failed",
                "error": str(e)
            }
    
    # === TRAITER LES FICHIERS ===
    
    # 1. D'abord les cours (pour voir les principaux)
    print("\n" + "=" * 80)
    print("📚 TRAITEMENT DES COURS")
    print("=" * 80)
    
    cours_files = list(raw_dir.glob("cours/*.pdf"))
    if cours_files:
        print(f"\n📁 {len(cours_files)} fichiers de cours trouvés\n")
        for i, pdf_path in enumerate(cours_files[:5], 1):  # 5 premiers cours
            result = process_file(pdf_path, i, len(cours_files[:5]))
            if result:
                results.append(result)
    
    # 2. Ensuite quelques exercices
    print("\n" + "=" * 80)
    print("✏️ TRAITEMENT DES EXERCICES")
    print("=" * 80)
    
    exercice_files = list(raw_dir.rglob("exercices/**/*.pdf"))
    if exercice_files:
        print(f"\n📁 {len(exercice_files)} fichiers d'exercices trouvés\n")
        # Prendre 2 exercices de chaque dossier
        for i, pdf_path in enumerate(exercice_files[:5], 1):  # 5 exercices
            result = process_file(pdf_path, i, len(exercice_files[:5]))
            if result:
                results.append(result)
    
    # === RÉSUMÉ FINAL ===
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE L'EXTRACTION")
    print("=" * 80)
    
    success = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "failed"]
    
    print(f"✅ Succès: {len(success)} fichiers")
    print(f"❌ Échecs: {len(failed)} fichiers")
    
    if success:
        total_chars = sum(r.get("characters", 0) for r in success)
        total_time = sum(r.get("time", 0) for r in success)
        print(f"📝 Total caractères extraits: {total_chars:,}")
        print(f"⏱️  Temps total: {total_time:.2f}s")
    
    if failed:
        print("\n❌ Fichiers en échec:")
        for f in failed:
            print(f"   - {f.get('file')}: {f.get('error', 'Erreur inconnue')}")
    
    print(f"\n📁 Résultats sauvegardés dans: {ParserConfig.PROCESSED_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    test_parser()