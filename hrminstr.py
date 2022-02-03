from hcexceptions import HCTypeError

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

	# Work out the state of the office
	# after completing this instruction.
	def simulate_state(self, state):
		raise NotImplementedError("HRMInstruction.simulate_state", self)

	# Return true if the instruction is made redundant
	# by the calculated office state.
	# This is false in the majority of cases
	def state_redundant(self, state_before):
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

	def simulate_state(self, state):
		state.clear_hand_constraints()

	def __repr__(self):
		return "hrmi.Input()"

class Output(HRMInstruction):
	def to_asm(self):
		return "OUTBOX"

	def simulate_state(self, state):
		state.clear_hand_constraints()
		state.add_constraint(EmptyHands())

	def __repr__(self):
		return "hrmi.Output()"

# Represents an instruction which takes a parameter of a location in memory
class AbstractParameterisedInstruction(HRMInstruction):
	__slots__ = ["loc"]

	def __init__(self, loc):
		super().__init__()
		self.loc = loc

	def to_asm(self):
		return self.mnemonic + " " + str(self.loc)

	def __repr__(self):
		return ("hrmi." + type(self).__name__ + "("
				+ repr(self.loc) + ")")

class Save(AbstractParameterisedInstruction):
	mnemonic = "COPYTO"
	writes_variable = True

	def simulate_state(self, state):
		state.clear_variable_constraints(self.loc)
		state.add_constraint(VariableInHands(self.loc))

		val = state.get_value_in_hands()
		if val is not None:
			state.add_constraint(VariableHasValue(self.loc, val))

	def state_redundant(self, state_before):
		return state_before.has_constraint(VariableInHands(self.loc))

	# This save instruction may be redundant if its
	# variable will not have its value used again.
	def var_redundant(self):
		return self.loc not in self.variables_used

class Load(AbstractParameterisedInstruction):
	mnemonic = "COPYFROM"
	reads_variable = True

	def simulate_state(self, state):
		var_in_hands = VariableInHands(self.loc)

		if not state.has_constraint(var_in_hands):
			state.clear_hand_constraints()

		state.add_constraint(var_in_hands)

		val = state.get_variable_value(self.loc)
		if val is not None:
			state.add_constraint(ValueInHands(val))

	def state_redundant(self, state_before):
		return state_before.has_constraint(VariableInHands(self.loc))

class Add(AbstractParameterisedInstruction):
	mnemonic = "ADD"
	reads_variable = True

	def simulate_state(self, state):
		state.clear_hand_constraints()

class Subtract(AbstractParameterisedInstruction):
	mnemonic = "SUB"
	reads_variable = True

	def simulate_state(self, state):
		state.clear_hand_constraints()

class BumpUp(AbstractParameterisedInstruction):
	mnemonic = "BUMPUP"
	reads_variable = True

	def simulate_state(self, state):
		state.clear_hand_constraints()
		state.clear_variable_constraints(self.loc)
		state.add_constraint(VariableInHands(self.loc))

class BumpDown(AbstractParameterisedInstruction):
	mnemonic = "BUMPDN"
	reads_variable = True

	def simulate_state(self, state):
		state.clear_hand_constraints()
		state.clear_variable_constraints(self.loc)
		state.add_constraint(VariableInHands(self.loc))

# Instruction which represents an action in the code which could not be
# expanded into correct code at the initial code generation stage.
# Pseudo instructions may be able to be expanded into correct code
# situationally later during static analysis.
class PseudoInstruction(HRMInstruction):
	def to_asm(self):
		raise HRMIInternalError("Pseudo instructions may not be "
				+ "converted directly to assembler", self)

	def attempt_expand(self, hands):
		raise NotImplementedError("PseudoInstruction.attempt_expand", self)

