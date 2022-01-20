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

class TestPhase2Parser(AbstractTests.TestError):
	# Test longer indent than expected
	def test_invalid_indent(self):
		self.assertError("test/source/errors/invalid-indent.hc",
				"Unexpected indent on line 5\n"
					"Expected no indent but got 1 tab",
				"An unexpected/invalid indent should produce a useful error")

	def test_forever_no_indent(self):
		self.assertError("test/source/errors/forever-no-indent.hc",
				"Expected indented block on line 5",
				"A forever loop should expect a greater "
					"indent on the following line")
	
	def test_mixed_indent(self):
		self.assertError("test/source/errors/mixed-indent.hc",
				"Unexpected indent on line 9\n"
					"Expected 1 tab but got 4 spaces",
				"Mixed indentation should throw a useful error")

if __name__ == "__main__":
	unittest.main()
