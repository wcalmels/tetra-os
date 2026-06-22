FROM python:3.11-slim
LABEL maintainer="Walter Calmels K."
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p tetra_data/models tetra_data/results tetra_data/logs
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8080/api/status || exit 1
CMD ['python', '-m', 'tetra_os.api.server']
