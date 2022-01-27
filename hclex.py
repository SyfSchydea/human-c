#!/usr/bin/env python3

from ply import lex, yacc

from hcexceptions import LexerError

keywords = {
	"init":    "INIT",
	"input":   "INPUT",
	"output":  "OUTPUT",
	"if":      "IF",
	"else":    "ELSE",
	"forever": "FOREVER",
}

tokens = (
	"NL",
	"WS",
	"COMMENT",

	"IDENTIFIER",
	"NUMBER",

	"EQUALS",
	"DBL_EQUALS",
	"NOT_EQUALS",
	"LESS_THAN",
	"LESS_THAN_OR_EQUAL",
	"GREATER_THAN",
	"GREATER_THAN_OR_EQUAL",
	"AT",
	"ADD",
	"SUBTRACT",
	"MULTIPLY",
	"OPEN_BRACKET",
	"CLOSE_BRACKET",
	"BANG",
	"DBL_AND",
	"DBL_OR",
	"ADD_EQUALS",

	*keywords.values(),
)

def track(tok):
	if not hasattr(tok.lexer, "colno"):
		tok.lexer.colno = 1

	tok.colno = tok.lexer.colno
	tok.lexer.colno += len(tok.value)
	return tok

def t_NL(t):
	r"\n"
	t.colno = t.lexer.colno
	t.lexer.lineno += 1
	t.lexer.colno = 1
	return t

def t_WS(t):
	r"[\t ]+"
	return track(t)

def t_COMMENT(t):
	r"//[^\n]*"
	return track(t)

def t_IDENTIFIER(t):
	r"[a-zA-Z_][a-zA-Z_\d]*"

	# Check for reserved words
	if t.value in keywords:
		t.type = keywords[t.value]

	return track(t)

def t_NUMBER(t):
	r"\d+"
	track(t)
	t.value = int(t.value)
	return t

def t_DBL_EQUALS(t):
	r"=="
	return track(t)

def t_NOT_EQUALS(t):
	r"!="
	return track(t)

def t_EQUALS(t):
	r"="
	return track(t)

def t_BANG(t):
	r"!"
	return track(t)

def t_DBL_AND(t):
	r"&&"
	return track(t)

def t_DBL_OR(t):
	r"\|\|"
	return track(t)

def t_LESS_THAN_OR_EQUAL(t):
	r"<="
	return track(t)

def t_LESS_THAN(t):
	r"<"
	return track(t)

def t_GREATER_THAN_OR_EQUAL(t):
	r">="
	return track(t)

def t_GREATER_THAN(t):
	r">"
	return track(t)

def t_AT(t):
	r"@"
	return track(t)

def t_ADD_EQUALS(t):
	r"\+="
	return track(t)

def t_ADD(t):
	r"\+"
	return track(t)

def t_SUBTRACT(t):
	r"-"
	return track(t)

def t_MULTIPLY(t):
	r"\*"
	return track(t)

def t_OPEN_BRACKET(t):
	r"\("
	return track(t)

def t_CLOSE_BRACKET(t):
	r"\)"
	return track(t)

def t_error(t):
	raise LexerError(f"Unexpected character at "
			f"line {t.lineno}, col {t.lexer.colno}: "
			+ repr(t.value.rstrip('\n')))

def main():
	import sys
	import argparse

	parser = argparse.ArgumentParser(description="Lex .hc files")
	parser.add_argument("input", default=None)

	args = parser.parse_args()

	f = None
	close_f = False
	if args.input is None:
		f = sys.stdin
	else:
		f = open(args.input)
		close_f = True

	for line in f:
		lex.input(line)
		for token in iter(lex.token, None):
			print(token.type, repr(token.value))
	
	if close_f:
		f.close()

lex.lex()

if __name__ == "__main__":
	main()

