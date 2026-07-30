# 📖 README COMPLET - NURU

```markdown
# 🌟 NURU - Tuteur IA pour le Programme Scolaire Sénégalais

<div align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10%2B-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status">
</div>

<br>

<div align="center">
  <h3>🇸🇳 Un assistant intelligent pour l'apprentissage des mathématiques</h3>
  <p><strong>NURU</strong> (qui signifie "lumière" en wolof) guide les élèves sénégalais à travers le programme de mathématiques de la Terminale S1.</p>
</div>

---

## 📋 Table des Matières

- [À Propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [Développement](#-développement)
- [Déploiement](#-déploiement)
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## 🎯 À Propos

**NURU** est un tuteur intelligent basé sur l'IA, spécialement conçu pour le programme scolaire sénégalais. Il utilise un système de Recherche Augmentée par Génération (RAG) combiné à un graphe de connaissances pour fournir des explications personnalisées, des exercices adaptés et un accompagnement pas à pas.

### Pourquoi NURU ?

- 🎓 **Spécifique au Sénégal** : Conçu pour le programme de Mathématiques Terminale S1
- 🤖 **Intelligence Artificielle** : Utilise des agents IA pour un tutorat personnalisé
- 📚 **Basé sur les sources officielles** : S'appuie sur les manuels et programmes officiels
- 🌍 **Accessible** : Interface web simple, fonctionne sur navigateur
- 💡 **Pédagogique** : Guide l'élève, ne donne pas la réponse directement

---

## ✨ Fonctionnalités

### 🤖 Agents Spécialisés

| Agent | Rôle | Fonctionnalités |
|-------|------|-----------------|
| **Orchestrateur** | Coordination | Analyse la demande, active les bons agents |
| **Planificateur** | Planification | Détermine l'intention et le niveau d'aide |
| **Cours** | Explications | Explique les concepts avec exemples |
| **Exercices** | Entraînement | Génère et corrige des exercices adaptés |
| **Quiz** | Évaluation | Propose des QCM, Vrai/Faux, questions ouvertes |
| **Vérificateur** | Contrôle | Vérifie la cohérence et réduit les hallucinations |

### 📚 Système RAG

- 🔍 Recherche hybride (dense + sparse)
- 📄 Indexation des documents officiels
- 🎯 Filtrage par métadonnées (classe, série, chapitre)
- 📊 Reranking des résultats

### 🧠 Knowledge Graph

- 🔗 Relations entre concepts mathématiques
- 📈 Prérequis et dépendances
- 🗺️ Parcours d'apprentissage personnalisés
- 🎓 Recommandation de concepts

### 🎨 Interface Utilisateur

- 💬 Chat conversationnel avec NURU
- 📱 Design responsive aux couleurs du Sénégal
- ⭐ Système de feedback
- 📊 Suivi de progression
- 🚀 Suggestions de questions rapides

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR                     │
│                     Gradio (Port 7860)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       API FASTAPI                           │
│                    (Port 8000) /docs                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     AGENTS LANGGRAPH                        │
│  Orchestrateur → Planificateur → Agents Spécialisés        │
└─────────────────────────────────────────────────────────────┘
                    ↓                            ↓
┌──────────────────────────┐      ┌──────────────────────────┐
│   QDRANT (Vectors)       │      │  NEO4J (Knowledge Graph) │
│   Recherche sémantique   │      │  Relations entre concepts│
└──────────────────────────┘      └──────────────────────────┘
                    ↓                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE D'INGESTION                      │
│  PDFs → Parser → Chunker → Metadata → Indexation           │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Technologies

### Backend

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| **Python** | 3.10+ | Langage principal |
| **FastAPI** | 0.104+ | API REST |
| **LangGraph** | 0.0.20+ | Orchestration multi-agents |
| **Qdrant** | Cloud | Base vectorielle |
| **Neo4j** | 5.x | Knowledge Graph |
| **Sentence-Transformers** | 2.2.0+ | Embeddings (BGE-M3) |

### Frontend

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| **Gradio** | 4.0+ | Interface utilisateur |
| **CSS** | Personnalisé | Design et thème Sénégal |

### Outils

| Technologie | Utilisation |
|-------------|-------------|
| **PyMuPDF** | Extraction PDF |
| **Nougat** | OCR Mathématiques |
| **SymPy** | Calcul formel |
| **Uvicorn** | Serveur ASGI |

---

## 📦 Installation

### Prérequis

```bash
# Python 3.10 ou supérieur
python --version

