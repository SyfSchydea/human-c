#!/usr/bin/env python3

from common_test import AbstractTests

class TestYear1(AbstractTests.TestValidProgram):
	source_path = "y1-mail-room.hc"
	exec_path = "y1.hrm"

	def test_simple(self):
		for numbers in [
				[1, 2, 3],
				[0, 0, 0],
				[-999, 0, 999],
				[4, 8, 15],
				[16, 23, 42]]:
			with self.subTest(self.input_to_name(numbers)):
				self.run_program(numbers, numbers)

class TestYear2(AbstractTests.TestValidProgram):
	source_path = "y2-busy-mail-room.hc"
	exec_path = "y2.hrm"

	def test_simple(self):
		for numbers in [
			[1, 2, 3],
			[],
			[*"bootsequence"],
			[*"loadprogram"],
			[*"autoexec"],
		]:
			with self.subTest(self.input_to_name(numbers)):
				self.run_program(numbers, numbers)

if __name__ == "__main__":
	unittest.main()
