PYTHON ?= python

all: src-pkg wheel-pkg

src-pkg:
	$(PYTHON) setup.py sdist

wheel-pkg:
	$(PYTHON) setup.py bdist_wheel

clean:
	git clean -xfd --exclude dist

allclean:
	git clean -xfd

update: wheel-pkg
	$(PYTHON) -m pip uninstall -y pclio
	$(PYTHON) -m pip install $(lastword $(shell ls -l dist/*.whl))


TESTF ?= test.csv

check: check1 check2

check1:
	./tests/runtests.sh

$(TESTF):
	yes $$(date) | head -n 150000 > $@

check2: $(TESTF)
	python3 ilff/reindex.py $(TESTF)
	python3 testgetln.py $(TESTF)
	python3 testgetr.py $(TESTF)
	python3 testgetlns.py $(TESTF)
	python3 testgetlns2.py $(TESTF)
	python3 testgetlns3.py $(TESTF)
