.PHONY: help venv venv-shell init-venv install dev-install run test test-cov lint format clean cache fix-accelerate

CACHE_BASE ?= $(HOME)/sgoinfre/.cache
PROJECT_ENV ?= $(HOME)/sgoinfre/.venvs/call_me_maybe
export UV_CACHE_DIR := $(CACHE_BASE)/.uv_cache
export UV_PROJECT_ENVIRONMENT := $(PROJECT_ENV)
export UV_LINK_MODE := copy
export HF_HOME := $(CACHE_BASE)/huggingface
export HF_HUB_CACHE := $(CACHE_BASE)/huggingface/hub
export TRANSFORMERS_CACHE := $(CACHE_BASE)/huggingface/transformers
export TORCH_HOME := $(CACHE_BASE)/torch
export XDG_CACHE_HOME := $(CACHE_BASE)/xdg

help:
	@echo "call_me_maybe - Function calling with a small LLM"
	@echo ""
	@echo "Available targets:"
	@echo "  venv         Create virtual environment in PROJECT_ENV"
	@echo "  venv-shell   Start an interactive shell with the venv activated"
	@echo "  init-venv    Create virtual environment and install dependencies"
	@echo "  install      Install dependencies"
	@echo "  dev-install  Install dependencies including dev tools (pytest, etc)"
	@echo "  run          Run the pipeline with default arguments"
	@echo "  test         Run the test suite"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run linters (flake8, mypy)"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Remove build artifacts and cache files"
	@echo "  help         Show this help message"
	@echo ""
	@echo "Run with custom files:"
	@echo "  make run DEFS=path/to/defs.json INPUT=path/to/input.json OUTPUT=path/to/output.json"

cache:
	@echo "Using cache root: $(CACHE_BASE)"
	@echo "Using project env: $(PROJECT_ENV)"

venv: cache
	@mkdir -p "$(dir $(PROJECT_ENV))"
	python3 -m venv "$(PROJECT_ENV)"

venv-shell: venv
	@echo "Starting shell with venv activated (exit to return)..."
	@. "$(PROJECT_ENV)/bin/activate" && exec "$$SHELL" -i

install: cache
	pip install uv
	uv sync

fix-accelerate: cache
	uv pip install accelerate

dev-install: cache
	pip install uv
	uv sync --extra dev

DEFS ?= data/input/functions_definition.json
INPUT ?= data/input/function_calling_tests.json
OUTPUT ?= data/output/function_calling_results.json

run:
	uv run python -m src --functions_definition $(DEFS) --input $(INPUT) --output $(OUTPUT)

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	@echo "Running flake8..."
	flake8 src/ tests/ --max-line-length=79 --count --show-source
	@echo ""
	@echo "Running mypy..."
	mypy src/ --ignore-missing-imports

format:
	@echo "Running black..."
	black src/ tests/
	@echo ""
	@echo "Running isort..."
	isort src/ tests/

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "Done!"

