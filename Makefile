.PHONY: test
test:
	poetry run flake8
	poetry run mypy ./**/*.py --strict
	poetry run pytest

.PHONY: fmt
fmt:
	poetry run black .
