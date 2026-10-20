LC_CPU_UID := $(shell id -u)
LC_CPU_GID := $(shell id -g)
export LC_CPU_UID LC_CPU_GID
CPU_COMPOSE = docker compose -f compose.cpu.yml

.PHONY: cpu-build cpu-check cpu-unit cpu-cache cpu-real
cpu-build:
	$(CPU_COMPOSE) build cpu-check
cpu-check: cpu-build
	mkdir -p local_outputs/cpu
	$(CPU_COMPOSE) run --rm cpu-check
cpu-unit: cpu-build
	mkdir -p local_outputs/cpu
	$(CPU_COMPOSE) run --rm unit-tests
cpu-cache: cpu-build
	mkdir -p local_outputs/cpu
	$(CPU_COMPOSE) run --rm cached-embeddings
cpu-real: cpu-build
	mkdir -p local_outputs/cpu
	$(CPU_COMPOSE) run --rm real-preprocess