# Git
git --version

# Espace disque : ~2GB
```

### 1. Cloner le Projet

```bash
# Dans votre terminal
git clone https://github.com/your-username/nuru.git
cd nuru
```

### 2. Créer l'Environnement Virtuel

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les Dépendances

```bash
# Installation principale
pip install --upgrade pip
pip install -r requirements.txt

# Si le fichier n'existe pas, installez manuellement :
pip install pymupdf pillow tqdm python-dotenv
pip install fastapi uvicorn gradio
pip install sentence-transformers
pip install qdrant-client neo4j
pip install langgraph langchain
pip install transformers torch scikit-learn
```

### 4. Configurer les Variables d'Environnement

```bash
# Créer le fichier .env
cat > .env << 'EOF'
# NURU - Configuration

# QDRANT Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key-here
QDRANT_COLLECTION=nuru_maths

# NEO4J
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
NEO4J_DATABASE=neo4j

# Gemini API (Optionnel)
GEMINI_API_KEY=your-gemini-api-key-here

# Configuration
LOG_LEVEL=INFO
DEBUG=True
ENVIRONMENT=development
API_URL=http://localhost:8000
FRONTEND_PORT=7860
EOF
```

### 5. Préparer les Données

```bash
# Créer les dossiers
mkdir -p data/raw data/processed data/ingestion_logs logs

# Placer les PDFs du programme sénégalais dans data/raw/
# Exemple :
# data/raw/cours/01_Revisions_trigonometrie.pdf
# data/raw/exercices/Chap1_Probabilite/TD1-Probabilite-TS1.pdf
```

---

## 🚀 Utilisation

### Mode Développement

#### 1. Lancer l'API

```bash
# Terminal 1
python -m backend.api.main
```

#### 2. Lancer le Frontend

```bash
# Terminal 2
python -m frontend.app
```

#### 3. Accéder à l'Interface

```bash
# Ouvrir dans le navigateur
http://localhost:7860
```

### Mode Production

```bash
# Lancer tout en une seule commande
chmod +x run_all.sh
./run_all.sh

# Ou avec Docker (à venir)
docker-compose up -d
```

### Pipeline d'Ingestion

```bash
# Traiter tous les documents
python -m scripts.ingest_pipeline

# Traiter seulement 5 fichiers
python -m scripts.ingest_pipeline --limit 5

# Forcer le retraitement
python -m scripts.ingest_pipeline --force

