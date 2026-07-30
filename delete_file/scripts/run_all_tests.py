# scripts/run_all_tests.py
"""
Lance tous les tests du projet.
"""
import sys
from pathlib import Path
import subprocess
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """Lance tous les tests."""
    
    print("\n" + "=" * 80)
    print("🧪 LANCEMENT DE TOUS LES TESTS - NURU")
    print("=" * 80)
    
    tests = [
        ("📋 Test du Parser", "scripts/test_parser.py"),
        ("📋 Test du Chunker", "scripts/test_chunker.py"),
        ("📋 Test des Métadonnées", "scripts/test_metadata.py"),
        ("📋 Vérification de l'environnement", "scripts/check_setup.py"),
    ]
    
    results = []
    total_start = time.time()
    
    for name, script in tests:
        print(f"\n{'=' * 80}")
        print(f"▶️  {name}")
        print(f"{'=' * 80}")
        
        script_path = project_root / script
        if not script_path.exists():
            print(f"❌ Script non trouvé: {script_path}")
            results.append({"name": name, "status": "failed", "error": "Script non trouvé"})
            continue
        
        try:
            start = time.time()
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            elapsed = time.time() - start
            
            if result.returncode == 0:
                print(result.stdout)
                print(f"✅ {name} terminé en {elapsed:.2f}s")
                results.append({"name": name, "status": "success", "time": elapsed})
            else:
                print(result.stdout)
                print(result.stderr)
                print(f"❌ {name} a échoué (code: {result.returncode})")
                results.append({"name": name, "status": "failed", "error": result.stderr[:200]})
        except subprocess.TimeoutExpired:
            print(f"❌ {name} a expiré (plus de 60s)")
            results.append({"name": name, "status": "timeout"})
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results.append({"name": name, "status": "error", "error": str(e)})
    
    # Rapport final
    total_time = time.time() - total_start
    
    print("\n" + "=" * 80)
    print("📊 RAPPORT FINAL DES TESTS")
    print("=" * 80)
    
    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]
    
    print(f"✅ Tests réussis: {len(success)}/{len(results)}")
    print(f"❌ Tests échoués: {len(failed)}/{len(results)}")
    print(f"⏱️  Temps total: {total_time:.2f}s")
    
    if failed:
        print("\n❌ Détails des échecs:")
        for f in failed:
            print(f"   - {f['name']}: {f.get('error', 'Erreur inconnue')}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    run_tests()