#!/usr/bin/env python3

# === Misc tests ===
#
# These are tests of programs which should be valid, and compile correctly,
# but don't make sense to include as an actual solution test.

from common_test import AbstractTests

class TestMixedIndent(AbstractTests.TestValidProgram):
	source_path = "misc/mixed-indent.hc"
	exec_path = "misc/mixed-indent.hrm"

	# This test aims to test indentation using both tabs and spaces,
	# But should function as an echo, the same as the year 2 solution.
	def test_echo(self):
		for numbers in [
				[1, 2, 3],
				[*"foobar"],
				[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]]:
			with self.subTest(self.input_to_name(numbers)):
				self.run_program(numbers, numbers)

class TestConstEq(AbstractTests.TestValidProgram):
	source_path = "misc/const-eq.hc"
	exec_path = "misc/const-eq.hrm"

	# This program should act as an echo, like the solution
	# to year 2, but tests evaluation of equality operators
	# and if statements on constant values.
	def test_echo(self):
		for numbers in [
				[1, 2, 3],
				[*"foobar"],
				[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]]:
			with self.subTest(self.input_to_name(numbers)):
				self.run_program(numbers, numbers)

class TestConstNe(AbstractTests.TestValidProgram):
	source_path = "misc/const-ne.hc"
	exec_path = "misc/const-ne.hrm"

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
	exec_path = "misc/var-starts-with-keyword.hrm"

	floor_size = 16

	# This file reads six values from the inbox, then outputs the first value
	def test_noop(self):
		for inbox, expected_outbox in [
				([1, 2, 3, 4, 5, 6], [1]),
				([13, 11, 7, 5, 3, 2], [13]),
				([*"IFFIER"], ["I"]),
		]:
			with self.subTest(self.input_to_name(inbox)):
				self.run_program(inbox, expected_outbox)