# Voir le rapport
cat data/processed/reports/ingestion_report_*.json
```

---

## 📁 Structure du Projet

```
nuru/
├── backend/                         # Backend Python
│   ├── agents/                      # Agents LangGraph
│   │   ├── orchestrator.py          # Agent orchestrateur
│   │   ├── planner.py              # Agent planificateur
│   │   ├── cours_agent.py          # Agent cours
│   │   ├── exercices_agent.py      # Agent exercices
│   │   ├── quiz_agent.py           # Agent quiz
│   │   ├── verifier_agent.py       # Agent vérificateur
│   │   ├── state.py                # Gestion d'état
│   │   └── config.py               # Configuration
│   │
│   ├── api/                         # API FastAPI
│   │   ├── main.py                 # Point d'entrée
│   │   ├── routes/                 # Endpoints
│   │   ├── models/                 # Pydantic models
│   │   ├── middleware/             # Middleware
│   │   └── dependencies/           # Injection de dépendances
│   │
│   └── rag/                         # Système RAG
│       ├── document_parser/        # Extraction PDF
│       ├── chunker/                # Chunking pédagogique
│       ├── metadata_extractor/     # Métadonnées
│       ├── vector_indexer/         # Qdrant
│       └── knowledge_graph/        # Neo4j
│
├── frontend/                        # Interface Gradio
│   ├── app.py                      # Application principale
│   ├── components/                 # Composants UI
│   └── utils/                      # Utilitaires
│
├── scripts/                         # Scripts utilitaires
│   ├── ingest_pipeline.py          # Pipeline d'ingestion
│   ├── test_parser.py              # Test du parser
│   ├── test_chunker.py             # Test du chunker
│   ├── test_metadata.py            # Test des métadonnées
│   ├── test_agents.py              # Test des agents
│   ├── test_vector_indexer.py      # Test Qdrant
│   ├── test_knowledge_graph.py     # Test Neo4j
│   ├── test_api.py                 # Test API
│   ├── diagnostic.py               # Diagnostic
│   └── check_setup.py              # Vérification
│
├── data/                            # Données
│   ├── raw/                        # PDFs source
│   ├── processed/                  # Résultats
│   │   ├── chunks/                 # Chunks sauvegardés
│   │   └── reports/                # Rapports
│   └── ingestion_logs/             # Logs
│
├── tests/                           # Tests unitaires
│   ├── test_parser_unit.py
│   ├── test_chunker_unit.py
│   ├── test_metadata_unit.py
│   └── test_integration.py
│
├── logs/                            # Logs d'exécution
├── .env                             # Variables d'environnement
├── requirements.txt                 # Dépendances
├── run_all.sh                      # Lancement complet
├── Dockerfile                      # Docker
├── LICENSE                         # Licence
└── README.md                       # Ce fichier
```

---

## 🔧 Développement

### Tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Tests unitaires spécifiques
python -m pytest tests/test_parser_unit.py -v
python -m pytest tests/test_chunker_unit.py -v
python -m pytest tests/test_metadata_unit.py -v

# Scripts de test
python scripts/test_parser.py
python scripts/test_chunker.py
python scripts/test_metadata.py
python scripts/test_agents.py

# Diagnostic complet
python scripts/diagnostic.py
```

### Vérification de l'Environnement

```bash
python scripts/check_setup.py
```

### Nettoyage

```bash
# Supprimer les fichiers temporaires
rm -rf data/processed/chunks/* data/processed/reports/*
rm -rf logs/*

# Supprimer l'environnement virtuel
rm -rf venv

# Réinitialiser le projet
git clean -fd
```

---

## 🌐 Déploiement

### Hugging Face Spaces

```bash
# 1. Créer un compte sur Hugging Face
# https://huggingface.co/join

# 2. Créer un nouveau Space avec Docker

# 3. Ajouter ce Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7860
CMD ["python", "-m", "frontend.app"]
```

### Docker

```bash
# Build
docker build -t nuru:latest .

# Run
docker run -p 7860:7860 -p 8000:8000 nuru:latest
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    command: python -m backend.api.main
    ports:
      - "8000:8000"
    env_file: .env
  
  frontend:
    build: .
    command: python -m frontend.app
    ports:
      - "7860:7860"
    env_file: .env
    depends_on:
      - api
```

```bash
docker-compose up -d
```

---

## 📊 API Documentation

Une fois l'API lancée, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérifier la santé du service |
| `/chat/` | POST | Envoyer un message à NURU |
| `/chat/search` | POST | Rechercher dans la base |
| `/chat/session/{id}` | GET | Récupérer une session |
| `/chat/feedback` | POST | Envoyer un feedback |

---

## 🤝 Contribution

### Comment Contribuer

1. **Fork** le projet
2. **Créer une branche** : `git checkout -b feature/ma-fonctionnalite`
3. **Commiter** : `git commit -m 'Ajout de ma fonctionnalité'`
4. **Pousser** : `git push origin feature/ma-fonctionnalite`
5. **Pull Request** sur GitHub

### Règles de Contribution

