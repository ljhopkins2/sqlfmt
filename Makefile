.PHONY: check
check:
	pytest
	isort .
	black .
	flake8 .
	mypy .

.PHONY: unit
unit:
	pytest --cov=sqlfmt --cov-report term-missing tests/unit_tests