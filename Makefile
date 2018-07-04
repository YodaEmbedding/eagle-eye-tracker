.PHONY: clean doc doc_run test
.PHONY: run_gui run_nxt run_sim

clean:
	find . -name '*.pyc'       -exec rm    --force {} +
	find . -name '__pycache__' -exec rm -r --force {} +

doc:
	make -C doc html

doc_run: doc
	$(BROWSER) doc/_build/html/index.html

run_gui:
	(cd gui && npm start)

run_nxt:
	make -C nxt run
	sleep 1
	python3 eagleeyetracker.py

run_sim:
	python3 simulation.py

test:
	mkdir -p log/
	pytest test/

