#!/usr/bin/make
PYTHON := /usr/bin/env python

sync-charm-helpers: bin/charm_helpers_sync.py
	@mkdir -p bin
	@$(PYTHON) bin/charm_helpers_sync.py -c charm-helpers.yaml

bin/charm_helpers_sync.py:
	@bzr cat lp:charm-helpers/tools/charm_helpers_sync/charm_helpers_sync.py > bin/charm_helpers_sync.py

test:
	@echo "Starting tests..."
	@nosetests tests --with-coverage --cover-package=hooks --ignore-files=charmhelpers

clean:
	@find . -name \*.pyc -delete
	@find . -name '*.bak' -delete
	@rm -f .coverage

setup: 
	@pip install -q -r requirements.txt --upgrade --user

