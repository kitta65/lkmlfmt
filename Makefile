.PHONY: test
test:
	poetry run isort **/*.py --check-only
	poetry run black . --check
	poetry run flake8
	poetry run mypy ./**/*.py --strict
	poetry run pytest

.PHONY: fmt
fmt:
	poetry run isort **/*.py
	poetry run black .
