#!/usr/bin/env python3

from ply import lex, yacc

tokens = (
	"NL",
	"WS",

	"LET",
	"INPUT",
	"OUTPUT",
	"FOREVER",

	"IDENTIFIER",

	"EQUALS",
)

def t_NL(t):
	r"\n"
	t.lexer.lineno += 1
	return t

t_WS = r"[\t ]+"

t_LET     = r"let"
t_INPUT   = r"input"
t_OUTPUT  = r"output"
t_FOREVER = r"forever"

t_IDENTIFIER = r"(?!(?:let|forever|input|output)[^a-zA-Z_\d])[a-zA-Z_][a-zA-Z_\d]*"

t_EQUALS = r"="

def t_error(t):
	raise TypeError(f"Unknown text {t.value}")

def main():
	PATH = "y4-scrambler-handler.hc"

	for line in open(PATH):
		lex.input(line)
		for token in iter(lex.token, None):
			print(token.type, repr(token.value))

lex.lex()

if __name__ == "__main__":
	main()

