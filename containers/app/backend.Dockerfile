# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26
FROM ${PYTHON_IMAGE} AS dependencies
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir uv==0.12.21
WORKDIR /opt/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

FROM dependencies AS test-dependencies
RUN uv sync --frozen --no-install-project --no-cache

FROM ${PYTHON_IMAGE} AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libstdc++6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=dependencies /opt/backend /opt/backend
ENV PATH="/opt/backend/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    TMPDIR=/work/uploads OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
WORKDIR /opt/app
COPY lungcancer ./lungcancer
COPY scripts ./scripts
COPY backend ./backend
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

FROM runtime AS tests
COPY --from=test-dependencies /opt/backend /opt/backend
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "backend/tests", "--junitxml=/work/jobs/backend-tests.xml"]
