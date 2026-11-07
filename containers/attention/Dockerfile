# syntax=docker/dockerfile:1
# Torch-CPU image for the attention MIL experiment (experiments/attention_mil).
# Separate from containers/cpu and the app images, which must stay torch-free.
ARG PYTHON_IMAGE=python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26

# Stage 1: install the locked packages (needs network; build tools stay in this stage).
FROM ${PYTHON_IMAGE} AS dependencies
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy
# openslide-python may build its small C extension on ARM64.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Same uv version that wrote experiments/attention_mil/uv.lock.
RUN python -m pip install --no-cache-dir uv==0.13.0
WORKDIR /opt/attention
COPY experiments/attention_mil/pyproject.toml experiments/attention_mil/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

# Stage 2: slim runtime with only the environment and the code.
FROM ${PYTHON_IMAGE} AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libstdc++6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=dependencies /opt/attention /opt/attention
ENV PATH="/opt/attention/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HOME=/tmp MPLCONFIGDIR=/tmp/matplotlib ATTN_BUNDLE=/inputs
WORKDIR /content/LungCancer
# lungcancer/ is reused read-only for its cache checks and metric definitions.
COPY lungcancer ./lungcancer
COPY experiments/attention_mil ./experiments/attention_mil
USER 10001:10001
CMD ["python", "-m", "pytest", "experiments/attention_mil", "-q", "-p", "no:cacheprovider"]
