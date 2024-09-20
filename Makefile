PYTHON ?= python

all: src-pkg wheel-pkg

src-pkg:
	$(PYTHON) setup.py sdist

wheel-pkg:
	$(PYTHON) setup.py bdist_wheel

clean:
	! test -d .git || git clean -xfd --exclude dist

allclean:
	git clean -xfd

uninstall: c-uninstall
	$(PYTHON) -m pip uninstall -y ilff

install: wheel-pkg c-install
	$(PYTHON) -m pip install -I $(lastword $(shell ls -lrt dist/*.whl))

update: wheel-pkg c-install
	$(PYTHON) -m pip install -I $(lastword $(shell ls -lrt dist/*.whl))

update: wheel-pkg uninstall install

venv = /var/lib/venvs/test
venv-install: c-install
	bash -c ". $(venv)/bin/activate && $(MAKE) install PREFIX=$(venv)"

venv-uninstall: c-uninstall
	bash -c ". $(venv)/bin/activate && $(MAKE) uninstall PREFIX=$(venv)"

c-install:
	make -C src install

c-uninstall:
	make -C src uninstall


TESTF ?= test.csv

check: check1 check2 check3

check1:
	./tests/runtests.sh

SHELL = bash
export LANG = C

$(TESTF):
	echo -n "" > $@
	for i in {1..15000}; do S=$$(date | head -c $$(( i % 37 + 3 ))); echo "$$S" >> $@; done

check2: $(TESTF)
	python3 testilff.py
	python3 testcilff.py
	python3 testreindex.py $(TESTF)
	python3 testgetln.py $(TESTF)
	python3 testgetr.py $(TESTF)
	python3 testgetlns.py $(TESTF)
	python3 testgetlns2.py $(TESTF)
	python3 testgetlns3.py $(TESTF)
	python3 testgetlns4.py $(TESTF)
	python3 testgetlnsnoilff.py ilff/ilff.py

check3: $(TESTF)
	-mkdir /tmp/subdir
	cp $(TESTF) /tmp/subdir
	python3 testreindex.py /tmp/subdir/$(TESTF)
	python3 testgetln.py /tmp/subdir/$(TESTF)
	python3 testgetr.py /tmp/subdir/$(TESTF)
	rm -rf /tmp/subdir
