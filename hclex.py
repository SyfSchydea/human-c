#!/usr/bin/env python3

from ply import lex, yacc

tokens = (
	"NL",
	"WS",
	"COMMENT",

	"LET",
	"INIT",
	"INPUT",
	"OUTPUT",
	"IF",
	"FOREVER",

	"IDENTIFIER",
	"NUMBER",

	"EQUALS",
	"DBL_EQUALS",
	"NOT_EQUALS",
	"AT",
	"ADD",
)

def t_NL(t):
	r"\n"
	t.lexer.lineno += 1
	return t

t_WS = r"[\t ]+"

t_COMMENT = r"//[^\n]*"

t_LET     = r"let"
t_INIT    = r"init"
t_INPUT   = r"input"
t_OUTPUT  = r"output"
t_IF      = r"if"
t_FOREVER = r"forever"

t_IDENTIFIER = (r"(?!(?:let|forever|input|output|init|if)"
	+ r"[^a-zA-Z_\d])[a-zA-Z_][a-zA-Z_\d]*")

def t_NUMBER(t):
	r"\d+"
	t.value = int(t.value)
	return t

t_EQUALS     = r"="
t_DBL_EQUALS = r"=="
t_NOT_EQUALS = r"!="
t_AT         = r"@"
t_ADD        = r"\+"

def t_error(t):
	raise TypeError(f"Unknown text {t.value}")

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

