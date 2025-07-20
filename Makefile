# ClynBoozle Development Makefile

.PHONY: help setup test lint format type-check quality clean build run dev

# Default target
help:
	@echo "ClynBoozle Development Commands:"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  setup         - Set up development environment"
	@echo "  clean         - Clean temporary files and caches"
	@echo ""
	@echo "Code Quality:"
	@echo "  format        - Format code with black"
	@echo "  lint          - Lint code with flake8"
	@echo "  type-check    - Check types with mypy"
	@echo "  quality       - Run all quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Run all tests"
	@echo "  test-models   - Run model tests only"
	@echo "  test-cov      - Run tests with coverage"
	@echo ""
	@echo "Application:"
	@echo "  run           - Run the application"
	@echo "  dev           - Run in development mode with debug logging"
	@echo "  build         - Build distributable application"

# Environment setup
setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/pre-commit install

# Code formatting
format:
	./venv/bin/black src/clynboozle tests --line-length=100

# Linting
lint:
	./venv/bin/flake8 src/clynboozle --max-line-length=100 --ignore=F401,E501,W503,W504 --statistics
	./venv/bin/flake8 tests --max-line-length=100 --ignore=F401,E501,W503,W504,E402 --statistics

# Type checking
type-check:
	./venv/bin/mypy src/clynboozle --ignore-missing-imports --no-strict-optional

# Combined quality checks
quality: format lint
	@echo "✅ Code quality checks completed"

# Testing
test:
	./venv/bin/pytest tests/ -v

test-models:
	./venv/bin/pytest tests/test_models.py -v

test-cov:
	./venv/bin/pytest tests/ --cov=src/clynboozle --cov-report=html --cov-report=term-missing

# Application execution
run:
	./venv/bin/python run_clynboozle.py

dev:
	./venv/bin/python run_clynboozle.py --debug

# Build distributable
build:
	./venv/bin/pyinstaller ClynBoozle.spec

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
