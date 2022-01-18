#!/usr/bin/env python3

class BossError(Exception):
	pass

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

		office.outbox.write(str(office.hands) + "\n")
		office.hands = None

# Holds the runtime for the HRM
class Office:
	__slots__ = [
		# List of Instructions
		"program",

		# Iterator from which inbox values are drawn
		"inbox",

		# File to which outbox values are written
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
	except InputError as e:
		sys.stderr.write(str(e))
		sys.exit(2)

	office.inbox = read_input(sys.stdin)
	office.outbox = sys.stdout
	office.execute()

if __name__ == "__main__":
	main()
