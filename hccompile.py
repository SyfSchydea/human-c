#!/usr/bin/env python3

import string

import hrminstr as hrmi
import hcparse2

def generate_name(idx):
	name = ""

	while True:
		idx, rem = divmod(idx, 26)

		name += string.ascii_lowercase[rem]

		if idx == 0:
			return name

# Extract a list of all unique blocks from a statement list
def extract_blocks(stmt_list):
	nodes_to_check = [stmt_list.stmts[0].block]
	blocks = []
	names_assigned = 0

	while len(nodes_to_check) > 0:
		block = nodes_to_check.pop()

		if isinstance(block, hrmi.ForeverBlock):
			block = block.first_block

		if block in blocks:
			continue

		blocks.append(block)

		block.set_label(generate_name(names_assigned))
		names_assigned += 1

		if block.next is not None:
			nodes_to_check.append(block.next.dest)

		# TODO: Also check for conditional jumps when they're implemented
	
	return blocks

def mark_implicit_jumps(blocks):
	for i in range(len(blocks) - 1):
		if blocks[i].next is None:
			continue

		if blocks[i].next.dest is blocks[i + 1]:
			blocks[i].next.implicit = True

# Assign named variables to memory locations
def assign_memory(blocks, initial_memory):
	variables = []

	for mem in initial_memory:
		if len(variables) <= mem.loc:
			variables += [None] * (mem.loc - len(variables) + 1)

		variables[mem.loc] = mem.name

	def get_addr(name):
		nonlocal variables

		if name not in variables:
			if None in variables:
				idx = variables.index(None)
				variables[idx] = name
			else:
				variables.append(name)

		return variables.index(name)
	
	for block in blocks:
		for inst in block.instructions:
			if ((isinstance(inst, hrmi.Save) or isinstance(inst, hrmi.Load))
					and type(inst.loc) is str):
				inst.loc = get_addr(inst.loc)

def main():
	import sys
	import argparse

	parser = argparse.ArgumentParser(description="Compile .hc files")
	parser.add_argument("input", default=None)

	args = parser.parse_args()

	tree = None
	if args.input is None:
		tree = hcparse2.parse_file(sys.stdin)
	else:
		tree = hcparse2.parse_from_path(args.input)

	initial_memory_map = tree.get_memory_map()

	tree.create_blocks()
	blocks = extract_blocks(tree)

	assign_memory(blocks, initial_memory_map)

	mark_implicit_jumps(blocks)

	print("-- HUMAN RESOURCE MACHINE PROGRAM --\n")

	for block in blocks:
		asm = block.to_asm()
		if len(asm) > 0:
			print(asm)
	
if __name__ == "__main__":
	main()
