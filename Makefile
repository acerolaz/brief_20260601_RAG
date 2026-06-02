.DEFAULT_GOAL := help

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

UV            = uv
DOCKER_COMPOSE = docker compose

# ═══════════════════════════════════════════════════════════════════════════════
# PHONY TARGETS (non-file targets)
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: help init init-db build up down logs docs lint format test test-unit test-acceptance coverage check

# ═══════════════════════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════════════════════

help: ## 📖 Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 LOCAL DEVELOPMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

init: ## Initialize local environment (venv + deps + .env)
	@echo "🔨 Setting up local development environment..."
	cp -n .env.example .env || true
	$(UV) venv
	$(UV) pip install -r requirements.txt
	@echo "✅ Setup complete! Run 'make up' to start services."

init-db: ## 🗄️  Initialize database (create pgvector extension + tables)
	@echo "📊 Running database migrations..."
	$(UV) run python -m src.infrastructure.config.init_db
	@echo "✅ Database initialized!"

# ═══════════════════════════════════════════════════════════════════════════════
# 🐳 DOCKER & SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

build: ## 🔨 Build Docker images (PostgreSQL + API)
	@echo "🔨 Building Docker images..."
	$(DOCKER_COMPOSE) build
	@echo "✅ Build complete!"

up: ## ⬆️  Start full stack (PostgreSQL + pgvector + API)
	@echo "🚀 Starting services..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Services running! API: http://localhost:8001"

down: ## ⬇️  Stop and remove all containers
	@echo "🛑 Stopping services..."
	$(DOCKER_COMPOSE) down
	@echo "✅ Services stopped!"

logs: ## 📋 Stream API container logs (Ctrl+C to exit)
	$(DOCKER_COMPOSE) logs -f api

docs: ## 📚 Open API Swagger documentation in browser
	@echo "📚 Opening Swagger UI at http://localhost:8001/docs"
	@command -v open >/dev/null 2>&1 && open http://localhost:8001/docs || echo "Please visit: http://localhost:8001/docs"

# ═══════════════════════════════════════════════════════════════════════════════
# 🧹 CODE QUALITY
# ═══════════════════════════════════════════════════════════════════════════════

lint: ## 🔍 Check code style with ruff linter
	@echo "🔍 Running linter..."
	$(UV) run ruff check src/ tests/
	@echo "✅ Lint check passed!"

format: ## ✨ Auto-format code with ruff
	@echo "✨ Formatting code..."
	$(UV) run ruff format src/ tests/
	@echo "✅ Formatting complete!"

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════════════════════

test: ## 🧪 Run full test suite (unit + acceptance tests)
	@echo "🧪 Running all tests..."
	$(UV) run pytest tests/ -v

test-unit: ## 🎯 Run unit tests only (fast, isolated)
	@echo "🎯 Running unit tests..."
	$(UV) run pytest tests/unit/ -v

test-acceptance: ## 🔗 Run acceptance tests (API contract validation)
	@echo "🔗 Running acceptance tests..."
	$(UV) run pytest tests/acceptance/ -v

coverage: ## 📊 Generate test coverage report
	@echo "📊 Generating coverage report..."
	$(UV) run pytest tests/ --cov=src --cov-report=term-missing

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 ALL-IN-ONE PIPELINES
# ═══════════════════════════════════════════════════════════════════════════════

check: format lint test ## ✅ Run format + lint + test (full QA pipeline)
	@echo "✅ All checks passed!"

