FROM python:3.13.15-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
COPY containers/train/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --create-home app
WORKDIR /app
COPY lungcancer ./lungcancer
COPY scripts/track_training_vertex.py scripts/train_vertex.py ./scripts/
USER app
ENTRYPOINT ["python", "scripts/train_vertex.py"]
