.PHONY: test clean

test:
	python3 -m unittest discover test

clean:
	find -name '*.hrm' | xargs rm
