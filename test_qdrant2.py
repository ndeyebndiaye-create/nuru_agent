import sys
import os
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from backend.app.rag.vector_indexer.retriever import HybridRetriever
from backend.app.rag.vector_indexer.config import VectorIndexerConfig

config = VectorIndexerConfig.from_env()
retriever = HybridRetriever(config)

print("Testing Qdrant connection and HybridRetriever...")
try:
    results = retriever.search_course_first("limites et continuité", top_k=5)
    
    course_docs = results.get("course_docs", [])
    supp_docs = results.get("supplement_docs", [])
    
    print(f"Found {len(course_docs)} course results and {len(supp_docs)} supplement results.")
    
    print("\n--- COURSE DOCS ---")
    for res in course_docs:
        meta = res.get("metadata", {})
        print(f"File: {meta.get('filename')} | Score: {res.get('score')} | Doc Type: {meta.get('doc_category')}")
        
    print("\n--- SUPPLEMENT DOCS ---")
    for res in supp_docs:
        meta = res.get("metadata", {})
        print(f"File: {meta.get('filename')} | Score: {res.get('score')} | Doc Type: {meta.get('doc_category')}")

except Exception as e:
    print(f"Error: {e}")

