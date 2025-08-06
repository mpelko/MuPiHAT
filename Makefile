.PHONY: help install dev-install format lint check clean test

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv pip install -r requirements.txt

dev-install: ## Install development dependencies
	uv pip install -r requirements-dev.txt
	uv pip install -e .

format: ## Format code with ruff
	ruff format .

lint: ## Run ruff linter
	ruff check .

check: ## Run ruff linter and formatter (dry run)
	ruff check .
	ruff format --check .

fix: ## Auto-fix linting issues
	ruff check --fix .
	ruff format .

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

sync: ## Sync dependencies with uv
	uv pip sync requirements-dev.txt

venv: ## Create virtual environment with uv
	uv venv
	@echo "Activate with: source .venv/bin/activate"

lock: ## Generate lock file (when using uv project mode)
	@echo "Use 'uv lock' when ready to switch to uv project mode"

test: ## Run tests (placeholder for when tests are added)
	@echo "No tests configured yet. Add your test command here."