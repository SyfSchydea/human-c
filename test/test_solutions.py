#!/usr/bin/env python3

import unittest
import os
import sys
import subprocess
import io

import hrm

class TestYear1(unittest.TestCase):
	source_path = "test/source/y1-mail-room.hc"
	exec_path = "test/source/y1.hrm"

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

	def test_simple(self):
		for numbers in [
				[1, 2, 3],
				[0, 0, 0],
				[-999, 0, 999],
				[4, 8, 15],
				[16, 23, 42]]:
			with self.subTest():
				office = self.office.clone()
				outbox = []

				office.inbox = iter(numbers)
				office.outbox = hrm.list_outbox(outbox)
				office.execute()

				self.assertEqual(outbox, numbers)

if __name__ == "__main__":
	unittest.main()
