PYTHON ?= python

all: src-pkg wheel-pkg c-libs

src-pkg wheel-pkg:
	$(PYTHON) -m build .

clean:
	! test -d .git || git clean -xfd --exclude dist

allclean:
	git clean -xfd

uninstall: c-uninstall
	$(PYTHON) -m pip uninstall -y ilff

install: c-install
	$(PYTHON) -m pip install .

install-pkg: wheel-pkg c-install
	$(PYTHON) -m pip install -I $(lastword $(shell ls -lrt dist/*.whl))

update: wheel-pkg c-install
	$(PYTHON) -m pip install -I $(lastword $(shell ls -lrt dist/*.whl))

update: wheel-pkg uninstall install

venv = /var/lib/venvs/test
venv-install: c-install
	bash -c ". $(venv)/bin/activate && $(MAKE) install PREFIX=$(venv)"

venv-uninstall: c-uninstall
	bash -c ". $(venv)/bin/activate && $(MAKE) uninstall PREFIX=$(venv)"

c-libs:
	$(MAKE) -C src

c-install:
	$(MAKE) -C src install

c-uninstall:
	$(MAKE) -C src uninstall


TESTF ?= test.csv
TESTFlnk ?= test-lnk.csv

check: check1 check2 check3
	rm $(TESTF)
	rm $(TESTFlnk)
	rm -rf .ilff-index

check1:
	./tests/runtests.sh

SHELL = bash
export LANG = C

TESTLNS = 150

test-csv: $(TESTF) $(TESTFlnk)

$(TESTF):
	echo -n "" > $@
	for i in {1..$(TESTLNS)}; do S=$$(date | head -c $$(( i % 37 + 3 ))); echo "$$S" >> $@; done

$(TESTFlnk): $(TESTF)
	ln -sfT $(TESTF) $(TESTFlnk)

check2: $(TESTF) $(TESTFlnk)
	python3 testilff.py
	python3 testreindex.py $(TESTF)
	python3 testgetln.py $(TESTF)
	python3 testgetr.py $(TESTF)
	python3 testgetlns.py $(TESTF)
	python3 testgetlns3.py $(TESTF)
	python3 testgetlns3.py $(TESTFlnk)
	python3 testgetlns3.py ilff/ilff.py
	python3 testgetlns4.py $(TESTF)
	python3 testgetlns4.py $(TESTFlnk)
	python3 testgetlns4.py ilff/ilff.py
	python3 testgetlns5.py $(TESTF)
	python3 testgetlnsnoilff.py $(TESTF)
	python3 testgetlnsnoilff.py ilff/ilff.py

check3: $(TESTF) $(TESTFlnk)
	-mkdir /tmp/subdir
	cp -d $(TESTF) $(TESTFlnk) /tmp/subdir
	ln -sfT /tmp/subdir/$(TESTF) /tmp/subdir/link2.csv
	ln -sfT ../subdir/$(TESTF) /tmp/subdir/link3.csv
	python3 testreindex.py /tmp/subdir/$(TESTF)
	python3 testgetln.py /tmp/subdir/$(TESTF)
	python3 testgetr.py /tmp/subdir/$(TESTF)
	python3 testgetlns3.py /tmp/subdir/$(TESTF)
	python3 testgetlns3.py /tmp/subdir/$(TESTFlnk)
	python3 testgetlns3.py /tmp/subdir/link2.csv
	python3 testgetlns3.py /tmp/subdir/link3.csv
	python3 testgetlns4.py /tmp/subdir/$(TESTF)
	python3 testgetlns4.py /tmp/subdir/$(TESTFlnk)
	python3 testgetlns4.py /tmp/subdir/link2.csv
	python3 testgetlns4.py /tmp/subdir/link3.csv
	rm -rf /tmp/subdir
