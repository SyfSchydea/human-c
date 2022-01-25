#!/usr/bin/env python3

# === Misc tests ===
#
# These are tests of programs which should be valid, and compile correctly,
# but don't make sense to include as an actual solution test.

from common_test import AbstractTests

class TestMixedIndent(AbstractTests.TestEcho):
	# This test aims to test indentation using both tabs and spaces,
	# But should function as an echo, the same as the year 2 solution.
	source_path = "misc/mixed-indent.hc"

class TestConstEq(AbstractTests.TestEcho):
	# This program should act as an echo, like the solution
	# to year 2, but tests evaluation of equality operators
	# and if statements on constant values.
	source_path = "misc/const-eq.hc"

class TestConstNe(AbstractTests.TestValidProgram):
	source_path = "misc/const-ne.hc"

	# This program always output nothing.
	# This tests use of constant evaluation of !=
	def test_noop(self):
		for inbox in [
				[],
				[1, 2, 3],
				[*"foobar"],
				[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]]:
			with self.subTest(self.input_to_name(inbox)):
				self.run_program(inbox, [])

class TestVarStartsWithKeyword(AbstractTests.TestValidProgram):
	source_path = "misc/var-starts-with-keyword.hc"
	floor_size = 16

	# This file reads six values from the inbox, then outputs the first value
	def test_output(self):
		self.run_tests([
			([1, 2, 3, 4, 5, 6], [1]),
			([13, 11, 7, 5, 3, 2], [13]),
			([*"IFFIER"], ["I"]),
		])

class TestConstAdd(AbstractTests.TestEcho):
	# Tests constant evaluation of the add operator
	source_path = "misc/const-add.hc"

class TestConstMul(AbstractTests.TestEcho):
	# Tests constant evaluation of the multiplication operator
	source_path = "misc/const-mul.hc"
	floor_size = 16

class TestAddMulPrecedence(AbstractTests.TestValidProgram):
	source_path = "misc/add-mul-precedence.hc"
	floor_size = 16

	# Tests operator precedence of add and multiply.
	# Should read pairs of inputs, x and y, and output (3 * x) + y
	def test_output(self):
		self.run_tests([
			([], []),
			([1, 1, 4, 67, 7, 11, 28, 49], [4, 79, 32, 133]),
			([-80, 89, -87, -64, 41, -84], [-151, -325, 39]),
			([68, 0, 0, 59, 0, 0], [204, 59, 0]),
			([12, -36, -8, 24], [0, 0]),
		])

class TestUnaryMinus(AbstractTests.TestValidProgram):
	source_path = "misc/unary-minus.hc"
	floor_size = 16

	# Tests the unary minus operator.
	# Should output the negative of each value
	# in the input then the original value.
	def test_output(self):
		self.run_tests([
			([], []),
			([ 0], [0, 0]),
			([ 2, -3], [-2, 2,   3, -3]),
			([ 1, 21], [-1, 1, -21, 21]),
			([-6, 10, 11], [6, -6, -10, 10, -11, 11]),
			([-4, -3,  9, -8], [4, -4, 3, -3, -9, 9, 8, -8]),
		])
