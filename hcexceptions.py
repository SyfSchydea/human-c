# Used for various types of errors caused by a mistake in the input source code.
class HCTypeError(Exception):
	pass

# Used for errors when attempting to lex the input source code.
class LexerError(Exception):
	pass

# Used for errors detected during either phase of parsing.
class HCParseError(Exception):
	pass
