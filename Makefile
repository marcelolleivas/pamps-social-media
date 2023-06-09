.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr reports/
	rm -fr .pytest_cache/
	rm -fr coverage.xml

.clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean: .clean-build .clean-pyc .clean-test ## remove all build, test, coverage and Python artifacts

.unit-test:
	./test.sh

tests-with-coverage:
	$(ENV_PREFIX)coverage run -m pytest -v -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage report --fail-under=90 --show-missing --omit="setup.py,pamps/cli.py,tests/*.py"

.isort-fix:
	isort --multi-line=3 --line-length=88 --trailing-comma pamps tests setup.py

.black-fix:
	black pamps tests setup.py

code-convention: .black-fix .isort-fix

code-convention-check:
	flake8 pamps tests --count --exit-zero --max-complexity=10 --max-line-length=127 --select=E9,Fb3,F7,F82 --show-source --statistics
	isort --check --diff --multi-line=3 --line-length=88 --trailing-comma pamps tests setup.py
	black --check --diff pamps tests setup.py
