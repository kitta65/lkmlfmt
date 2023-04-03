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

.PHONY: publish
publish:
	python -c 'import tomllib,os,pathlib;v=tomllib.loads(pathlib.Path("pyproject.toml").read_text())["tool"]["poetry"]["version"];assert v==os.getenv("GITHUB_REF","").replace("refs/tags/","")'
	poetry build
	poetry publish --password ${PYPI_PASSWORD} --username dr666m1
