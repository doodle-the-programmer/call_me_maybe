.PHONY: help install dev-install run test lint format clean

help:
	@echo "call_me_maybe - Function calling with a small LLM"
	@echo ""
	@echo "Available targets:"
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

install:
	uv pip install -e .

fix-accelerate:
	uv pip install accelerate

dev-install:
	uv pip install -e ".[dev]"

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
