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

if __name__ == "__main__":
	unittest.main()
