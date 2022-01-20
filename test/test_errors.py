#!/usr/bin/env python3

import unittest
import subprocess

class AbstractTests:
	class TestError(unittest.TestCase):
		# Check that the given file throws the specified error.
		# Checks that the expected error is in the stderr output.
		def assertError(self, src_path, expected_error, msg=None):
			process = subprocess.run(["./hccompile.py", src_path],
					capture_output=True)

			self.assertNotEqual(0, process.returncode,
					"Invalid source should not exit with code 0")
			self.assertEqual(expected_error,
					process.stderr.decode().rstrip(), msg)

class TestLexer(AbstractTests.TestError):
	def test_invalid_char(self):
		self.assertError("test/source/errors/lexer-error.hc",
				"Unexpected character at line 4, col 3: '~'",
				"Lexer errors should produce a useful error message")

class TestParser(AbstractTests.TestError):
	def test_empty_output_stmt(self):
		self.assertError("test/source/errors/empty-output-stmt.hc",
				"Syntax error at '\\n' on line 6, col 7",
				"Empty output statement should result in "
						"an informative syntax error")

if __name__ == "__main__":
	unittest.main()
