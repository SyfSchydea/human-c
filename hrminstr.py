class HRMIInternalError(Exception):
	pass

class HRMInstruction:
	def to_asm(self):
		raise NotImplementedError("HRMInstruction.to_asm", self)

class Input(HRMInstruction):
	def to_asm(self):
		return "INBOX"

	def __repr__(self):
		return "hrmi.Input()"

class Output(HRMInstruction):
	def to_asm(self):
		return "OUTBOX"

	def __repr__(self):
		return "hrmi.Output()"

class AbstractParameterisedInstruction(HRMInstruction):
	__slots__ = ["loc"]

	def __init__(self, loc):
		self.loc = loc

class Save(AbstractParameterisedInstruction):
	def to_asm(self):
		return "COPYTO " + str(self.loc)

	def __repr__(self):
		return f"hrmi.Save({repr(self.loc)})"

class Load(AbstractParameterisedInstruction):
	def to_asm(self):
		return "COPYFROM " + str(self.loc)

	def __repr__(self):
		return f"hrmi.Load({repr(self.loc)})"

class Add(AbstractParameterisedInstruction):
	def to_asm(self):
		return "ADD " + str(self.loc)

	def __repr__(self):
		return f"hrmi.Add({repr(self.loc)})"

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
	]

	def __init__(self):
		self.instructions = []
		self.jumps_in = []
		self.conditional = None
		self.next = None
		self.label = None
	
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
	
	def __repr__(self):
		return ("Block("
			+ repr(self.instructions) + ")")

class AbstractJump:
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
