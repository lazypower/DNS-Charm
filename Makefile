#!/usr/bin/make

test: clean
	@echo "Starting tests..."
	@tox -e contrib

lint: clean
	@find $(sources) -type f \( -iname '*.py' ! -iwholename './lib/*' \) -print0 | xargs -r0 flake8

clean:
	@find . -name \*.pyc -delete
	@find . -name '*.bak' -delete
	@rm -f .coverage

