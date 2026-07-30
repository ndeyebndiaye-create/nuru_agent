# scripts/check_setup.py
"""
Vérifie que l'environnement est correctement configuré.
"""
import sys
from pathlib import Path
from importlib.util import find_spec

# Les consoles Windows peuvent encore utiliser CP1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_module(module_name):
    """Vérifie si un module est installé."""
    try:
        available = find_spec(module_name) is not None
        if not available:
            raise ImportError(module_name)
        print(f"  ✅ {module_name}")
        return True
    except ImportError:
        print(f"  ❌ {module_name}")
        return False

def main():
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT NURU")
    print("=" * 80)
    
    # 1. Vérifier les modules Python
    print("\n📦 Modules Python:")
    modules = [
        "pymupdf",
        "PIL",
        "transformers",
        "torch",
        "tqdm",
        "dotenv",
        "fastapi",
        "uvicorn",
        "gradio",
        "qdrant_client",
        "langgraph",
        "sqlalchemy",
        "psycopg",
        "ollama",
        "requests",
    ]
    
    missing = []
    for mod in modules:
        if not check_module(mod):
            missing.append(mod)
    
    # 2. Vérifier la structure des dossiers
    print("\n📁 Structure des dossiers:")
    project_root = Path(__file__).parent.parent
    folders = [
        project_root / "data" / "raw",
        project_root / "data" / "processed",
        project_root / "backend" / "app" / "rag" / "document_parser",
        project_root / "backend" / "app" / "rag" / "chunker",
        project_root / "backend" / "app" / "rag" / "metadata_extractor",
        project_root / "scripts",
        project_root / "tests"
    ]
    
    for folder in folders:
        status = "✅" if folder.exists() else "❌"
        print(f"  {status} {folder.relative_to(project_root)}")
    
    # 3. Vérifier les fichiers PDF
    print("\n📄 Fichiers PDF trouvés:")
    raw_dir = project_root / "data" / "raw"
    if raw_dir.exists():
        pdf_files = list(raw_dir.rglob("*.pdf"))
        if pdf_files:
            print(f"  ✅ {len(pdf_files)} fichier(s) PDF")
            for f in pdf_files[:5]:  # Afficher les 5 premiers
                size = f.stat().st_size / 1024  # Taille en KB
                print(f"     - {f.name} ({size:.1f} KB)")
            if len(pdf_files) > 5:
                print(f"     ... et {len(pdf_files) - 5} autres")
        else:
            print("  ⚠️ Aucun fichier PDF trouvé")
            print("     Placez vos PDFs dans: data/raw/")
    else:
        print("  ❌ Dossier data/raw/ inexistant")
    
    # 4. Résumé
    print("\n" + "=" * 80)
    if missing:
        print("⚠️ Modules manquants:")
        for mod in missing:
            print(f"   pip install {mod}")
        print("\n📌 Installez les modules manquants pour continuer.")
    else:
        print("✅ Tous les modules sont installés!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
