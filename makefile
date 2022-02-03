.PHONY: test clean

test:
	@export PYTHONHASHSEED=0
	python3 -m unittest discover test

clean:
	find -name '*.hrm' | xargs rm -f
	rm -f parser.out parsetab.py
