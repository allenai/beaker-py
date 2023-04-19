.PHONY : docs
docs :
	rm -rf docs/build/
	sphinx-autobuild -b html --watch beaker/ --watch README.md docs/source/ docs/build/

.PHONY : build
build :
	rm -rf *.egg-info/
	python -m build
