.ONESHELL: 

lint: 
	flake8 src/data_services/
	flake8 tests/

format: 
	black src/data_services/
	black tests/

test: 
	@echo "Running a battery of tests..."
	@echo "Unit tests..."
	pytest -s -q --disable-pytest-warnings tests/unit/test_eodhd.py
	pytest -s -q --disable-pytest-warnings tests/unit/test_loader.py
	pytest -s -q --disable-pytest-warnings tests/unit/test_fetch_utils.py
	@echo "Tests carried out successfully!"

all: lint format test

.PHONY:  lint format test
