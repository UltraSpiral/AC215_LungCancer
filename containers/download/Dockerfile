FROM python:3.13.15-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY containers/download/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --create-home app
WORKDIR /app
COPY lungcancer ./lungcancer
COPY scripts/download_cohort.py ./scripts/download_cohort.py
USER app
ENTRYPOINT ["python", "scripts/download_cohort.py"]
