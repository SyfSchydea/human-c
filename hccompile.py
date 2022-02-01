#!/usr/bin/env python3

import sys
import string

from hcexceptions import HCTypeError, LexerError, HCParseError
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

		while isinstance(block, hrmi.CompoundBlock):
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
	blocks[0].update_hands(hrmi.HandsState([hrmi.EmptyHands()]))
	blocks_to_check = [blocks[0]]

	while len(blocks_to_check) > 0:
		blk = blocks_to_check.pop()
		if blk.hand_data_propagated:
			continue

		hands = blk.hands_at_start.clone()
		for instr in blk.instructions:
			instr.simulate_hands(hands)

		# Propagate through both possible paths of the conditional jump
		if blk.conditional is not None:
			cond_hands = hands.clone()
			blk.conditional.simulate_hands(cond_hands)
			cond_block = blk.conditional.dest
			cond_block.update_hands(cond_hands)
			blocks_to_check.append(cond_block)

		# Propagate through the unconditional
		if blk.next is not None:
			next_block = blk.next.dest
			next_block.update_hands(hands)
			blocks_to_check.append(next_block)

		blk.hand_data_propagated = True

	# Make optimisations based on calculated hand data
	for blk in blocks:
		hands = blk.hands_at_start.clone()

		i = 0
		while i < len(blk.instructions):
			instr = blk.instructions[i]

			# Remove the instruction if it's redundant
			if instr.hands_redundant(hands):
				del blk.instructions[i]
				continue

			# Expand pseudo instructions if possible
			if isinstance(instr, hrmi.PseudoInstruction):
				expanded = instr.attempt_expand(hands)
				if expanded is not None:
					blk.instructions[i:i+1] = expanded
					continue

			instr.simulate_hands(hands)
			i += 1

def memory_map_contains(memory_map, var_name):
	for memloc in memory_map:
		if memloc.name == var_name:
			return True
	
	return False

# Find each time a variable is referenced, and work backwards
# to each place in the code that that variable could be getting
# its value from, marking that in every instruction inbetween,
# that variable is in use.
def record_variable_use(blocks, memory_map):
	for blk in blocks:
		for i in range(len(blk.instructions)):
			instr = blk.instructions[i]

			if not instr.reads_variable:
				continue

			blk.back_propagate_variable_use(i, instr.loc,
					memory_map_contains(memory_map, instr.loc))

# Optimise code by tracking where variables are actually
# used, and when their value is last set.
# Any instances of a variable's value being set when
# it isn't going to be used again may be removed.
def optimise_variable_needs(blocks, memory_map):
	for blk in blocks:
		i = 0
		while i < len(blk.instructions):
			instr = blk.instructions[i]

			if instr.var_redundant():
				del blk.instructions[i]
			else:
				i += 1

def rename_variable(blocks, old_name, new_name):
	for block in blocks:
		for instr in block.instructions:
			if instr.needs_variable(old_name):
				instr.mark_variable_used(new_name)

			if not isinstance(instr, hrmi.AbstractParameterisedInstruction):
				continue
			if instr.loc == old_name:
				instr.loc = new_name

# Class used to track which variables are used alongside which others.
class VariableUseTracker:
	__slots__ = [
		# Set of sorted tuples of pairs of variables
		# which are used simultaneously.
		"used",

		# Set of each unique variable seen
		"unique_vars",
	]

	def __init__(self):
		self.used = set()
		self.unique_vars = set()

	def _mk_key(self, var_a, var_b):
		return tuple(sorted((var_a, var_b)))

	def mark_used(self, var_a, var_b):
		self.used.add(self._mk_key(var_a, var_b))

	def are_used(self, var_a, var_b):
		if var_a == var_b:
			return True

		return self._mk_key(var_a, var_b) in self.used

	def add_var(self, var):
		self.unique_vars.add(var)

	def get_unique(self):
		return iter(self.unique_vars)

	def __repr__(self):
		return type(self).__name__ + "(" + repr(self.used) + ")"

# Merge variables which are never required to hold
# their values simultaneously.
# Variables which may be merged in this way
# will be renamed to share the same name.
# Relies on variable use data being stored by record_variable_use first.
def merge_disjoint_variables(blocks, namespace, memory_map):
	# Create data structure to track which pairs
	# of variables are used simultaneously
	var_use = VariableUseTracker()

	# Iterate through each instruction in the whole program
	for block in blocks:
		for instr in block.instructions:
			# Check if two or more variables are used during this instruction
			instr_vars = list(instr.variables_used)
			for i in range(len(instr_vars)):
				var1 = instr_vars[i]
				var_use.add_var(var1)
				for j in range(i + 1, len(instr_vars)):
					var2 = instr_vars[j]

					# If so, mark the variables as unmergable in the array
					var_use.mark_used(var1, var2)

	# Look through the array for any mergable pairs of variables
	for var1 in var_use.get_unique():
		if memory_map_contains(memory_map, var1):
			continue

		for var2 in var_use.get_unique():
			if var_use.are_used(var1, var2):
				continue

			# Rename instances of the first to match the second
			rename_variable(blocks, var1, var2)

			# Update the table to reflect the change
			for var3 in namespace.names:
				# Any variables which var1 couldn't merge
				# with, var2 now can't merge with either.
				if var_use.are_used(var1, var3):
					var_use.mark_used(var2, var3)

				# var1 can no longer merge with anything,
				# because it doesn't exist anymore
				var_use.mark_used(var1, var3)

			var_use.mark_used(var1, var2)

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
		for jmp in [*block.jumps_in]:
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
	import argparse

	parser = argparse.ArgumentParser(description="Compile .hc files")
	parser.add_argument("input", default=None)

	args = parser.parse_args()

	tree = None
	try:
		if args.input is None:
			tree = hcparse2.parse_file(sys.stdin)
		else:
			tree = hcparse2.parse_from_path(args.input)
	except (LexerError, HCParseError) as e:
		print(e, file=sys.stderr)
		return 1

	try:
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

		record_variable_use(blocks, initial_memory_map)
		merge_disjoint_variables(blocks, namespace, initial_memory_map)
		optimise_hands_tracking(blocks)
	except HCTypeError as e:
		print(e, file=sys.stderr)
		return 1

	optimise_variable_needs(blocks, initial_memory_map)

	collapse_redundant_blocks(blocks)

	assign_memory(blocks, initial_memory_map)

	mark_implicit_jumps(blocks)

	print("-- HUMAN RESOURCE MACHINE PROGRAM --\n")

	for block in blocks:
		asm = block.to_asm()
		if len(asm) > 0:
			print(asm)

	return 0

if __name__ == "__main__":
	sys.exit(main())
