# 2011-08-15

clean:
	find . -type f -name '*.result' -exec rm -f {} \;
	find . -type f -name '*.pyc' -exec rm -f {} \;

distclean: clean
	grep -rl 'XXXXXXXXXXXXX Template not edited ' unittests/|xargs rm -f
	find unittests/ -name '__init__.py' -exec rm -f {} \;
	find unittests/ -type d -exec rmdir --ignore-fail-on-non-empty \{\} \;

tests: FORCE
	python -m unittest discover -v -s unittests

FORCE:
