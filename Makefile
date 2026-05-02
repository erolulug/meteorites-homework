.PHONY: run test

PYTHON ?= python3

run:
	bin/meteorites

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

