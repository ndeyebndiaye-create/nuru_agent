# Dockerfile - NURU Backend (API FastAPI + Agents LangGraph)
FROM python:3.11-slim

# Dépendances système : build tools (pour certains paquets scientifiques),
# poppler/tesseract si tu actives l'OCR plus tard.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python d'abord (meilleur cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# Dossiers de données (montés en volume en production)
RUN mkdir -p data/raw data/processed data/ingestion_logs logs

EXPOSE 8080

ENV PORT=8080 \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["python", "-m", "backend.app.api.main"]