# Loads a constant value into the hands.
class LoadConstant(PseudoInstruction):
	__slots__ = ["value"]

	def __init__(self, value):
		super().__init__()
		self.value = value

	def simulate_state(self, state):
		state.clear_hand_constraints()
		state.add_constraint(ValueInHands(self.value))

	def state_redundant(self, state_before):
		return state_before.has_constraint(ValueInHands(self.value))

	def attempt_expand(self, state):
		hand_val = state.get_value_in_hands()
		if hand_val == self.value:
			return []

		var_name = state.find_variable_with_value(self.value)
		if var_name is not None:
			return [Load(var_name)]

		if self.value == 0:
			var_in_hands = state.get_variable_in_hands()
			if var_in_hands is not None:
				return [Subtract(var_in_hands)]

		return None

	def __repr__(self):
		return type(self).__name__ + "(" + repr(self.value) + ")"

# Finds the difference between two variables.
# May optionally be negated in order to produce more efficient code.
class Difference(PseudoInstruction):
	__slots__ = [
		# Names of variables to compare
		"left",
		"right",
	]

	def __init__(self, left, right):
		super().__init__()
		self.left  = left
		self.right = right
	
	def simulate_state(self, state):
		state.clear_hand_constraints()

	def attempt_expand(self, hands):
		if hands.has_constraint(VariableInHands(self.left)):
			return [Subtract(self.right)]
		elif hands.has_constraint(VariableInHands(self.right)):
			return [Subtract(self.left)]
		else:
			return [
				Load(self.left),
				Subtract(self.right),
			]

	def __repr__(self):
		return (type(self).__name__ + "("
			+ repr(self.left) + ", "
			+ repr(self.right) + ")")

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

		# Properties used in state tracking
		"state_at_start",
		"state_data_propagated",

		"lineno",
	]

	def __init__(self, lineno=None):
		self.instructions = []
		self.jumps_in = []
		self.conditional = None
		self.next = None
		self.label = None

		self.state_at_start = None
		self.state_data_propagated = False

		self.lineno = lineno

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
			print("Bad assign. New one:", next_block, "Old one:", self.next.dest)
			raise HRMIInternalError("Attempted to assign mulitple unconditional jumps to block")

		jmp = Jump(self, next_block)

		self.next = jmp

	def _assign_conditional(self, jump):
		if self.conditional is not None:
			raise HRMIInternalError("Attempted to assign multiple "
				+ "conditional jumps to block")

		self.conditional = jump

	# Assign a conditional block for a 'jump if zero' instruction
	def assign_jz(self, next_block):
		self._assign_conditional(JumpZero(self, next_block))

	# Assign a conditional block for a 'jump if negative' instruction
	def assign_jn(self, next_block):
		self._assign_conditional(JumpNegative(self, next_block))

	# Remove the conditional jump from the block
	def unlink_conditional(self):
		jmp = self.conditional
		jmp.unlink_dest()
		self.conditional = None
		return jmp

	def register_jump_in(self, jump):
		self.jumps_in.append(jump)

	def unregister_jump_in(self, jump):
		if jump not in self.jumps_in:
			raise ValueError("Specified jump not present", jump)

		self.jumps_in.remove(jump)

	def set_label(self, label):
		self.label = label

	def update_state(self, new_state):
		worst_state = None

		if self.state_at_start is None:
			worst_state = new_state
		else:
			worst_state = self.state_at_start.worst_case(new_state)

		if worst_state != self.state_at_start:
			self.state_at_start = worst_state
			self.state_data_propagated = False

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
			raise HCTypeError(f"Variable '{var_name}' "
					"referenced before assignment "
					"on line " + str(self.lineno))

		# Propagation has not stopped by the start of this
		# block, so propagate into the next blocks
		for jmp in self.jumps_in:
			jmp.src.back_propagate_variable_use(-1, var_name,
					is_pre_initialised)

	def get_entry_block(self):
		return self

	def get_exit_blocks(self):
		return (self,)

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
		while isinstance(dest, CompoundBlock):
			dest = dest.first_block

		self.src = src
		self.dest = dest

		dest.register_jump_in(self)

	# Remove the jump from its destination
	def unlink_dest(self):
		self.dest.unregister_jump_in(self)
		self.dest = None

	def redirect(self, new_dest):
		self.unlink_dest()
		self.dest = new_dest
		new_dest.register_jump_in(self)

	# Calculate constraints on the hands when this (conditional) jump passes
	def simulate_state_pass(self, state):
		pass

	# Calculate constraints on the hands when this (conditional) jump passes
	def simulate_state_fail(self, state):
		pass

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

	def simulate_state_pass(self, state):
		state.add_constraint(ValueInHands(0))

	def simulate_state_fail(self, state):
		state.add_constraint(ValueNotInHands(0))

	# Check if this jump is guaranteed to fail given the state of the hands
	def redundant_fails(self, hands):
		value = hands.get_value_in_hands()
		return ((value is not None and value != 0)
				or 0 in hands.get_values_not_in_hands())

	# Check if this jump is guaranteed to pass given the state of the hands
	def redundant_passes(self, hands):
		return hands.get_value_in_hands() == 0

