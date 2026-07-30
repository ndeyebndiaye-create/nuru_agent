# scripts/ingest_pipeline.py
"""
Pipeline d'ingestion complet pour NURU.
"""
import sys
from pathlib import Path
import logging
import json
import time
from datetime import datetime
import argparse
from typing import List,Any,Optional,Dict

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Charge .env AVANT tout import de config *.from_env() : sans cela, QDRANT_URL
# retombe sur sa valeur par defaut quand le script est lance directement, hors du
# wrapper run_backend_windows.ps1 qui exporte .env pour l'API.
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from scripts.ingest_config import IngestConfig
from scripts.ingest_utils import (
    ProgressTracker, get_file_hash, load_processed_files,
    save_processed_files, get_file_info, save_chunks,
    load_chunks
)

# Import des modules backend
from backend.app.rag.document_parser import DocumentParser, ParserConfig
from backend.app.rag.chunker import ChunkingPipeline, ChunkerConfig
from backend.app.rag.metadata_extractor import MetadataMerger, MetadataConfig
from backend.app.rag.vector_indexer import VectorIndexer, VectorIndexerConfig

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path("data/ingestion_logs/pipeline.log"))
    ]
)
logger = logging.getLogger(__name__)

class IngestPipeline:
    """
    Pipeline d'ingestion complet.
    """
    
    def __init__(self, config: IngestConfig = None):
        self.config = config or IngestConfig()
        self.processed_files = load_processed_files(self.config.processed_dir)
        
        # Initialiser les composants
        self._init_components()
        
        # Statistiques
        self.stats = {
            "start_time": datetime.now(),
            "total_files": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "chunks_created": 0,
            "indexed_chunks": 0
        }
    
    def _init_components(self):
        """Initialise les composants du pipeline."""
        try:
            # Document Parser
            self.parser = DocumentParser(use_nougat=self.config.use_nougat)
            logger.info("✅ DocumentParser initialisé")
            
            # Chunker
            chunker_config = ChunkerConfig(
                min_chunk_size=self.config.chunk_min_size,
                max_chunk_size=self.config.chunk_max_size,
                ideal_chunk_size=self.config.chunk_ideal_size
            )
            self.chunker = ChunkingPipeline(chunker_config)
            logger.info("✅ Chunker initialisé")
            
            # Metadata Extractor
            metadata_config = MetadataConfig()
            self.metadata_extractor = MetadataMerger(metadata_config)
            logger.info("✅ MetadataExtractor initialisé")
            
            # Vector Indexer
            vector_config = VectorIndexerConfig.from_env()
            vector_config.qdrant_collection = self.config.qdrant_collection
            self.vector_indexer = VectorIndexer(vector_config)
            logger.info("✅ VectorIndexer initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation: {e}")
            raise
    
    def run(self, force: bool = False, limit: int = None):
        """
        Exécute le pipeline.
        
        Args:
            force: Forcer le retraitement de tous les fichiers
            limit: Limiter le nombre de fichiers à traiter
        """
        logger.info("=" * 80)
        logger.info("🚀 DÉMARRAGE DU PIPELINE D'INGESTION")
        logger.info("=" * 80)
        
        # 1. Trouver les fichiers
        files = self._find_files(limit)
        self.stats["total_files"] = len(files)
        
        if not files:
            logger.warning("⚠️ Aucun fichier trouvé")
            return
        
        logger.info(f"📁 {len(files)} fichiers trouvés")
        
        # 2. Initialiser le tracker de progression
        tracker = ProgressTracker(len(files))
        
        # 3. Traiter chaque fichier
        all_chunks = []
        
        for file_path in files:
            # Vérifier si déjà traité
            if not force and self._should_skip(file_path):
                tracker.update("skipped", file_path)
                continue
            
            try:
                # Traiter le fichier
                chunks = self._process_file(file_path)
                
                if chunks:
                    all_chunks.extend(chunks)
                    self.stats["chunks_created"] += len(chunks)
                    tracker.update("success", file_path)
                else:
                    tracker.update("failed", file_path, "Aucun chunk créé")
                
            except Exception as e:
                logger.error(f"❌ Erreur sur {file_path.name}: {e}")
                tracker.update("failed", file_path, str(e))
        
        # 4. Indexer tous les chunks
        if all_chunks:
            self._index_chunks(all_chunks)
        
        # 5. Générer le rapport
        self._generate_report(tracker)
        
        logger.info("=" * 80)
        logger.info("✅ PIPELINE TERMINÉ")
        logger.info("=" * 80)
    
    def _find_files(self, limit: int = None) -> List[Path]:
        """Trouve tous les fichiers à traiter."""
        extensions = self.config.file_extensions
        files = []
        
        for ext in extensions:
            files.extend(self.config.raw_dir.rglob(f"*{ext}"))
        
        # Filtrer par taille
        files = [f for f in files if f.stat().st_size < self.config.max_file_size_mb * 1024 * 1024]
        
        # Trier par nom
        files.sort(key=lambda x: x.name)
        
        if limit:
            files = files[:limit]
        
        return files
    
    def _should_skip(self, file_path: Path) -> bool:
        """Vérifie si le fichier doit être ignoré."""
        if not self.config.skip_existing:
            return False
        
        file_hash = get_file_hash(file_path)
        processed = self.processed_files.get(str(file_path))
        
        return processed == file_hash
    
    def _process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Traite un fichier individuel.
        
        Returns:
            Liste de chunks
        """
        logger.info(f"📄 Traitement: {file_path.name}")
        
        # 1. Extraire le texte
        logger.info(f"   📖 Extraction du texte...")
        text = self.parser.extract(file_path)
        
        if not text or len(text) < 10:
            logger.warning(f"   ⚠️ Texte vide ou trop court")
            return []
        
        logger.info(f"   ✅ {len(text)} caractères extraits")
        
        # 2. Extraire les métadonnées
        logger.info(f"   📋 Extraction des métadonnées...")
        metadata = self.metadata_extractor.extract_metadata(file_path, text)
        logger.info(f"   ✅ Métadonnées: {', '.join(metadata.keys())}")
        
        # 3. Chunker
        logger.info(f"   ✂️ Chunking...")
        chunks = self.chunker.process(text, metadata)
        logger.info(f"   ✅ {len(chunks)} chunks créés")
        
        # 4. Sauvegarder les chunks
        if self.config.save_chunks and chunks:
            chunk_file = save_chunks(chunks, file_path, self.config.chunks_dir)
            logger.info(f"   💾 Chunks sauvegardés: {chunk_file}")
        
        # 5. Mettre à jour la liste des fichiers traités
        # IMPORTANT : on ne marque le fichier comme "traité" que s'il a
        # réellement produit des chunks. Sinon, un fichier dont le texte
        # s'extrait mais dont le chunking échoue (0 chunk) serait marqué
        # "fait" pour toujours et ne serait plus jamais retenté, même
        # après correction du problème sous-jacent.
        if chunks:
            file_hash = get_file_hash(file_path)
            self.processed_files[str(file_path)] = file_hash
            save_processed_files(self.config.processed_dir, self.processed_files)
        else:
            logger.warning(f"   ⚠️ 0 chunk produit pour {file_path.name} — pas marqué comme traité, sera retenté au prochain lancement.")
        
        return chunks
    
    def _index_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexe les chunks dans Qdrant."""
        logger.info(f"📊 Indexation de {len(chunks)} chunks dans Qdrant...")
        
        try:
            stats = self.vector_indexer.index_chunks(chunks)
            self.stats["indexed_chunks"] = stats.get("indexed", 0)
            logger.info(f"✅ {stats.get('indexed', 0)} chunks indexés")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'indexation: {e}")
    
    def _generate_report(self, tracker: ProgressTracker):
        """Génère un rapport final."""
        report = tracker.get_report()
        
        # Ajouter les statistiques du pipeline
        report["pipeline_stats"] = {
            "chunks_created": self.stats["chunks_created"],
            "indexed_chunks": self.stats["indexed_chunks"]
        }
        
        # Sauvegarder le rapport
        report_file = self.config.reports_dir / f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Afficher le résumé
        print("\n" + "=" * 80)
        print("📊 RAPPORT D'INGESTION")
        print("=" * 80)
        print(f"📁 Fichiers traités: {report['total_files']}")
        print(f"✅ Succès: {report['success']}")
        print(f"❌ Échecs: {report['failed']}")
        print(f"⏭️  Ignorés: {report['skipped']}")
        print(f"⏱️  Temps: {report['elapsed_time']:.2f}s")
        print(f"\n📊 Statistiques du pipeline:")
        print(f"   📝 Chunks créés: {self.stats['chunks_created']}")
        print(f"   📈 Chunks indexés: {self.stats['indexed_chunks']}")
        print(f"\n📄 Rapport détaillé: {report_file}")
        print("=" * 80)

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Pipeline d'ingestion NURU")
    parser.add_argument("--force", action="store_true", help="Forcer le retraitement")
    parser.add_argument("--limit", type=int, help="Limiter le nombre de fichiers")
    parser.add_argument("--config", type=str, help="Chemin du fichier de configuration")
    
    args = parser.parse_args()
    
    # Charger la configuration
    if args.config:
        # Charger depuis un fichier JSON
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            config = IngestConfig(**config_data)
    else:
        config = IngestConfig()
    
    # Exécuter le pipeline
    pipeline = IngestPipeline(config)
    pipeline.run(force=args.force, limit=args.limit)

if __name__ == "__main__":
    main()
