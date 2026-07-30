# scripts/test_metadata.py
"""
Script de test/démonstration de l'extracteur de métadonnées.
"""
import sys
from pathlib import Path
import json
import logging
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.rag.metadata_extractor import MetadataMerger, MetadataConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metadata_extraction():
    """Test l'extraction des métadonnées."""
    
    print("\n" + "=" * 80)
    print("🧪 TEST EXTRACTEUR DE MÉTADONNÉES - NURU")
    print("=" * 80)
    
    # Configuration
    config = MetadataConfig()
    merger = MetadataMerger(config)
    
    # 1. Tester sur des noms de fichiers simulés
    print("\n📋 Test sur des noms de fichiers simulés:\n")
    
    test_files = [
        ("data/raw/cours/01_Revisions_trigonometrie.pdf", 
         "Contenu du cours de trigonométrie..."),
        ("data/raw/exercices/Chap1_Probabilite/TD1-Probabilite-TS1.pdf",
         "Exercices de probabilités..."),
        ("data/raw/Devoirs_et_compositions/Devoirs-TS-1.pdf",
         "Devoir de mathématiques..."),
    ]
    
    for file_path_str, content in test_files:
        file_path = Path(file_path_str)
        print(f"📄 {file_path.name}")
        print("-" * 40)
        
        try:
            metadata = merger.extract_metadata(file_path, content)
            
            # Afficher les métadonnées importantes
            print(f"   🔹 Classe: {metadata.get('classe', 'N/A')}")
            print(f"   🔹 Série: {metadata.get('serie', 'N/A')}")
            print(f"   🔹 Série nom: {metadata.get('serie_nom', 'N/A')}")
            print(f"   🔹 Chapitre: {metadata.get('chapitre', 'N/A')}")
            print(f"   🔹 Type: {metadata.get('type_document', 'N/A')}")
            print(f"   🔹 Auteur: {metadata.get('auteur', 'N/A')}")
            print(f"   🔹 Compétences: {metadata.get('competences', [])}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print()
    
    # 2. Tester avec un contenu réel
    print("\n" + "=" * 80)
    print("📋 Test avec un contenu réel")
    print("=" * 80)
    
    real_content = """
# Chapitre 1 : Révisions de Trigonométrie

Classe de Terminale S1
Année scolaire 2023-2024
Professeur: M. Babacar DJITTE

## I. Rappels et compléments

### 1. Le radian

**Définition 1 :** On appelle radian, noté rad, la mesure de l'angle au centre qui intercepte un arc de longueur égale au rayon.

### 2. Cercle trigonométrique

**Théorème 1 :** Le cercle trigonométrique est un cercle de rayon 1 centré à l'origine.

**Exercice 1 :**
Calculer cos(π/3) et sin(π/3).

**Compétences :** Calculer, Déterminer, Résoudre, Analyser

## II. Formules fondamentales

**Propriété 1 :** Pour tout angle θ :
- sin²(θ) + cos²(θ) = 1
- sin(θ + π) = -sin(θ)
- cos(θ + π) = -cos(θ)

**Exemple :**
Calculer sin(π/6) et cos(π/6).
"""
    
    test_file = Path("data/raw/cours/Trigonométrie_TS1.pdf")
    
    print(f"\n📄 {test_file.name}")
    print("-" * 40)
    
    start_time = time.time()
    metadata = merger.extract_metadata(test_file, real_content)
    elapsed = time.time() - start_time
    
    print(f"\n📊 Métadonnées extraites ({elapsed:.2f}s):")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    # 3. Sauvegarder les résultats
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "metadata_complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés: {output_file}")
    
    # 4. Analyser les compétences
    if "competences" in metadata:
        print(f"\n📋 Compétences détectées: {len(metadata['competences'])}")
        for comp in metadata["competences"]:
            print(f"   - {comp}")
    
    # 5. Vérifier les champs manquants
    print("\n🔍 Vérification des champs:")
    for field in config.required_fields:
        status = "✅" if field in metadata else "❌"
        value = metadata.get(field, "MANQUANT")
        print(f"   {status} {field}: {value}")
    
    print("\n✅ Test terminé!")

def analyze_real_files():
    """Analyse les métadonnées des fichiers réels."""
    print("\n" + "=" * 80)
    print("📊 ANALYSE DES FICHIERS RÉELS")
    print("=" * 80)
    
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        print("❌ Dossier data/raw/ inexistant")
        return
    
    pdf_files = list(raw_dir.rglob("*.pdf"))
    if not pdf_files:
        print("❌ Aucun PDF trouvé")
        return
    
    print(f"\n📁 {len(pdf_files)} fichiers PDF trouvés\n")
    
    merger = MetadataMerger()
    results = []
    
    for pdf_path in pdf_files[:5]:  # Limiter à 5 pour la démo
        print(f"📄 {pdf_path.name}")
        
        try:
            # Extraire un peu de contenu pour les métadonnées
            from backend.app.rag.document_parser import DocumentParser
            parser = DocumentParser(use_nougat=False)
            text = parser.extract(pdf_path)
            
            # Extraire les métadonnées
            metadata = merger.extract_metadata(pdf_path, text[:500])  # Seulement les 500 premiers caractères
            
            results.append({
                "file": pdf_path.name,
                "classe": metadata.get("classe", "N/A"),
                "serie": metadata.get("serie", "N/A"),
                "chapitre": metadata.get("chapitre", "N/A"),
                "type": metadata.get("type_document", "N/A")
            })
            
            print(f"   ✅ Classe: {metadata.get('classe', 'N/A')}")
            print(f"   ✅ Série: {metadata.get('serie', 'N/A')}")
            print(f"   ✅ Chapitre: {metadata.get('chapitre', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print()
    
    # Résumé
    print("=" * 80)
    print("📊 RÉSUMÉ")
    print("=" * 80)
    
    classes = {}
    series = {}
    
    for r in results:
        classes[r["classe"]] = classes.get(r["classe"], 0) + 1
        series[r["serie"]] = series.get(r["serie"], 0) + 1
    
    print("\n📚 Classes détectées:")
    for cls, count in classes.items():
        print(f"   - {cls}: {count} fichier(s)")
    
    print("\n📚 Séries détectées:")
    for serie, count in series.items():
        print(f"   - {serie}: {count} fichier(s)")

if __name__ == "__main__":
    # Menu
    print("\n" + "=" * 80)
    print("📋 MENU DE TEST DES MÉTADONNÉES")
    print("=" * 80)
    print("1. Test avec contenu simulé")
    print("2. Test avec contenu réel")
    print("3. Analyser les fichiers réels")
    print("4. Quitter")
    print("=" * 80)
    
    choice = input("\nVotre choix (1-4): ")
    
    if choice == "1":
        test_metadata_extraction()
    elif choice == "2":
        # Test avec contenu réel
        print("\nTest avec contenu réel...")
        # Créer un fichier de test
        test_file = Path("data/raw/test_contenu_reel.pdf")
        if not test_file.parent.exists():
            test_file.parent.mkdir(parents=True)
        
        real_content = """
# Chapitre 1 : Probabilités

Classe de Terminale S1
Année scolaire 2023-2024

**Exercice :** Calculer la probabilité...

Compétences : Calculer, Déterminer
"""
        merger = MetadataMerger()
        metadata = merger.extract_metadata(test_file, real_content)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        
    elif choice == "3":
        analyze_real_files()
    else:
        print("Au revoir!")