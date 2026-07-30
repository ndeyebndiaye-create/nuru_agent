# scripts/ingest_utils.py
"""
Utilitaires pour le pipeline d'ingestion.
"""
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import sys

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Suivi de progression du pipeline."""
    
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.processed = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        self.file_results = []
    
    def update(self, status: str, file_path: Path, error: Optional[str] = None):
        """Met à jour la progression."""
        self.processed += 1
        
        if status == "success":
            self.success += 1
        elif status == "failed":
            self.failed += 1
        elif status == "skipped":
            self.skipped += 1
        
        self.file_results.append({
            "file": str(file_path),
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        # Afficher la progression
        progress = (self.processed / self.total_files) * 100
        elapsed = time.time() - self.start_time
        sys.stdout.write(f"\r📊 Progression: {self.processed}/{self.total_files} ({progress:.1f}%) - {elapsed:.1f}s")
        sys.stdout.flush()
    
    def get_report(self) -> Dict[str, Any]:
        """Génère un rapport."""
        elapsed = time.time() - self.start_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_files": self.total_files,
            "processed": self.processed,
            "success": self.success,
            "failed": self.failed,
            "skipped": self.skipped,
            "elapsed_time": elapsed,
            "files": self.file_results
        }

def get_file_hash(file_path: Path) -> str:
    """Calcule le hash d'un fichier."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def load_processed_files(processed_dir: Path) -> Dict[str, str]:
    """Charge la liste des fichiers déjà traités."""
    index_file = processed_dir / "processed_index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_processed_files(processed_dir: Path, files: Dict[str, str]):
    """Sauvegarde la liste des fichiers traités."""
    index_file = processed_dir / "processed_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=2, ensure_ascii=False)

def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Récupère les informations d'un fichier."""
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "path": str(file_path),
        "size_mb": stat.st_size / (1024 * 1024),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "extension": file_path.suffix,
        "hash": get_file_hash(file_path)
    }

def save_chunks(chunks: List[Dict[str, Any]], file_path: Path, chunks_dir: Path):
    """Sauvegarde les chunks d'un fichier."""
    # Créer un nom unique
    name = file_path.stem + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    chunk_file = chunks_dir / f"{name}.json"
    
    with open(chunk_file, 'w', encoding='utf-8') as f:
        json.dump({
            "source": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "chunks": chunks
        }, f, indent=2, ensure_ascii=False)
    
    return chunk_file

def load_chunks(chunk_file: Path) -> List[Dict[str, Any]]:
    """Charge les chunks d'un fichier."""
    with open(chunk_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("chunks", [])