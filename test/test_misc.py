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

class TestConstLe(AbstractTests.TestMultiply):
	# Tests constant evaluation of the less than or equal to operator
	source_path = "misc/const-le.hc"
	factor = 3

class TestConstGe(AbstractTests.TestMultiply):
	# Tests constant evaluation of the less than or equal to operator
	source_path = "misc/const-ge.hc"
	factor = 3

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

class TestConstOr(AbstractTests.TestMultiply):
	# This file tests static evaluation of the logical or operator.
	# It should output each value in the input multiplied by 10.
	source_path = "misc/const-or.hc"
	factor = 10

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

class TestLogicalXnor(AbstractTests.TestValidProgram):
	source_path = "misc/logical-xnor.hc"
	floor_size = 16

	# This file tests use of the equals operator as logical xnor.
	# The file should read pairs of values from the inbox, then output them both
	# only if either both or neither are non-negative.
	def test_output(self):
		self.run_tests([
			([], []),
			([  1, -11], []),
			([ -2,  11,  -7,  7], []),
			([  3,  -4,   2, 13,  -9, -14], [2, 13, -9, -14]),
			([-12,  11, -11, -1,  14, -14, -8,   7],
			 [          -11, -1,                  ]),
			([ -3,  -9,  13, -3, -13,  10, -4, -21],
			 [ -3,  -9,                    -4, -21]),
			([  7,   0,   0,  5,   1,  17,  1, -12],
			 [  7,   0,   0,  5,   1,  17]),
			([  0,   0,   6,  0,   4,   0,  3,  10],
			 [  0,   0,   6,  0,   4,   0,  3,  10]),
			([ 10,   5,   8, 13,  10,   9,  3,  10],
			 [ 10,   5,   8, 13,  10,   9,  3,  10]),
			([  0,   0,  -7,  0,   0,  -3, -5, -11],
			 [  0,   0,                    -5, -11]),
		])

class TestConstXor(AbstractTests.TestMultiply):
	source_path = "misc/const-xor.hc"
	factor = 2

class TestConstXnor(AbstractTests.TestMultiply):
	source_path = "misc/const-xnor.hc"
	factor = 2

class TestAddEquals(AbstractTests.TestValidProgram):
	source_path = "misc/add-equals.hc"
	floor_size = 16

	# This program tests the '+=' assignment operator

	# This file should read two values at a time from
	# the inbox, and output their sum.
	def test_output(self):
		self.run_tests([
			([], []),
			([ 1,  18], [19]),
			([-2, -12, 14,   9], [-14, 23]),
			([ 4,  11, -5,  12, 14, 12], [15, 7, 26]),
			([ 3,   5,  1,   4,  6, -8, -7,  5], [ 8,   5, -2, -2]),
			([ 0,   6,  2,   0,  0,  0, -8,  8], [ 6,   2,  0,  0]),
			([-9,   0,  0, -14,  6, -6,  7, -7], [-9, -14,  0,  0]),
		])

class TestSubEquals(AbstractTests.TestValidProgram):
	source_path = "misc/sub-equals.hc"
	floor_size = 16

	# This program tests the '-=' assignment operator

	# This file should read two values at a time from
	# the inbox, and output their difference.
	def test_output(self):
		self.run_tests([
			([], []),
			([ 1,  18], [-17]),
			([-2, -12, 14,   9], [10, 5]),
			([ 4,  11, -5,  12, 14, 12], [-7, -17, 2]),
			([ 3,   5,  1,   4,  6, -8, -7,  5], [-2, -3, 14, -12]),
			([ 0,   6,  2,   0,  0,  0, -8,  8], [-6,  2,  0, -16]),
			([-9,   0,  0, -14,  6, -6,  7, -7], [-9, 14, 12,  14]),
		])

class TestMulEquals(AbstractTests.TestMultiply):
	source_path = "misc/mul-equals.hc"
	factor = 4

class TestWhile(AbstractTests.TestValidProgram):
	source_path = "misc/while.hc"

	initial_memory = [None, 1] + [None] * 14

	# This file should test while loops.

	# The file should read each input and output each
	# number down to 1 for each positive input.
	# Zero and negative inputs will be ignored.
	def test_output(self):
		self.run_tests([
			([], []),
			([  3], [3, 2, 1]),
			([  1,  3], [1, 3, 2, 1]),
			([  4,  0,  6], [4, 3, 2, 1, 6, 5, 4, 3, 2, 1]),
			([-14,  6, -7], [6, 5, 4, 3, 2, 1]),
			([  0, -1, -2,  0], []),
			([ -4,  5,  0, -9, 2], [5, 4, 3, 2, 1, 2, 1]),
		])

class TestIncrement(AbstractTests.TestValidProgram):
	source_path = "misc/increment.hc"
	floor_size = 16

	# This file tests the prefix increment operator.
	# The operator should add one to the value of its
	# operand, then return its new value.

	# The file should read each value from the input,
	# and output its value plus one.
	def test_output(self):
		self.run_tests([
			([], []),
			([ 7], [8]),
			([17, 14], [18, 15]),
			([13, 11,  14], [14, 12, 15]),
			([12,  4,  20,  11], [13, 5, 21, 12]),
			([11,  6,  12,  13,  2], [12, 7,  13,  14,  3]),
			([-1, -6, -11, -19, -9], [0, -5, -10, -18, -8]),
			([ 8,  9,   0,   4, -9], [9, 10,   1,   5, -8]),
		])

class TestNestedSub(AbstractTests.TestValidProgram):
	source_path = "misc/nest-sub.hc"
	floor_size = 16

	# This file tests expansion of nested subtraction operators.
	def test_output(self):
		self.run_tests([
			([], []),
			([1, 20,  3], [-16, -22, 18]),
			([7, -9, 10, 12, 7, 17], [26, 6, -12, 22, -12, 2]),
		])

class TestZeroPlusExpr(AbstractTests.TestEcho):
	# This tests for expansion of the expression (0 + x).
	# An issue with this was identified in issue #22
	source_path = "misc/zero-plus-expr.hc"
