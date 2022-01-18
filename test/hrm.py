#!/usr/bin/env python3

class BossError(Exception):
	pass

class Instruction:
	def __repr__(self):
		return type(self).__name__ + "()"

class Inbox(Instruction):
	pass

class Outbox(Instruction):
	pass

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

	return program

def main():
	import sys
	import argparse

	parser = argparse.ArgumentParser(description="Emulate the Human Resource Machine")
	parser.add_argument("program", help="Input program filepath")

	args = parser.parse_args()

	try:
		program = load_program(args.program)
	except BossError as e:
		sys.stderr.write(str(e))
		sys.exit(1)

	print(program)

if __name__ == "__main__":
	main()
