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

class TestConstSub(AbstractTests.TestEcho):
	# Tests constant evaluation of the subtraction operator
	source_path = "misc/const-sub.hc"

class TestConstLt(AbstractTests.TestEcho):
	# Tests constant evaluation of the less than operator
	source_path = "misc/const-lt.hc"

class TestConstGt(AbstractTests.TestEcho):
	# Tests constant evaluation of the greater than operator
	source_path = "misc/const-gt.hc"

class TestConstLe(AbstractTests.TestTriple):
	# Tests constant evaluation of the less than or equal to operator
	source_path = "misc/const-le.hc"

class TestConstGe(AbstractTests.TestTriple):
	# Tests constant evaluation of the less than or equal to operator
	source_path = "misc/const-ge.hc"

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

class TestBrackets(AbstractTests.TestValidProgram):
	source_path = "misc/brackets.hc"
	floor_size = 16

	# Tests use of brackets in expressions.
	# Should take 2 values from the input then output double their sum.
	def test_output(self):
		self.run_tests([
			([], []),
			([ 2,  3], [10]),
			([20, -4, -4, 2], [32, -4]),
			([ 0, 18, 6, 10, 7, 12], [ 36, 32, 38]),
			([-9,  0, 9,  0, 0,  0], [-18, 18,  0]),
		])

class TestConstNot(AbstractTests.TestEcho):
	# Tests constant evaluation of logical not
	source_path = "misc/const-not.hc"

class TestLogicalNot(AbstractTests.TestValidProgram):
	source_path = "misc/logical-not.hc"
	floor_size = 16

	# This file tests evaluation of logical not.
	# It should read pairs of values, and output them only if they are not equal
	def test_output(self):
		self.run_tests([
			([], []),
			([10, 14],                        [10, 14]),
			([21, 14,  7,  7],                [21, 14]),
			([ 5,  8, 12,  7,  1, 1],         [ 5,  8, 12,  7]),
			([17, 17,  1, 13, 10, 4, 10, 10], [         1, 13, 10, 4]),
			([13,  3, 10,  5,  9, 3,  5, 13], [13,  3, 10,  5,  9, 3, 5, 13]),
			([19, 19,  3,  3,  1, 1, 10, 10], []),
		])

class TestLogicalAnd(AbstractTests.TestValidProgram):
	source_path = "misc/logical-and.hc"
	floor_size = 16

	# This file tests compilation of logical and.
	# It should read pairs of values from the inbox, and send them to the outbox
	# only if they are both positive.
	def test_output(self):
		self.run_tests([
			([], []),
			([  1, -11], []),
			([ -2,  11,  -7,  7], []),
			([  3,  -4,   2, 13,  -9, -14], [2, 13]),
			([-12,  11, -11, -1,  14, -14, -8,   7], []),
			([ -3,  -9,  13, -3, -13,  10, -4, -21], []),
			([  7,   0,   0,  5,   1,  17,  1, -12], [1, 17]),
			([  0,   0,   6,  0,   4,   0,  3,  10], [3, 10]),
			([ 10,   5,   8, 13,  10,   9,  3,  10],
					[10, 5, 8, 13, 10, 9, 3, 10]),
		])

class TestLogicalAndComplexRight(AbstractTests.TestValidProgram):
	source_path = "misc/logical-and-complex-right.hc"
	floor_size = 16

	# This program aims to test for evaluation of the
	# logical and operator using a more complex right
	# operand which requires additional statements to
	# be injected during compilation.

	# This file should read values from the inbox and
	# output it if and only if it is non-negative and
	# the following two inputs sum to 0. Those inputs
	# shouldn't be consumed if the original input was
	# negative.
	def test_output(self):
		self.run_tests([
			([], []),
			([13, 12, -12], [13]),
			([-11], []),
			([-1, 14, 9, -9], [14]),
			([10, -9, 3, -10, 21, 12, -12], [21]),
			([17, -13, 13, 7, 18, -18, 3, 13, -13], [17, 7, 3]),
			([-13, -4, 7, 5, -5], [7]),
			([1, 1, -6, 6, -16, 16], [6]),
			([4, 3, 7, -7, 7, 10, 5, -5, 5, 20, 11, -11], []),
		])

class TestConstAnd(AbstractTests.TestEcho):
	# This file tests static evaluation of the logical and operator.
	source_path = "misc/const-and.hc"
	floor_size = 16

class TestLogicalOr(AbstractTests.TestValidProgram):
	source_path = "misc/logical-or.hc"
	floor_size = 16

	# This file tests compilation of logical or.
	# It should read pairs of values from the inbox, and send them to the outbox
	# if at least one is positive.
	def test_output(self):
		self.run_tests([
			([], []),
			([  1, -11], [1, -11]),
			([ -2,  11,  -7,  7], [-2, 11, -7, 7]),
			([  3,  -4,   2, 13,  -9, -14], [3, -4, 2, 13]),
			([-12,  11, -11, -1,  14, -14, -8,   7],
			 [-12,  11,           14, -14, -8,   7]),
			([ -3,  -9,  13, -3, -13,  10, -4, -21],
			 [           13, -3, -13,  10]),
			([  7,   0,   0,  5,   1,  17,  1, -12],
			 [  7,   0,   0,  5,   1,  17,  1, -12]),
			([  0,   0,   6,  0,   4,   0,  3,  10],
			 [            6,  0,   4,   0,  3,  10]),
			([ 10,   5,   8, 13,  10,   9,  3,  10],
			 [ 10,   5,   8, 13,  10,   9,  3,  10]),
		])

class TestConstOr(AbstractTests.TestValidProgram):
	source_path = "misc/const-or.hc"
	floor_size = 16

	# This file tests static evaluation of the logical or operator.
	# It should output each value in the input multiplied by 10.
	def test_output(self):
		self.run_tests([
			([], []),
			([ 11], [110]),
			([  7, -4], [70, -40]),
			([ 11,  9, -3], [110, 90, -30]),
			([-13,  7,  1, -1], [-130, 70, 10, -10]),
			([ 16,  4, 18, -6, 5], [160, 40, 180, -60, 50]),
			([ 12,  1, -2, -7, 3, 2], [120, 10, -20, -70, 30, 20]),
			([  0,  0,  0,  0], [0, 0, 0, 0]),
		])

class TestLogicalXor(AbstractTests.TestValidProgram):
	source_path = "misc/logical-xor.hc"
	floor_size = 16

	# This file tests use of the not equals operator as logical xor.
	# The file should read pairs of values from the inbox, then output them both
	# only if exactly one is positive.
	def test_output(self):
		self.run_tests([
			([], []),
			([  1, -11], [1, -11]),
			([ -2,  11,  -7,  7], [-2, 11, -7, 7]),
			([  3,  -4,   2, 13,  -9, -14], [3, -4]),
			([-12,  11, -11, -1,  14, -14, -8,   7],
			 [-12,  11,           14, -14, -8,   7]),
			([ -3,  -9,  13, -3, -13,  10, -4, -21],
			 [           13, -3, -13,  10]),
			([  7,   0,   0,  5,   1,  17,  1, -12],
			 [  7,   0,   0,  5,            1, -12]),
			([  0,   0,   6,  0,   4,   0,  3,  10],
			 [            6,  0,   4,   0]),
			([ 10,   5,   8, 13,  10,   9,  3,  10], []),
		])
