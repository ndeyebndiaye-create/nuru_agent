# frontend/Dockerfile - NURU Frontend (Gradio)
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir gradio==6.20.0 "requests>=2.31.0"

COPY frontend/ ./frontend/

EXPOSE 7860

ENV PYTHONUNBUFFERED=1 \
    API_URL=http://backend:8080 \
    GRADIO_PORT=7860

CMD ["python", "-m", "frontend.gradio_app"]