- 📝 Code commenté en français ou anglais
- 🧪 Tests unitaires pour chaque nouvelle fonctionnalité
- 📖 Documentation mise à jour
- 🎨 Respect des normes PEP 8
- ✅ `pytest tests/` doit passer

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **Ministère de l'Éducation du Sénégal** pour le programme officiel
- **Khan Academy** pour l'inspiration (Khanmigo)
- **Communauté open-source** pour les outils utilisés
- **ALiVE & DiCENTRE4AI** pour leur travail sur l'IA au Sénégal
- **Tous les enseignants et élèves** qui ont contribué aux retours

---

## 📞 Contact

- **Email** : nuru@education.sn
- **GitHub** : [https://github.com/your-username/nuru](https://github.com/your-username/nuru)
- **Documentation** : [https://nuru.readthedocs.io](https://nuru.readthedocs.io)

---

## 🔮 Feuille de Route

### Version 1.0.0 (Actuelle)
- ✅ Extraction des PDFs
- ✅ Chunking pédagogique
- ✅ Métadonnées automatiques
- ✅ Indexation vectorielle (Qdrant)
- ✅ Knowledge Graph (Neo4j)
- ✅ Agents multi-agents
- ✅ API REST
- ✅ Interface Gradio
- ✅ Pipeline d'ingestion

### Version 1.1.0 (À venir)
- 🔄 Intégration de Gemini API pour les réponses
- 🔄 Support de Nougat pour les formules mathématiques
- 🔄 Calcul formel avec SymPy
- 🔄 Reconnaissance vocale
- 🔄 Mode hors-ligne

### Version 2.0.0 (Futur)
- 🔄 Support de toutes les classes (1ère, 2nde)
- 🔄 Autres disciplines (Physique, SVT)
- 🔄 Application mobile
- 🔄 Intégration LMS (Moodle)
- 🔄 Analyse prédictive des performances

---

## ⚠️ Notes Importantes

### Pour l'Ingestion des Données

1. **Formats supportés** : PDF principalement
2. **Taille recommandée** : Fichiers < 50MB
3. **Nom des fichiers** : Contenir des informations utiles (ex: "Chapitre_3_Derivabilite.pdf")
4. **Structure** : Respecter l'arborescence du programme

### Pour Qdrant Cloud

- 🆓 **Gratuit jusqu'à 1GB** de données vectorielles
- 🔑 **API Key** nécessaire
- 🌐 **URL du cluster** à configurer

### Pour Neo4j

- 🆓 **Version Community** gratuite
- 💻 **Installation locale** ou **Cloud**
- 📊 **Indexation** recommandée pour les performances

---

## 🎓 Citations

Si vous utilisez NURU dans un cadre académique, veuillez citer :

```bibtex
@software{nuru2024,
  author = {NURU Team},
  title = {NURU: Tuteur IA pour le Programme Scolaire Sénégalais},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/your-username/nuru}
}
```

---

<div align="center">
  <h3>🇸🇳 NURU - La lumière de l'apprentissage au Sénégal</h3>
  <p>Développé avec ❤️ pour les élèves et enseignants sénégalais</p>
  <br>
  <img src="https://img.shields.io/badge/Made%20with-Python-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Made%20with-AI-purple.svg" alt="AI">
  <img src="https://img.shields.io/badge/For-Senegal-green.svg" alt="Senegal">
</div>
```

---

## 📄 Fichiers Supplémentaires

### requirements.txt

```txt
# NURU - Dépendances Principales
pymupdf>=1.23.0
pillow>=10.0.0
tqdm>=4.65.0
python-dotenv>=1.0.0

# API et Interface
fastapi>=0.104.0
uvicorn>=0.24.0
gradio>=4.0.0

# IA et ML
sentence-transformers>=2.2.0
transformers>=4.35.0
torch>=2.0.0
scikit-learn>=1.3.0

# Bases de Données
qdrant-client>=1.9.0
neo4j>=5.14.0

# Agents et Orchestration
langgraph>=0.0.20
langchain>=0.1.0

# Utilitaires
requests>=2.31.0
numpy>=1.24.0
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Exposer les ports
EXPOSE 7860 8000

# Lancer l'application
CMD ["python", "-m", "frontend.app"]
```

---

**Voilà ! NURU est maintenant prêt à être déployé. Bonne lecture !** 🚀