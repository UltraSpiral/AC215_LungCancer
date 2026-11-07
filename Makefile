LC_CPU_UID := $(shell id -u)
LC_CPU_GID := $(shell id -g)
export LC_CPU_UID LC_CPU_GID
CPU_COMPOSE = docker compose -f compose.cpu.yml
LC_APP_UID := $(shell id -u)
LC_APP_GID := $(shell id -g)
export LC_APP_UID LC_APP_GID
APP_COMPOSE = docker compose -f compose.app.yml

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

.PHONY: app-up app-stop app-resume app-down app-test app-logs
app-up:
	mkdir -p local_outputs/app/jobs
	$(APP_COMPOSE) up --build -d --wait --wait-timeout 120 api web
	python3 scripts/check_app_ready.py
app-stop:
	$(APP_COMPOSE) stop api web
app-resume:
	$(APP_COMPOSE) up -d --wait --wait-timeout 120 api web
	python3 scripts/check_app_ready.py
app-down:
	$(APP_COMPOSE) down
app-test:
	mkdir -p local_outputs/app/jobs
	$(APP_COMPOSE) --profile test build app-tests
	$(APP_COMPOSE) --profile test run --rm app-tests
app-logs:
	$(APP_COMPOSE) logs --no-color api web

.PHONY: ms2-demo
ms2-demo:
	python3 scripts/run_ms2_demo.py
