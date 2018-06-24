.PHONY: clean doc doc_run run test

clean:
	find . -name '*.pyc'       -exec rm    --force {} +
	find . -name '__pycache__' -exec rm -r --force {} +

doc:
	make -C doc html

run:
	python3 simulation.py

test:
	pytest test/

