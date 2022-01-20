#!/usr/bin/env python3

import unittest
import os
import sys
import subprocess
import io

import hrm

class AbstractTests:
	class TestValidProgram(unittest.TestCase):
		# Expected to have source_path and exec_path properties to define
		# the locations of the source files, and compiled files.

		@classmethod
		def setUpClass(cls):
			with open(cls.exec_path, "w") as exe:
				try:
					process = subprocess.run(
							["./hccompile.py", cls.source_path],
							check=True, stderr=subprocess.PIPE,
							stdout=exe)
				except subprocess.CalledProcessError as e:
					print("Error encountered while attempting to compile "
							+ cls.source_path + ":\n"
							+ e.stderr.decode(), file=sys.stderr)
					raise

			cls.office = hrm.load_program(cls.exec_path)
			cls.assertIsNotNone(cls, cls.office)

		def assert_outbox(self, expected, actual):
			for i in range(len(expected)):
				if i >= len(actual):
					self.fail("Not enough stuff in the\n"
							"OUTBOX! Management\n"
							f"expected a total of {len(expected)} items,\n"
							f"not {len(actual)}!")

				if expected[i] != actual[i]:
					self.fail("Bad outbox!\n"
							"Management expected\n"
							+ repr(expected[i])
							+ f", but you outboxed {repr(actual[i])}.")

			# Fallback for missed inconsistencies
			self.assertEqual(expected, actual)

		def run_program(self, inbox, expected_outbox):
			office = self.office.clone()
			outbox = []

			office.inbox = iter(inbox)
			office.outbox = hrm.list_outbox(outbox)
			try:
				office.execute()
			except hrm.BossError as be:
				self.fail(be)

			self.assert_outbox(expected_outbox, outbox)

		def input_to_name(self, inputs):
			if len(inputs) == 0:
				return "<empty>"

			if all(type(x) is str for x in inputs):
				separator = ""
			else:
				separator = ", "

			return separator.join(str(x) for x in inputs)

class TestYear1(AbstractTests.TestValidProgram):
	source_path = "test/source/y1-mail-room.hc"
	exec_path = "test/source/y1.hrm"

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
	source_path = "test/source/y2-busy-mail-room.hc"
	exec_path = "test/source/y2.hrm"

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