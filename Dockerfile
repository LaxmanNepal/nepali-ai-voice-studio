FROM python:3.11-slim

ARG BACKEND_REQ=backends/pocket_tts/requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7860
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ${BACKEND_REQ} /tmp/backend-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt

COPY app.py ./
COPY app ./app
COPY backends ./backends
COPY models ./models
EXPOSE 7860
CMD ["python", "app.py"]
