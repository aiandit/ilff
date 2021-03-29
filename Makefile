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

check:
	./tests/runtests.sh

check1:
	python3 reindex.py $(TESTF)
	python3 testgetln.py $(TESTF)
	python3 testgetr.py $(TESTF)
	python3 testgetlns.py $(TESTF)
	python3 testgetlns2.py $(TESTF)
	python3 testgetlns3.py $(TESTF)
