# 2011-09-17

PYLINT_CMD = pylint
GITBRANCH ?= master

# Defaults to check all, but allow to check a specific module by using:
# PYLINT_ENTRYPOINT=pytheialib.FoobarModule make pylint
PYLINT_ENTRYPOINT?=pytheialib

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -type d -name '__pycache__' -exec rm -Rf {} \;

distclean: clean
	rm -Rf dist *.egg-info build
	make -C tests distclean

# list make targets:
list:
	@grep '^[a-zA-Z_.]*:' Makefile

pylint:
	LANG=C $(PYLINT_CMD) --rcfile=tests/pylint.rc -f colorized -ry $(PYLINT_ENTRYPOINT) --exit-zero

tests: pylint FORCE
	LANG=C make -C tests tests

dev:
	pip3 install ruff mypy mypy-baseline nose2 pylint

test:
	nose2

# cover:
# 	rm tests/coverage/ -rf
# 	nose2 --with-coverage --cover-package=pytheia --cover-html --cover-html-dir=tests/coverage

style:
	ruff format . --check

format:
	ruff check --select I --fix
	ruff format .

check: ruff_lint mypy

ruff_lint:
	ruff check .

mypy:
	mypy . --install-types --non-interactive 2>&1 | mypy-baseline filter

mypy-reset-baseline:  # Add new typing errors to mypy. Use sparingly.
	mypy . --install-types --non-interactive 2>&1 | mypy-baseline sync

black:
	find pytheialib -name "*.py" -exec black "{}" \;

MANIFEST.in:
	git ls-tree -r HEAD | awk '{print "include ", $$4}' > MANIFEST.in

FORCE:
.IGNORE:
