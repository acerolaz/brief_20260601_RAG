.DEFAULT_GOAL := help
UV            = uv
DOCKER_COMPOSE = docker compose

.PHONY: help
help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-22s\033[0m %s\n", $$1, $$2}'

# ── Local dev setup ───────────────────────────────────────────────────────────

.PHONY: init
init: ## Copy .env.example → .env, create venv and install dependencies
	cp -n .env.example .env || true
	$(UV) venv
	$(UV) pip install -r requirements.txt

.PHONY: init-db
init-db: ## Run DB migrations (create pgvector extension + tables)
	$(UV) run python -m src.infrastructure.config.init_db

# ── Docker ────────────────────────────────────────────────────────────────────

.PHONY: build
build: ## Build Docker images
	$(DOCKER_COMPOSE) build

.PHONY: up
up: ## Start the full stack (pgvector + API)
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down: ## Stop and remove containers
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs: ## Tail API logs
	$(DOCKER_COMPOSE) logs -f api

# ── Quality ───────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Run ruff linter
	$(UV) run ruff check src/ tests/

.PHONY: format
format: ## Auto-format with ruff
	$(UV) run ruff format src/ tests/

.PHONY: test
test: ## Run the full test suite (unit + acceptance)
	$(UV) run pytest tests/ -v

.PHONY: test-unit
test-unit: ## Run unit tests only
	$(UV) run pytest tests/unit/ -v

.PHONY: test-acceptance
test-acceptance: ## Run acceptance (API contract) tests only
	$(UV) run pytest tests/acceptance/ -v

.PHONY: coverage
coverage: ## Run tests with coverage report
	$(UV) run pytest tests/ --cov=src --cov-report=term-missing

# ── All-in-one ────────────────────────────────────────────────────────────────

.PHONY: check
check: format lint test ## Format, lint and test in one shot

