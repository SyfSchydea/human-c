class HRMInstruction:
	def to_asm(self):
		raise NotImplementedError("HRMInstruction.to_asm", self)

class Input(HRMInstruction):
	def to_asm(self):
		return "input"

	def __repr__(self):
		return "hrmi.Input()"

class Output(HRMInstruction):
	def to_asm(self):
		return "output"

	def __repr__(self):
		return "hrmi.Output()"

class Save(HRMInstruction):
	__slots__ = ["loc"]

	def __init__(self, loc):
		self.loc = loc

	def to_asm(self):
		return "save " + self.loc

	def __repr__(self):
		return f"hrmi.Save({repr(self.loc)})"

class Load(HRMInstruction):
	__slots__ = ["loc"]

	def __init__(self, loc):
		self.loc = loc

	def to_asm(self):
		return "load " + self.loc

	def __repr__(self):
		return f"hrmi.Load({repr(self.loc)})"

# Block of instructions
# A block consists of
#  * a series of linear instructions (non jumps),
#  * a series of up to two conditional jumps
#  * an unconditional jump
class Block:
	__slots__ = [
		"instructions",
		"next",
		"label",
		"jumps_in",
	]

	def __init__(self):
		self.instructions = []
		self.jumps_in = []
		self.next = None
		self.label = None
	
	def needs_label(self):
		for jmp in self.jumps_in:
			if not jmp.implicit:
				return True

		return False

	def to_asm(self):
		lines = []

		if self.label is not None and self.needs_label():
			lines.append(self.label + ":")

		for inst in self.instructions:
			lines.append(inst.to_asm())

		if self.next is not None and not self.next.implicit:
			lines.append(self.next.to_asm())

		return "\n".join(lines)
	
	def add_instruction(self, instr):
		self.instructions.append(instr)
	
	def assign_next(self, next_block):
		if isinstance(next_block, ForeverBlock):
			next_block = next_block.first_block

		jmp = Jump(self, next_block)

		self.next = jmp
		next_block.jumps_in.append(jmp)
	
	def set_label(self, label):
		self.label = label
	
	def __repr__(self):
		return ("Block("
			+ repr(self.instructions) + ")")

# Represents a jump from the end of one block to another
class Jump:
	__slots__ = [
		# References to source and destination blocks
		"src",
		"dest",

		# True if the two blocks are adjacent, meaning no jmp instruction is needed
		"implicit",
	]

	def __init__(self, src, dest):
		self.src = src
		self.dest = dest

		self.implicit = False
	
	def to_asm(self):
		return "jmp " + self.dest.label
	
	def __repr__(self):
		return f"Jump({self.src.label}, {self.dest.label})"

# Pseudo-Block for forever blocks
# Contains a reference to the first block in the body of the loop
class ForeverBlock:
	__slots__ = [
		"first_block",
	]

	def __init__(self, block):
		self.first_block = block
	
	def add_instruction(self, instr):
		raise TypeError("Cannot add instruction directly to a ForeverBlock")

	def assign_next(self, next_block):
		# No error as this will one day be important once break is implemented
		pass
	
	def __repr__(self):
		return "ForeverBlock(" + repr(self.first_block) + ")"
