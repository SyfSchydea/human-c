class HRMIInternalError(Exception):
	pass

class HRMInstruction:
	# Should be overridden to True for instructions which
	# require a variable to be set to a value
	reads_variable = False

	# Should be overridden to True for instructions which set
	# the value of the variable in their .loc property.
	# Note that this should not be True for variables which modify
	# the value, but still rely on a value already being set.
	writes_variable = False

	__slots__ = [
		# Set of variables used during this instruction.
		# These variables are not necessarily used directly by this
		# instruction, but their values must be held during the execution
		# of this instruction.
		"variables_used",
	]

	def __init__(self):
		self.variables_used = set()

	def to_asm(self):
		raise NotImplementedError("HRMInstruction.to_asm", self)

	# Work out the state of the processor's hands
	# after completing this instruction.
	def simulate_hands(self, hands_before):
		raise NotImplementedError("HRMInstruction.simulate_hands", self)

	# Return true if the instruction is made redundant
	# by the calculated hands state.
	# This is false in the majority of cases
	def hands_redundant(self, hands_before):
		return False

	def mark_variable_used(self, name):
		self.variables_used.add(name)

	# Returns true if the instruction requires the given
	# variable to hold a value during execution
	def needs_variable(self, name):
		return name in self.variables_used

	# Should return true if this instruction is used to set
	# a variable to a value, but that value will not be used,
	# rendering the instruction redundant.
	# False for most instructions.
	def var_redundant(self):
		return False

class Input(HRMInstruction):
	def to_asm(self):
		return "INBOX"

	def simulate_hands(self, hands_before):
		return UnknownHands()

	def __repr__(self):
		return "hrmi.Input()"

class Output(HRMInstruction):
	def to_asm(self):
		return "OUTBOX"

	def simulate_hands(self, hands_before):
		return EmptyHands()

	def __repr__(self):
		return "hrmi.Output()"

# Represents an instruction which takes a parameter of a location in memory
class AbstractParameterisedInstruction(HRMInstruction):
	__slots__ = ["loc"]

	def __init__(self, loc):
		super().__init__()
		self.loc = loc

class Save(AbstractParameterisedInstruction):
	writes_variable = True

	def to_asm(self):
		return "COPYTO " + str(self.loc)

	def simulate_hands(self, hands_before):
		return VariableInHands(self.loc)

	def hands_redundant(self, hands_before):
		return hands_before == VariableInHands(self.loc)

	# This save instruction may be redundant if its
	# variable will not have its value used again.
	def var_redundant(self):
		return self.loc not in self.variables_used

	def __repr__(self):
		return f"hrmi.Save({repr(self.loc)})"

class Load(AbstractParameterisedInstruction):
	reads_variable = True

	def to_asm(self):
		return "COPYFROM " + str(self.loc)

	def simulate_hands(self, hands_before):
		return VariableInHands(self.loc)

	def hands_redundant(self, hands_before):
		return hands_before == VariableInHands(self.loc)

	def __repr__(self):
		return f"hrmi.Load({repr(self.loc)})"

class Add(AbstractParameterisedInstruction):
	reads_variable = True

	def to_asm(self):
		return "ADD " + str(self.loc)

	def simulate_hands(self, hands_before):
		return UnknownHands()

	def __repr__(self):
		return f"hrmi.Add({repr(self.loc)})"

# Instruction which represents an action in the code which could not be
# expanded into correct code at the initial code generation stage.
# Pseudo instructions may be able to be expanded into correct code
# situationally later during static analysis.
class PseudoInstruction(HRMInstruction):
	def to_asm(self):
		raise HRMIInternalError("Pseudo instructions may not be converted directly to assembler")

# Loads a constant value into the hands.
class LoadConstant(PseudoInstruction):
	__slots__ = ["value"]

	def __init__(self, value):
		super().__init__()
		self.value = value

	def simulate_hands(self, hands_before):
		# TODO: Return that the specific value will be in hand
		return UnknownHands()

