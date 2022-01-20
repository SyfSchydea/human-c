#!/usr/bin/env python3

from dataclasses import dataclass
import re

import hcast as ast
import hcparse

# Phase 2 parsing:
# Creates proper tree from lines and indents

class HCParseError(Exception):
	pass

def main():
	import sys
	import argparse

	parser = argparse.ArgumentParser(description="Parse .hc files")
	parser.add_argument("input", default=None)

	args = parser.parse_args()

	tree = None
	if args.input is None:
		tree = parse_file(sys.stdin)
	else:
		tree = parse_from_path(args.input)
	
	for stmt in tree.stmts:
		print(stmt)

def parse_file(f):
	program = f.read()

	result = hcparse.parser.parse(program, tracking=True)
	if result is None:
		raise HCParseError("Program failed to produce a tree")

	tree = nest_lines(result)

	return tree

def parse_from_path(path):
	with open(path) as f:
		return parse_file(f)

def readable_indent(indent):
	if len(indent) == 0:
		return "no indent"

	match = re.fullmatch(r"\t*| *", indent)
	if match:
		name = "tab" if indent[0] == "\t" else "space"
		if len(indent) != 1:
			name += "s"

		return str(len(indent)) + " " + name

	return "".join("<tab>" if c == "\t" else "<space>" for c in indent)

@dataclass
class StackEntry:
	statements: list
	indent: str = None

# Nest lines appropriately, given a list of raw lines from phase 1 parsing
def nest_lines(line_list):
	if len(line_list) == 0:
		return ast.StatementList()

	stack = [
		StackEntry(ast.StatementList(), line_list[0].indent),
	]

	if len(line_list) == 0:
		return stack[0].statements

	for line in line_list:
		if stack[-1].indent is None:
			# TODO: get some line numbers in these errors
			# TODO: And print out the indent, (and what's expected?)
			if not line.indent.startswith(stack[-2].indent):
				raise HCParseError("Non-matching indent on line "
						+ str(line.lineno))
			if len(line.indent) <= len(stack[-2].indent):
				raise HCParseError("Expected indented block on line "
						+ str(line.lineno))

			stack[-1].indent = line.indent
		
		# Validate indent, and drop a block of indentation if needed
		while line.indent != stack[-1].indent:
			if (len(line.indent) < len(stack[-1].indent)
					and stack[-1].indent.startswith(line.indent)):
				stack.pop()
			else:
				raise HCParseError("Unexpected indent on line "
						+ str(line.lineno) + "\n"
						+ "Expected " + readable_indent(stack[-1].indent)
						+ " but got " + readable_indent(line.indent))

		if isinstance(line, ast.Else):
			last_if = stack[-1].statements.get_last_stmt()
			if not isinstance(last_if, ast.If):
				raise HCParseError("Else statement on "
						f"line {line.lineno} "
						"has no matching If statement")

			if last_if.else_block is not None:
				raise HCParseError("If statement has a second else "
						"statement on line " + str(line.lineno))

			last_if.else_block = ast.StatementList()
			stack.append(StackEntry(last_if.else_block))
			continue

		# Append self to tree
		stack[-1].statements.append(line)

		# Add self to stack if expected sub-statements
		if isinstance(line, ast.Forever):
			stack.append(StackEntry(line.body))
		elif isinstance(line, ast.If):
			stack.append(StackEntry(line.then_block))
	
	return stack[0].statements

if __name__ == "__main__":
	main()
