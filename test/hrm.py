#!/usr/bin/env python3

import re

# Used to represent an error which the boss in-game would throw
class BossError(Exception):
	pass

# Used to represent an error about the values fed into the inbox
class InboxError(Exception):
	pass

MIN_VALUE = -999
MAX_VALUE =  999

class Instruction:
	def __repr__(self):
		return type(self).__name__ + "()"

	# Checks that the worker's hands are not empty
	# when an instruction expects to use the value
	def empty_hands_check(self, office):
		if office.hands is None:
			raise BossError(
					"Empty value! You\n"
					f"can't {self.name} with\n"
					"empty hands!\n")

class ParameterisedInstruction(Instruction):
	__slots__ = ["param"]

	def __init__(self, param):
		self.param = param

	# Checks that the specified spot on the floor is not empty.
	# Assumes that self.param is a floor address.
	def empty_floor_check(self, office):
		if office.floor[self.param] is None:
			raise BossError(
					f"Empty value! You can't {self.name}\n"
					"with an empty tile on the\n"
					"floor! Try writing something\n"
					"to that tile first")

	def __repr__(self):
		return type(self).__name__ + "(" + repr(self.param) + ")"

class Inbox(Instruction):
	name = mnemonic = "INBOX"

	def execute(self, office):
		office.hands = next(office.inbox)

class Outbox(Instruction):
	name = mnemonic = "OUTBOX"

	def execute(self, office):
		self.empty_hands_check(office)
		office.outbox(office.hands)
		office.hands = None

class CopyFrom(ParameterisedInstruction):
	name = mnemonic = "COPYFROM"

	def execute(self, office):
		self.empty_floor_check(office)

		office.hands = office.floor[self.param]

class CopyTo(ParameterisedInstruction):
	name = mnemonic = "COPYTO"

	def execute(self, office):
		self.empty_hands_check(office)

		office.floor[self.param] = office.hands

class Add(ParameterisedInstruction):
	name = mnemonic = "ADD"

	def execute(self, office):
		self.empty_floor_check(office)
		self.empty_hands_check(office)

		value = office.floor[self.param]
		if type(value) is str or type(office.hands) is str:
			raise BossError(
					"You can't ADD with a\n"
					"letter! What would\n"
					"that even mean?!")

		office.hands += value

class Sub(ParameterisedInstruction):
	name = mnemonic = "SUB"

	def execute(self, office):
		self.empty_floor_check(office)
		self.empty_hands_check(office)

		subtrahend = office.floor[self.param]

		if type(subtrahend) is int and type(office.hands) is int:
			office.hands -= subtrahend

		elif type(subtrahend) is str and type(office.hands) is str:
			office.hands = ord(office.hands.upper()) - ord(subtrahend.upper())

		else:
			raise BossError(
					"You can't SUB with mixed\n"
					"operands! SUB'ing between one\n"
					"letter and one number is invalid.\n"
					"Only nice respectable pairs of two\n"
					"letters or two numbers allowed.")

class AbstractJump(ParameterisedInstruction):
	# Perform the jump, without checking an conditions
	def jump(self, office):
		# Subtract one to account for the pc advancing after execution
		office.program_counter = self.param - 1

class Jump(AbstractJump):
	name = mnemonic = "JUMP"

	def execute(self, office):
		self.jump(office)

class JumpZ(AbstractJump):
	mnemonic = "JUMPZ"
	name = "JUMP IF ZERO"

	def execute(self, office):
		self.empty_hands_check(office)
		if office.hands == 0:
			self.jump(office)

class JumpN(AbstractJump):
	mnemonic = "JUMPN"
	name = "JUMP IF NEGATIVE"

	def execute(self, office):
		self.empty_hands_check(office)
		if office.hands < 0:
			self.jump(office)

# Holds the runtime for the HRM
class Office:
	__slots__ = [
		# List of Instructions
		"program",

		# Dict of labels {"name": position}
		"labels",

		# Iterator from which inbox values are drawn
		"inbox",

		# Function to pass outbox numbers to
		"outbox",

		# Value held in the worker's hands
		# Can be an int from -999 to 999, and single letter string, or None if empty
		"hands",

		# Array of memory values on the floor
		# Can be an int from -999 to 999, and single letter string, or None if empty
		"floor",

		# Id of next instruction
		"program_counter",
	]

	def __init__(self, program, labels, floor=None):
		self.program = program
		self.labels = labels

		self.inbox = None
		self.outbox = None

		self.hands = None
		self.floor = floor if floor is not None else []
		self.program_counter = 0

	def execute(self):
		while self.program_counter < len(self.program):
			instr = self.program[self.program_counter]

			try:
				instr.execute(self)
			except StopIteration:
				break

			self.program_counter += 1

	# Creates a clone of the current office.
	def clone(self):
		copy = Office(self.program, self.labels, [*self.floor])
		copy.inbox = self.inbox
		copy.outbox = self.outbox
		copy.hands = self.hands
		copy.program_counter = self.program_counter
		return copy

	def __repr__(self):
		return ("Office(" + repr(self.program) + ", "
				+ "hands=" + repr(self.hands) + ", "
				+ "pc=" + repr(self.program_counter) + ")")