# Block of instructions
# A block consists of
#  * a series of linear instructions (non jumps),
#  * an optional conditional jump
#  * an unconditional jump
class Block:
	__slots__ = [
		"instructions",
		"conditional",
		"next",
		"label",
		"jumps_in",

		# Properties used in hands tracking
		"hands_at_start",
		"hand_data_propagated",
	]

	def __init__(self):
		self.instructions = []
		self.jumps_in = []
		self.conditional = None
		self.next = None
		self.label = None

		self.hands_at_start = None
		self.hand_data_propagated = False
	
	def needs_label(self):
		for jmp in self.jumps_in:
			if not (isinstance(jmp, Jump) and jmp.implicit):
				return True

		return False

	def to_asm(self):
		lines = []

		if self.label is not None and self.needs_label():
			lines.append(self.label + ":")

		for inst in self.instructions:
			lines.append(inst.to_asm())

		if self.conditional is not None:
			lines.append(self.conditional.to_asm())

		if self.next is not None and not self.next.implicit:
			lines.append(self.next.to_asm())

		return "\n".join(lines)
	
	def add_instruction(self, instr):
		self.instructions.append(instr)
	
	def assign_next(self, next_block):
		if self.next is not None:
			raise HRMIInternalError("Attempted to assign mulitple unconditional jumps to block")

		while isinstance(next_block, CompoundBlock):
			next_block = next_block.first_block

		jmp = Jump(self, next_block)

		self.next = jmp
		next_block.register_jump_in(jmp)

	def assign_jz(self, next_block):
		if self.conditional is not None:
			raise HRMIInternalError("Attempted to assign mulitple conditional jumps to block")

		if isinstance(next_block, CompoundBlock):
			next_block = next_block.first_block

		jz = JumpZero(self, next_block)

		self.conditional = jz
		next_block.register_jump_in(jz)

	def register_jump_in(self, jump):
		self.jumps_in.append(jump)

	def unregister_jump_in(self, jump):
		if jump not in self.jumps_in:
			raise ValueError("Specified jump not present", jump)

		self.jumps_in.remove(jump)

	def set_label(self, label):
		self.label = label

	def update_hands(self, new_hands):
		worst_hands = None

		if self.hands_at_start is None:
			worst_hands = new_hands

		else:
			worst_hands = self.hands_at_start.worst_case(new_hands)

		if worst_hands != self.hands_at_start:
			self.hands_at_start = new_hands
			self.hand_data_propagated = False

	# Mark instructions as using the given variable names
	# Propagation works backwards until it finds an instruction
	# which sets the value of this variable.
	# If propagation reaches the start of the block, it will continue into
	# recursive calls into the jumps_in blocks which lead to this block.
	# Pass instr_idx < 0 to propagate starting at the end of the block.
	def back_propagate_variable_use(self, instr_idx, var_name,
				is_pre_initialised):
		if instr_idx < 0:
			instr_idx = len(self.instructions) - 1

		for i in range(instr_idx, -1, -1):
			instr = self.instructions[i]

			# Stop propagation if we already know that
			# the instruction uses the variable.
			if instr.needs_variable(var_name):
				return

			instr.mark_variable_used(var_name)

			# Stop propagation if this instruction sets the variable.
			if instr.writes_variable and instr.loc == var_name:
				return

		# If propagation reaches all the way back to the starting block,
		# then the variable may be read before it is written to.
		if len(self.jumps_in) == 0 and not is_pre_initialised:
			raise HRMIInternalError(f"Variable '{var_name}' may "
					+ "be referenced before assignment")

		# Propagation has not stopped by the start of this
		# block, so propagate into the next blocks
		for jmp in self.jumps_in:
			jmp.src.back_propagate_variable_use(-1, var_name,
					is_pre_initialised)

	def __repr__(self):
		return ("Block("
			+ repr(self.instructions) + ")")

class AbstractJump(HRMInstruction):
	__slots__ = [
		# References to source and destination blocks
		"src",
		"dest",
	]

	def __init__(self, src, dest):
		self.src = src
		self.dest = dest

	def redirect(self, new_dest):
		self.dest.unregister_jump_in(self)
		self.dest = new_dest
		new_dest.register_jump_in(self)

	def simulate_hands(self, hands_before):
		return hands_before

	def __repr__(self):
		return f"{type(self).__name__}({self.src.label}, {self.dest.label})"

# Represents a jump from the end of one block to another
class Jump(AbstractJump):
	__slots__ = [
		# True if the two blocks are adjacent, meaning no jmp instruction is needed
		"implicit",
	]

	def __init__(self, src, dest):
		super().__init__(src, dest)

		self.implicit = False
	
	def to_asm(self):
		return "JUMP " + self.dest.label

class JumpZero(AbstractJump):
	def to_asm(self):
		return "JUMPZ " + self.dest.label

# Pseudo blocks used to represent the multiple blocks involved
# in control flow statements such as 'forever', or 'if'
class CompoundBlock:
	__slots__ = [
		# Entry point into this block
		"first_block",

		# List of exit points out of this block
		"exit_points",
	]

	def __init__(self, first_block, exit_points=None):
		self.first_block = first_block
		self.exit_points = exit_points
		if self.exit_points is None:
			self.exit_points = []

	def add_instruction(self, instr):
		raise TypeError("Cannot add instruction directly to a Compound Block")

	def assign_next(self, next_block):
		for block in self.exit_points:
			block.assign_next(next_block)

	def register_jump_in(self, jump):
		self.first_block.register_jump_in(jump)

	def __repr__(self):
		return (type(self).__name__ + "("
			+ repr(self.first_block) + ", "
			+ repr(self.exit_points) + ")")

class ForeverBlock(CompoundBlock):
	def __init__(self, block):
		super().__init__(block)

class IfThenElseBlock(CompoundBlock):
	def __init__(self, block, then_exit, else_exit):
		super().__init__(block, [then_exit, else_exit])

# Abstract class for values which the processor's
# hands may take during hands tracking
class AbstractHands:
	def __eq__(self, other):
		if other is None:
			return False

		if not isinstance(other, AbstractHands):
			return NotImplemented

		return type(self) is type(other)

	# Calculate the "worst case" for these two hands states
	# That is, if it has been calculated that the hands could be in either of
	# the two states, what is the strongest claim we can make about the state
	# of the hands at this point?
	def worst_case(self, other):
		if self == other:
			return self
		else:
			return UnknownHands()

# The processor has nothing in their hands
class EmptyHands(AbstractHands):
	pass

# We don't know anything about what the processor has in their hands
class UnknownHands(AbstractHands):
	pass

# The processor is holding a value which matches the value of a variable
class VariableInHands(AbstractHands):
	__slots__ = ["name"]

	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		super_result = super().__eq__(other)
		if super_result != True:
			return super_result

		return other.name == self.name
