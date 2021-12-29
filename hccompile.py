#!/usr/bin/env python3

import string

from hcast import generate_name
import hrminstr as hrmi
import hcparse2

# Extract a list of all unique blocks from a statement list
def extract_blocks(stmt_list):
	if len(stmt_list.stmts) == 0:
		return []

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

		if block.conditional is not None:
			nodes_to_check.append(block.conditional.dest)
		if block.next is not None:
			nodes_to_check.append(block.next.dest)

	return blocks

# Optimise code by tracking what the state of the
# hands will be at each stage in the code.
def optimise_hands_tracking(blocks):
	# First, ensure all hands_at_start values are accurate
	blocks[0].update_hands(hrmi.EmptyHands())
	blocks_to_check = [blocks[0]]

	while len(blocks_to_check) > 0:
		blk = blocks_to_check.pop()
		if blk.hand_data_propagated:
			continue

		hands = blk.hands_at_start
		for instr in blk.instructions:
			hands = instr.simulate_hands(hands)

		# Propagate through both possible paths of the conditional jump
		if blk.conditional is not None:
			hands = blk.conditional.simulate_hands(hands)
			cond_block = blk.conditional.dest
			cond_block.update_hands(hands)
			blocks_to_check.append(cond_block)

		# Propagate through the unconditional
		if blk.next is not None:
			next_block = blk.next.dest
			next_block.update_hands(hands)
			blocks_to_check.append(next_block)

		blk.hand_data_propagated = True

	# Make optimisations based on calculated hand data
	for blk in blocks:
		hands = blk.hands_at_start

		i = 0
		while i < len(blk.instructions):
			instr = blk.instructions[i]

			if instr.hands_redundant(hands):
				del blk.instructions[i]
			else:
				hands = instr.simulate_hands(hands)
				i += 1

# Optimise code by tracking where variables are actually
# used, and when their value is last set.
# Any instances of a variable's value being set when
# it isn't going to be used again may be removed.
def optimise_variable_needs(blocks):
	# Find each time a variable is referenced, and work backwards
	# to each place in the code that that variable could be getting
	# its value from, marking that in every instruction inbetween,
	# that variable is in use.
	for blk in blocks:
		for i in range(len(blk.instructions)):
			instr = blk.instructions[i]

			if not instr.reads_variable:
				continue

			blk.back_propagate_variable_use(i, instr.loc)

	# Iterate through each instruction in the program again.
	for blk in blocks:
		i = 0
		while i < len(blk.instructions):
			instr = blk.instructions[i]

			if instr.var_redundant():
				del blk.instructions[i]
			else:
				i += 1

# Removes blocks which are simply a trivial redirect to another block
def collapse_redundant_blocks(blocks):
	redundant_blocks = []

	for block in blocks:
		# If block has at least one instruction, it's not redundant
		if len(block.instructions) > 0:
			continue

		# If it has a condition jump, it's not redundant
		if block.conditional is not None:
			continue

		# If it has no unconditional jump, we can't reroute it (and it's
		# probably the end block, which we don't want to get rid of)
		if block.next is None:
			continue

		# But if it is redundant, redirect blocks
		# which jump to it to skip past it
		for jmp in block.jumps_in:
			jmp.redirect(block.next.dest)

		block.next.dest.unregister_jump_in(block.next)

		# And add it to the list of redundant blocks,
		# so we can remove it from the list later
		redundant_blocks.append(block)
	
	for block in redundant_blocks:
		blocks.remove(block)

def mark_implicit_jumps(blocks):
	for i in range(len(blocks) - 1):
		if blocks[i].next is None:
			continue

		if blocks[i].next.dest is blocks[i + 1]:
			blocks[i].next.implicit = True

# Assign named variables to memory locations
def assign_memory(blocks, initial_memory):
	if len(blocks) == 0:
		return

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
			if (isinstance(inst, hrmi.AbstractParameterisedInstruction)
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
	namespace = tree.get_namespace()
	tree.validate_structure(namespace)

	tree.create_blocks()
	end_block = hrmi.Block()
	tree.last_block.assign_next(end_block)

	blocks = extract_blocks(tree)

	# Ensure end block is at the end, if it's still present
	if end_block in blocks:
		blocks.remove(end_block)
		blocks.append(end_block)
	
	optimise_hands_tracking(blocks)
	optimise_variable_needs(blocks)

	collapse_redundant_blocks(blocks)

	assign_memory(blocks, initial_memory_map)

	mark_implicit_jumps(blocks)

	print("-- HUMAN RESOURCE MACHINE PROGRAM --\n")

	for block in blocks:
		asm = block.to_asm()
		if len(asm) > 0:
			print(asm)
	
if __name__ == "__main__":
	main()
