#!/usr/bin/env python3

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

class Inbox(Instruction):
	def execute(self, office):
		office.hands = next(office.inbox)

class Outbox(Instruction):
	def execute(self, office):
		if office.hands is None:
			raise BossError("Empty value! You\n"
					"can't OUTBOX with\n"
					"empty hands!\n")

		office.outbox(office.hands)
		office.hands = None

# Holds the runtime for the HRM
class Office:
	__slots__ = [
		# List of Instructions
		"program",

		# Iterator from which inbox values are drawn
		"inbox",

		# Function to pass outbox numbers to
		"outbox",

		# Value held in the worker's hands
		# Either an int from -999 to 999, or None if empty
		"hands",

		# Id of next instruction
		"program_counter",
	]

	def __init__(self, program):
		self.program = program

		self.inbox = None
		self.outbox = None

		self.hands = None
		self.program_counter = 0

	def execute(self):
		while self.program_counter < len(self.program):
			instr = self.program[self.program_counter]

			try:
				instr.execute(self)
			except StopIteration:
				break

			self.program_counter += 1

	def __repr__(self):
		return ("Office(" + repr(self.program) + ", "
				+ "hands=" + repr(self.hands) + ", "
				+ "pc=" + repr(self.program_counter) + ")")

BOSS_PASTE_ERROR = ("You can't paste that\n"
		"here! It does not appear\n"
		"to be a valid program!\n"
		"\n")

def load_program(path):
	program = []

	with open(path) as f:
		for line in f:
			line = line.strip()

			if line == "":
				continue

			if line == "-- HUMAN RESOURCE MACHINE PROGRAM --":
				break

			raise BossError(BOSS_PASTE_ERROR
					+ "Program should start with:\n"
					"'-- HUMAN RESOURCE MACHINE PROGRAM --'\n")

		for line in f:
			line = line.strip()

			if line == "":
				continue

			if line == "INBOX":
				program.append(Inbox())
			elif line == "OUTBOX":
				program.append(Outbox())
			else:
				raise BossError(BOSS_PASTE_ERROR
						+ f"Unrecognised instruction: '{line}'\n")

	return Office(program)

# Generate numbers from the given file
def read_input(file_in):
	for line in file_in:
		line = line.strip()

		if line == "":
			continue

		try:
			num = int(line)
		except ValueError as e:
			raise InboxError(e)

		if num < MIN_VALUE or num > MAX_VALUE:
			raise InboxError("number out of bounds: " + repr(num))

		yield num

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
