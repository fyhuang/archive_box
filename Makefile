.PHONY: tags check_all test_all

PACKAGES=archivebox dtsdb

tags:
	ctags -R $(PACKAGES)

checks:
	mypy $(PACKAGES)
	python3 -m unittest
