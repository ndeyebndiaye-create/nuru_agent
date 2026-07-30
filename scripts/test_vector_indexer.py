"""
Test Qdrant en mode mémoire - Syntaxe correcte.
"""
import sys
from pathlib import Path
import logging
import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)

def test_qdrant_memory():
    """Test Qdrant en mode mémoire."""
    print("\n" + "=" * 80)
    print("🧪 TEST QDRANT - MODE MÉMOIRE")
    print("=" * 80)
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http import models
        
        print("✅ Qdrant-client installé")
        
        # Créer un client en mémoire
        print("\n📁 Création du client Qdrant en mémoire...")
        client = QdrantClient(":memory:")
        
        # Créer une collection
        print("📁 Création de la collection...")
        client.create_collection(
            collection_name="test_collection",
            vectors_config=models.VectorParams(
                size=4,
                distance=models.Distance.COSINE,
            )
        )
        
        # Ajouter des points
        print("📊 Ajout de points...")
        
        points = [
            models.PointStruct(
                id=1,
                vector=[1.0, 0.0, 0.0, 0.0],
                payload={"text": "La dérivée de x² est 2x", "chapitre": "Dérivabilité"}
            ),
            models.PointStruct(
                id=2,
                vector=[0.0, 1.0, 0.0, 0.0],
                payload={"text": "La dérivée de e^x est e^x", "chapitre": "Exponentielle"}
            ),
            models.PointStruct(
                id=3,
                vector=[0.0, 0.0, 1.0, 0.0],
                payload={"text": "Le théorème de Pythagore", "chapitre": "Géométrie"}
            )
        ]
        
        client.upsert(
            collection_name="test_collection",
            points=points
        )
        print("✅ Points ajoutés")
        
        # RECHERCHE - Méthode correcte pour Qdrant 1.12+
        print("\n🔍 Recherche...")
        
        # Méthode 1: Utiliser query_points (nouvelle API)
        try:
            results = client.query_points(
                collection_name="test_collection",
                query=[0.5, 0.5, 0.0, 0.0],
                limit=3,
                with_payload=True
            )
            results = results.points
        except AttributeError:
            # Méthode 2: Utiliser search (ancienne API)
            results = client.search(
                collection_name="test_collection",
                query_vector=[0.5, 0.5, 0.0, 0.0],
                limit=3,
                with_payload=True
            )
        
        print(f"✅ {len(results)} résultats trouvés\n")
        for r in results:
            print(f"   📊 Score: {r.score:.3f}")
            print(f"   📝 Texte: {r.payload.get('text', 'N/A')}")
            print(f"   📚 Chapitre: {r.payload.get('chapitre', 'N/A')}")
            print()
        
        print("\n✅ Test terminé!")
        
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("\n📌 Installe Qdrant:")
        print("   pip install qdrant-client")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print(f"   Type: {type(e).__name__}")

def test_with_embeddings():
    """Test avec de vrais embeddings."""
    print("\n" + "=" * 80)
    print("🧪 TEST QDRANT + EMBEDDINGS RÉELS")
    print("=" * 80)
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http import models
        from sentence_transformers import SentenceTransformer
        
        print("✅ Dépendances chargées")
        
        # Charger le modèle
        print("\n📊 Chargement du modèle d'embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        vector_size = model.get_sentence_embedding_dimension()
        print(f"✅ Modèle chargé - Dimension: {vector_size}")
        
        # Créer Qdrant en mémoire
        print("\n📁 Création de Qdrant en mémoire...")
        client = QdrantClient(":memory:")
        
        client.create_collection(
            collection_name="nuru_maths",
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            )
        )
        print("✅ Collection créée")
        
        # Données
        chunks = [
            {"text": "La dérivée de f(x) = x² est f'(x) = 2x", "metadata": {"chapitre": "Dérivabilité"}},
            {"text": "La dérivée de e^x est e^x", "metadata": {"chapitre": "Fonctions Exponentielles"}},
            {"text": "Exercice: Calculer la dérivée de f(x) = 3x² - 5x + 2", "metadata": {"chapitre": "Dérivabilité"}},
            {"text": "L'intégrale de x² est x³/3 + C", "metadata": {"chapitre": "Calcul Intégral"}},
            {"text": "Le théorème de Pythagore: a² + b² = c²", "metadata": {"chapitre": "Géométrie"}}
        ]
        
        # Indexer
        print("\n📊 Indexation des chunks...")
        texts = [chunk["text"] for chunk in chunks]
        embeddings = model.encode(texts, normalize_embeddings=True)
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            client.upsert(
                collection_name="nuru_maths",
                points=[
                    models.PointStruct(
                        id=i + 1,
                        vector=embedding.tolist(),
                        payload={"text": chunk["text"], **chunk["metadata"]}
                    )
                ]
            )
        
        print(f"✅ {len(chunks)} points indexés")
        
        # Recherche
        print("\n🔍 Tests de recherche...")
        
        queries = [
            "Comment dériver x² ?",
            "dérivée exponentielle",
            "calcul intégral",
            "Pythagore"
        ]
        
        for query in queries:
            print(f"\n📝 Query: \"{query}\"")
            print("-" * 40)
            
            query_embedding = model.encode(query, normalize_embeddings=True)
            
            try:
                # Nouvelle API (1.12+)
                results = client.query_points(
                    collection_name="nuru_maths",
                    query=query_embedding.tolist(),
                    limit=3,
                    with_payload=True
                )
                results = results.points
            except AttributeError:
                # Ancienne API
                results = client.search(
                    collection_name="nuru_maths",
                    query_vector=query_embedding.tolist(),
                    limit=3,
                    with_payload=True
                )
            
            if results:
                for r in results:
                    print(f"   Score: {r.score:.3f} - {r.payload.get('text', '')[:60]}...")
            else:
                print("   ❌ Aucun résultat")
        
        print("\n✅ Test terminé!")
        
    except ImportError as e:
        print(f"❌ Erreur: {e}")
        print("\n📌 Installe les dépendances:")
        print("   pip install qdrant-client sentence-transformers")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("📋 MENU DE TEST")
    print("=" * 80)
    print("1. Test Qdrant simple (vecteurs manuels)")
    print("2. Test Qdrant + Embeddings réels")
    print("3. Quitter")
    print("=" * 80)
    
    choice = input("\nVotre choix (1-3): ")
    
    if choice == "1":
        test_qdrant_memory()
    elif choice == "2":
        test_with_embeddings()
    else:
        print("Au revoir!")
