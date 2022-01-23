#!/usr/bin/env python3

from common_test import AbstractTests

class TestYear1(AbstractTests.TestValidProgram):
	source_path = "solutions/y1-mail-room.hc"
	exec_path = "solutions/y1.hrm"

	def test_solution(self):
		for numbers in [
				[1, 2, 3],
				[0, 0, 0],
				[-999, 0, 999],
				[4, 8, 15],
				[16, 23, 42]]:
			with self.subTest(self.input_to_name(numbers)):
				self.run_program(numbers, numbers)

class TestYear2(AbstractTests.TestValidProgram):
	source_path = "solutions/y2-busy-mail-room.hc"
	exec_path = "solutions/y2.hrm"

	def test_solution(self):
		for numbers in [
			[1, 2, 3],
			[],
			[*"BOOTSEQUENCE"],
			[*"LOADPROGRAM"],
			[*"AUTOEXEC"],
		]:
			with self.subTest(self.input_to_name(numbers)):
				self.run_program(numbers, numbers)

class TestYear3(AbstractTests.TestValidProgram):
	source_path = "solutions/y3-copy-floor.hc"
	exec_path = "solutions/y3.hrm"

	initial_memory = [
		"U", "J", "X",
		"G", "B", "E",
	]

	def test_solution(self):
		self.run_program([], [*"BUG"])

class TestYear4(AbstractTests.TestValidProgram):
	source_path = "solutions/y4-scrambler-handler.hc"
	exec_path = "solutions/y4.hrm"

	floor_size = 3

	def test_solution(self):
		for inbox, expected_outbox in [
			([1, 9, "P", "G", 2, 8], [9, 1, "G", "P", 8, 2]),
			([4, 9, "K", "X", 1, 8], [9, 4, "X", "K", 8, 1]),
			([2, 7, "Q", "Q", 1, 6], [7, 2, "Q", "Q", 6, 1]),
			([4, 5, "I", "T", 2, 6], [5, 4, "T", "I", 6, 2]),
			([1, 7, "B", "V", 1, 7], [7, 1, "V", "B", 7, 1]),
		]:
			with self.subTest(self.input_to_name(inbox)):
				self.run_program(inbox, expected_outbox)

class TestYear6(AbstractTests.TestValidProgram):
	source_path = "solutions/y6-rainy-summer.hc"
	exec_path = "solutions/y6.hrm"

	floor_size = 3

	def test_solution(self):
		for inbox, expected_outbox in [
			([2, 2, 4, 0, -6, 9, 9, -5], [4,   4,  3,  4]),
			([8, 0, 1, 4, -4, 1, 0, -7], [8,   5, -3, -7]),
			([3, 5, 4, 0, -2, 3, 4, -2], [8,   4,  1,  2]),
			([6, 7, 9, 9, -7, 2, 6, -3], [13, 18, -5,  3]),
		]:
			with self.subTest(self.input_to_name(inbox)):
				self.run_program(inbox, expected_outbox)

class TestYear7(AbstractTests.TestValidProgram):
	source_path = "solutions/y7-zero-exterminator.hc"
	exec_path = "solutions/y7.hrm"

	floor_size = 9

	def test_solution(self):
		for inbox, expected_outbox in [
			([8, 0, -1, "F", 0, 0,  3, 0], [8, -1, "F",  3]),
			([5, 0,  2, "E", 0, 0, -2, 0], [5,  2, "E", -2]),
			([8, 0,  0, "E", 0, 0,  4, 0], [8, "E", 4]),
			([5, 0,  5, "E", 0, 0,  0, 0], [5,  5, "E"]),
			([3, 0,  0, "D", 0, 0,  0, 0], [3, "D"]),
		]:
			with self.subTest(self.input_to_name(inbox)):
				self.run_program(inbox, expected_outbox)

	# The game's inboxes for this test are incredibly
	# formulaic, and allow for solutions which do not
	# work for arbitrary inboxes.
	# This function checks that the compiled solution
	# works for more complex inboxes.
	def test_extended(self):
		for inbox, expected_outbox in [
			([], []),
			([0, 0, 0, 0], []),
			([1, 2, 3, 4], [1, 2, 3, 4]),
			([0, 0,  2, "E", 0, 0, -2, 0], [2, "E", -2]),
			([5, 9,  2, "E", 0, 0, -2, 0], [5,  9,  2,  "E", -2]),
			([5, 0,  2,  0,  0, 0, -2, 0], [5,  2, -2]),
			([5, 0,  2, "E", 9, 0, -2, 0], [5,  2, "E",  9, -2]),
			([5, 0,  2, "E", 0, 9, -2, 0], [5,  2, "E",  9, -2]),
			([5, 0,  2, "E", 0, 0, -2, 9], [5,  2, "E", -2,  9]),
		]:
			with self.subTest(self.input_to_name(inbox)):
				self.run_program(inbox, expected_outbox)

if __name__ == "__main__":
	unittest.main()
