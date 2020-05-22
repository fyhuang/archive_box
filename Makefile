.PHONY: tags check_all test_all

tags:
	ctags -R .

checks:
	mypy dtsdb
	python3 -m unittest