class JumpNegative(AbstractJump):
	def to_asm(self):
		return "JUMPN " + self.dest.label

	# Check if this jump is guaranteed to fail given the state of the hands
	def redundant_fails(self, hands):
		value = hands.get_value_in_hands()
		return value is not None and value >= 0

	# Check if this jump is guaranteed to pass given the state of the hands
	def redundant_passes(self, hands):
		value = hands.get_value_in_hands()
		return value is not None and value < 0

# Pseudo blocks used to represent the multiple blocks involved
# in control flow statements such as 'forever', or 'if'
class CompoundBlock:
	__slots__ = [
		# Entry point into this block
		"first_block",

		# Set of exit points out of this block
		"exit_points",
	]

	def __init__(self, first_block, exit_points=None):
		self.first_block = first_block

		if exit_points is None:
			self.exit_points = set()
		else:
			self.exit_points = set(exit_points)

	def add_instruction(self, instr):
		raise TypeError("Cannot add instruction directly to a Compound Block")

	def assign_next(self, next_block):
		for block in self.exit_points:
			block.assign_next(next_block)

	def register_jump_in(self, jump):
		self.first_block.register_jump_in(jump)

	def get_entry_block(self):
		return self.first_block

	def get_exit_blocks(self):
		return tuple(self.exit_points)

	def __repr__(self):
		return (type(self).__name__ + "("
			+ repr(self.first_block) + ", "
			+ repr(self.exit_points) + ")")

class ForeverBlock(CompoundBlock):
	def __init__(self, block):
		super().__init__(block)

# Abstract class for constraints on which values the processor's
# hands may take during execution.
class AbstractStateConstraint:
	# Id used to ensure sub-types have different hashes
	CONSTRAINT_ID = -1

	constrains_hands = False
	constrains_variable = False

	def __eq__(self, other):
		if other is None:
			return False

		if not isinstance(other, AbstractStateConstraint):
			return NotImplemented

		return type(self) is type(other)

	def __hash__(self):
		return hash(self.CONSTRAINT_ID)

# The processor has nothing in their hands
class EmptyHands(AbstractStateConstraint):
	CONSTRAINT_ID = 0

	constrains_hands = True

	def __repr__(self):
		return type(self).__name__ + "()"

# The processor is holding a value which matches the value of a variable
class VariableInHands(AbstractStateConstraint):
	CONSTRAINT_ID = 1

	constrains_hands = True
	constrains_variable = True

	__slots__ = ["name"]

	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		super_result = super().__eq__(other)
		if super_result != True:
			return super_result

		return other.name == self.name

	def __hash__(self):
		return hash((self.CONSTRAINT_ID, self.name))

	def __repr__(self):
		return type(self).__name__ + "(" + repr(self.name) + ")"

