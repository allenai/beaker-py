.PHONY : docs
docs :
	rm -rf docs/build/
	sphinx-autobuild -b html --watch beaker/ docs/source/ docs/build/
