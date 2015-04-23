.PHONY: clean
clean: clean_python_bytecode

.PHONY: clean_python_bytecode
clean_python_bytecode:
	find . -iname '*.pyc' -exec rm {} +
	find . -iname '__pycache__' -type d -exec rm -rf {} +

.PHONY: test
test:
	pip install -r requirements_for_tests.txt
	./run_tests.sh
