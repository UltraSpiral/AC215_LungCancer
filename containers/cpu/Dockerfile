# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26
FROM ${PYTHON_IMAGE} AS dependencies
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy
# openslide-python may build its small C extension on ARM64.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir uv==0.12.21
WORKDIR /opt/cpu
COPY containers/cpu/pyproject.toml containers/cpu/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

FROM ${PYTHON_IMAGE} AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libstdc++6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=dependencies /opt/cpu /opt/cpu
COPY --from=dependencies /usr/local/bin/uv /usr/local/bin/uv
ENV PATH="/opt/cpu/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /content/LungCancer
COPY lungcancer ./lungcancer
COPY scripts ./scripts
COPY tests ./tests
COPY configs ./configs
COPY pyproject.toml ./pyproject.toml
USER 10001:10001
CMD ["python", "scripts/verify_cpu_bundle.py", "all", "--bundle", "/inputs", "--output", "/outputs"]
