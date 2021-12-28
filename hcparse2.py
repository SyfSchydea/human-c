#!/usr/bin/env python3

from dataclasses import dataclass

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
				raise HCParseError("Non-matching indent")
			if len(line.indent) <= len(stack[-2].indent):
				raise HCParseError("Expected indented block")

			stack[-1].indent = line.indent
		
		# Validate indent, and drop a block of indentation if needed
		while line.indent != stack[-1].indent:
			if (len(line.indent) < len(stack[-1].indent)
					and stack[-1].indent.startswith(line.indent)):
				stack.pop()
			else:
				raise HCParseError("Invalid indent")

		if isinstance(line, ast.Else):
			last_if = stack[-1].statements.get_last_stmt()
			if not isinstance(last_if, ast.If):
				raise HCParseError("Else statement has no matching If statement")

			if last_if.else_block is not None:
				raise HCParseError("If statement has multiple Else statements")

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
