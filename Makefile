NOSETESTS = nosetests -m '([Dd]escribe|[Ww]hen|[Ss]hould|[Tt]est)' -e DingusTestCase
PYTHON = python

.PHONY: test unit-test acceptance-test docs

test: unit-test acceptance-test
unit-test:
	$(NOSETESTS) tests/unit/*.py

acceptance-test:
	$(NOSETESTS) tests/acceptance/*.py

docs:
	$(PYTHON) ./setup.py build_sphinx
