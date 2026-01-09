.PHONY: help install lint format test clean docker-up docker-down

help:
    @echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make lint          - Run all linters"
	@echo "  make format        - Format code with black and isort"
	@echo "  make test          - Run tests"
	@echo "  make coverage      - Run tests with coverage"
	@echo "  make security      - Run security checks"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-test   - Run tests in Docker"
	@echo "  make docker-lint   - Run linters in Docker"
	@echo "  make clean         - Clean cache files"

install:
	pip install -r requirements-dev.txt

lint:
	@echo "Running flake8..."
	flake8 .
	@echo "Running pylint..."
	pylint users orders reporting
	@echo "Running mypy..."
	mypy users orders reporting
	@echo "✅ All linters passed!"

format:
	@echo "Running black..."
	black .
	@echo "Running isort..."
	isort .
	@echo "✅ Code formatted!"

test:
	python manage.py test

coverage:
	pytest --cov=users --cov=orders --cov-report=html --cov-report=term

security:
	@echo "Running bandit..."
	bandit -r users orders reporting -ll
	@echo "Running safety..."
	safety check
	@echo "✅ Security checks passed!"

docker-up:
	docker compose up -d
	@echo "⏳ Waiting for services..."
	sleep 5
	docker compose exec web python manage.py migrate

docker-down:
	docker compose down

docker-test:
	docker compose exec web python manage.py test

docker-lint:
	docker compose exec web flake8 .
	docker compose exec web pylint users orders reporting

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage
	@echo "✅ Cleaned cache files!"
