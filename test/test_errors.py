#!/usr/bin/env python3

import unittest
import subprocess

from common_test import AbstractTests

class TestLexer(AbstractTests.TestError):
	def test_invalid_char(self):
		self.assertError("errors/lexer-error.hc",
				"Unexpected character at line 4, col 3: '~'",
				"Lexer errors should produce a useful error message")

class TestParser(AbstractTests.TestError):
	def test_empty_output_stmt(self):
		self.assertError("errors/empty-output-stmt.hc",
				"Syntax error at '\\n' on line 6, col 7",
				"Empty output statement should result in "
						"an informative syntax error")

class TestPhase2Parser(AbstractTests.TestError):
	# Test longer indent than expected
	def test_invalid_indent(self):
		self.assertError("errors/invalid-indent.hc",
				"Unexpected indent on line 5\n"
					"Expected no indent but got 1 tab",
				"An unexpected/invalid indent should produce a useful error")

	def test_forever_no_indent(self):
		self.assertError("errors/forever-no-indent.hc",
				"Expected indented block on line 5",
				"A forever loop should expect a greater "
					"indent on the following line")
	
	def test_mixed_indent(self):
		self.assertError("errors/mixed-indent.hc",
				"Unexpected indent on line 9\n"
					"Expected 1 tab but got 4 spaces",
				"Mixed indentation should throw a useful error")

class TestInitStmt(AbstractTests.TestError):
	def test_duplicate_varname(self):
		self.assertError("errors/init-dupe-var.hc",
				"Variable 'foo' declared twice on line 5",
				"Declaring a variable with a duplicate name should "
						"produce an informative error message")

	def test_duplicate_address(self):
		self.assertError("errors/init-dupe-addr.hc",
				"Multiple variables declared at floor address 0 on line 5",
				"Declaring a variable with a duplicate floor address should "
						"produce an informative error message")

class TestVariables(AbstractTests.TestError):
	def test_output_invalid_var(self):
		self.assertError("errors/output-invalid-var.hc",
				"Variable 'foo' referenced before assignment on line 4",
				"Attempting to use a variable before it is assigned should "
						"produce a useful error message")

if __name__ == "__main__":
	unittest.main()
