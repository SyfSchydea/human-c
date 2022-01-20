#!/usr/bin/env python3

import unittest
import subprocess

class TestLexer(unittest.TestCase):
	def test_invalid_char(self):
		src_path = "test/source/errors/lexer-error.hc"

		process = subprocess.run(["./hccompile.py", src_path],
				capture_output=True)

		self.assertNotEqual(0, process.returncode,
				"Invalid source should not exit with code 0")
		self.assertIn("Unexpected character at line 4, col 3: '~'", process.stderr.decode(),
				"Lexer errors should produce a useful error message")

if __name__ == "__main__":
	unittest.main()
