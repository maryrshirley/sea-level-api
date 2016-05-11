ifndef DJANGO_VERSION_CASE
	DJANGO_VERSION_CASE = ==1.8.12
endif

.PHONY: clean
clean: clean_python_bytecode

.PHONY: clean_python_bytecode
clean_python_bytecode:
	find . -iname '*.pyc' -exec rm {} +
	find . -iname '__pycache__' -type d -exec rm -rf {} +

.PHONY: test
test:
	pip install --upgrade "Django${DJANGO_VERSION_CASE}"
	pip install -r requirements_for_tests.txt
	pip freeze
	./run_tests.sh