class AbstractValueConstraint(AbstractStateConstraint):
	__slots__ = ["value"]

	def __init__(self, value):
		self.value = value

	def __hash__(self):
		return hash((self.CONSTRAINT_ID, self.value))

	def __eq__(self, other):
		super_result = super().__eq__(other)
		if super_result != True:
			return super_result

		return other.value == self.value

	def __repr__(self):
		return type(self).__name__ + "(" + repr(self.value) + ")"

# The processor is holding a specific, constant value
class ValueInHands(AbstractValueConstraint):
	CONSTRAINT_ID = 2
	constrains_hands = True

# The processor cannot be holding a specific value
class ValueNotInHands(AbstractValueConstraint):
	CONSTRAINT_ID = 3
	constrains_hands = True

class VariableHasValue(AbstractStateConstraint):
	CONSTRAINT_ID = 4
	constrains_variable = True

	__slots__ = [
		"name",
		"value",
	]

	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __eq__(self, other):
		super_result = super().__eq__(other)
		if super_result != True:
			return super_result

		return self.value == other.value and self.name == other.name

	def __hash__(self):
		return hash((self.CONSTRAINT_ID, self.name, self.value))

	def __repr__(self):
		return (type(self).__name__ + "("
				+ repr(self.name) + ", "
				+ repr(self.value) + ")")

# Holds a set of zero or more constraints about the processor's
# hands at a particular point in execution
class OfficeState:
	__slots__ = ["constraints"]

	def __init__(self, constraints=[]):
		self.constraints = set(constraints)

	# Return only constraints which are guaranteed to be true in both the self and other cases
	def worst_case(self, other):
		return OfficeState(self.constraints & other.constraints)

	def has_constraint(self, cons):
		return cons in self.constraints

	def add_constraint(self, cons):
		self.constraints.add(cons)

	def clear_constraints(self):
		self.constraints.clear()

	def clear_hand_constraints(self):
		constraints_to_remove = [con for con in self.constraints
				if con.constrains_hands]
		for con in constraints_to_remove:
			self.constraints.remove(con)

	def clear_variable_constraints(self, name):
		constraints_to_remove = [con for con in self.constraints
				if con.constrains_variable and con.name == name]
		for con in constraints_to_remove:
			self.constraints.remove(con)

	# Fetch the name of a variable which is already in the processor's hands, or
	# None if the hands do not match a variable.
	def get_variable_in_hands(self):
		for constraint in self.constraints:
			if isinstance(constraint, VariableInHands):
				return constraint.name

		return None

	# Fetch the value currently guaranteed to be on hand.
	# If a specific value is not known, return None.
	def get_value_in_hands(self):
		for constraint in self.constraints:
			if isinstance(constraint, ValueInHands):
				return constraint.value

		return None

	# Fetch a set of values guaranteed not to be in hands.
	# Note that this does not include values excluded by a ValueInHands
	# constraint, only those excluded by ValueNotInHands constraints.
	def get_values_not_in_hands(self):
		excluded_values = set()

		for constraint in self.constraints:
			if isinstance(constraint, ValueNotInHands):
				excluded_values.add(constraint.value)

		return excluded_values

	# Fetch the value of the given variable or None if not known.
	def get_variable_value(self, name):
		for con in self.constraints:
			if isinstance(con, VariableHasValue) and con.name == name:
				return con.value

		return None

	# Find a variable which is guaranteed to have the given value.
	# Even if multiple variables satisfy the
	# requirement, only one will be returned.
	# If no variables have the value, the function will return None.
	def find_variable_with_value(self, value):
		for con in self.constraints:
			if isinstance(con, VariableHasValue) and con.value == value:
				return con.name

		return None

	def clone(self):
		return OfficeState(self.constraints)

	def __eq__(self, other):
		if not isinstance(other, OfficeState):
			return NotImplemented

		return self.constraints == other.constraints

	def __repr__(self):
		return (type(self).__name__ + "("
				+ repr(self.constraints) + ")")
