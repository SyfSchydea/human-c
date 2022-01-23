#!/usr/bin/env python3

import unittest
import os
import sys
import subprocess
import re

import hrm

TEST_SOURCE_DIR = "test/source"

class AbstractTests:
	# Run test cases for a valid program
	class TestValidProgram(unittest.TestCase):
		# source_path    - Location of source file
		# exec_path      - Location to save compiled file
		# initial_memory - Initial floor state

		@classmethod
		def get_src(cls):
			return os.path.join(TEST_SOURCE_DIR, cls.source_path)

		@classmethod
		def get_exe(cls):
			return os.path.join(TEST_SOURCE_DIR, cls.exec_path)

		@classmethod
		def setUpClass(cls):
			if not hasattr(cls, "exec_path"):
				match = re.fullmatch(r"(.*)\.hc", cls.source_path)
				if not match:
					raise Exception("No exec path specified, "
							"and source path in unexpected format. "
							"Unable to find path to save resulting program to")
				cls.exec_path = match[1] + ".hrm"

			with open(cls.get_exe(), "w") as exe:
				try:
					process = subprocess.run(
							["./hccompile.py", cls.get_src()],
							check=True, stderr=subprocess.PIPE,
							stdout=exe)
				except subprocess.CalledProcessError as e:
					cls.fail(cls,
							"Error encountered while attempting to compile "
							+ cls.get_src() + ":\n"
							+ e.stderr.decode())
					raise

			if hasattr(cls, "initial_memory"):
				initial_memory = cls.initial_memory
			elif hasattr(cls, "floor_size"):
				initial_memory = [None] * cls.floor_size
			else:
				initial_memory = []

			cls.office = hrm.load_program(cls.get_exe(), initial_memory)
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

		# Run a series of test cases on the compiled program
		# test_cases should be an iterable of tuples of (inbox, expected_outbox)
		def run_tests(self, test_cases):
			for inbox, expected_outbox in test_cases:
				with self.subTest(self.input_to_name(inbox)):
					self.run_program(inbox, expected_outbox)

		def input_to_name(self, inputs):
			if len(inputs) == 0:
				return "<empty>"

			if all(type(x) is str for x in inputs):
				separator = ""
			else:
				separator = ", "

			return separator.join(str(x) for x in inputs)

	# Perform tests on a program which should act as an echo.
	# Expects all values in the inbox to be copied to the outbox.
	class TestEcho(TestValidProgram):
		def test_echo(self):
			for inbox in [
				[],
				[1, 2, 3, 4, 5],
				[*"foobar"],
				[2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37, 41, 43],
				[1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233],
				[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3],
			]:
				with self.subTest(self.input_to_name(inbox)):
					self.run_program(inbox, inbox)

	# Run test cases on programs expected to throw an error in the compiler
	class TestError(unittest.TestCase):
		# Check that the given file throws the specified error.
		# Checks that the expected error is in the stderr output.
		def assertError(self, src_path, expected_error, msg=None):
			process = subprocess.run([
						"./hccompile.py",
						os.path.join(TEST_SOURCE_DIR, src_path)],
					capture_output=True)

			self.assertNotEqual(0, process.returncode,
					"Invalid source should not exit with code 0")
			self.assertEqual(expected_error,
					process.stderr.decode().rstrip(), msg)
