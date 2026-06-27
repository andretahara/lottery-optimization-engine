.PHONY: install test cov lint format quina mega clean

install:
	pip install -e ".[dev]"

test:
	pytest

cov:
	pytest --cov=lottery_optimizer --cov-report=term-missing

lint:
	ruff check lottery_optimizer tests scripts

format:
	ruff format lottery_optimizer tests scripts

quina:
	python scripts/run_quina_example.py

mega:
	python scripts/run_mega_sena_example.py

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