def validate_floor_addr(param, floor_size=0, lineno=None):
	if not re.match(r"\d+", param):
		raise BossError(BOSS_PASTE_ERROR
			+ f"{type(self).__name__} parameter should be a number ({param})\n")

	addr = int(param)
	if addr >= floor_size:
		raise BossError("You can't paste that here! It is a\n"
				"valid program, but required more\n"
				"slots on the floor than we have\n"
				"available here! We have only 3\n"
				"slots available on this floor!\n"
				"\n"
				f"Attempted to access floor address {addr} on line {lineno}, "
				f"but have only {floor_size} spots on the floor\n")

	return addr

BOSS_PASTE_ERROR = ("You can't paste that\n"
		"here! It does not appear\n"
		"to be a valid program!\n"
		"\n")

def load_program(path, initial_floor=[]):
	program = []
	labels = {}

	floor_size = len(initial_floor)

	with open(path) as f:
		lineno = 0

		for line in f:
			lineno += 1
			line = line.strip()

			if line == "":
				continue

			if line == "-- HUMAN RESOURCE MACHINE PROGRAM --":
				break

			raise BossError(BOSS_PASTE_ERROR
					+ "Program should start with:\n"
					"'-- HUMAN RESOURCE MACHINE PROGRAM --'\n")

		for line in f:
			lineno += 1
			line = line.strip()

			match = re.match(r"([a-zA-Z\d]+)\s*:\s*(.*)$", line)
			if match:
				name = match[1]
				labels[name] = len(program)
				line = match[2]

			if line == "":
				continue

			match = re.match(r"([A-Z]+)(?:\s*([a-zA-Z\d]+))?", line)
			if not match:
				raise BossError(BOSS_PASTE_ERROR
						+ f"Failed to parse line: '{line}'\n")

			instr = match[1]
			param = match[2]

			if instr == "INBOX":
				program.append(Inbox())
			elif instr == "OUTBOX":
				program.append(Outbox())
			elif instr == "COPYFROM":
				program.append(CopyFrom(validate_floor_addr(param, floor_size, lineno)))
			elif instr == "COPYTO":
				program.append(CopyTo(validate_floor_addr(param, floor_size, lineno)))
			elif instr == "ADD":
				program.append(Add(validate_floor_addr(param, floor_size, lineno)))
			elif instr == "SUB":
				program.append(Sub(validate_floor_addr(param, floor_size, lineno)))
			elif instr == "JUMP":
				program.append(Jump(param))
			elif instr == "JUMPZ":
				program.append(JumpZ(param))
			elif instr == "JUMPN":
				program.append(JumpN(param))
			else:
				raise BossError(BOSS_PASTE_ERROR
						+ f"Unrecognised instruction: '{line}'\n")

	# Swap jump parameters from label names to positions in the code
	for instr in program:
		if isinstance(instr, AbstractJump):
			instr.param = labels[instr.param]

	return Office(program, labels, initial_floor)

# Generate numbers from the given file
def read_input(file_in):
	for line in file_in:
		line = line.strip()

		if line == "":
			continue

		if re.fullmatch(r"-?\d+", line):
			val = int(line)

			if val < MIN_VALUE or val > MAX_VALUE:
				raise InboxError("number out of bounds: " + repr(val))
		elif re.fullmatch(r"[a-zA-Z]", line):
			val = line
		else:
			raise InboxError("Invalid inbox value: " + repr(line))

		yield val

# Create an outbox function which writes to a file
def file_outbox(file_out):
	def outbox(num):
		nonlocal file_out

		file_out.write(str(num) + "\n")

	return outbox

# Create an outbox function which appends to a list
def list_outbox(lst):
	def outbox(num):
		nonlocal lst

		lst.append(num)
	
	return outbox

def main():
	import sys
	import argparse

	parser = argparse.ArgumentParser(description="Emulate the Human Resource Machine")
	parser.add_argument("program", help="Input program filepath")

	args = parser.parse_args()

	try:
		office = load_program(args.program)
	except BossError as e:
		sys.stderr.write(str(e))
		sys.exit(1)

	office.inbox = read_input(sys.stdin)
	office.outbox = file_outbox(sys.stdout)

	try:
		office.execute()
	except BossError as e:
		sys.stderr.write(str(e))
		sys.exit(1)
	except InboxError as e:
		sys.stderr.write(str(e))
		sys.exit(2)

if __name__ == "__main__":
	main()
