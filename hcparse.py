#!/usr/bin/env python3

from ply import yacc

from hclex import tokens
import hcast as ast

# Phase 1 parsing:
# Creates list of lines

def p_line_list(p):
	"lines : line optws NL lines"
	p[0] = p[4]
	p[0].insert(0, p[1])

def p_final_line(p):
	"lines : line optws optnl"
	p[0] = [p[1]]

def p_line(p):
	"line : optws stmt"
	p[0] = p[2]
	p[0].indent = p[1]

def p_empty_line(p):
	"lines : optws NL lines"
	p[0] = p[3]

def p_comment_line(p):
	"lines : optws COMMENT NL lines"
	p[0] = p[4]

def p_opt_ws(p):
	"optws : WS"
	p[0] = p[1]

def p_no_ws(p):
	"optws :"
	p[0] = ""

def p_opt_nl(p):
	"optnl : NL"
	p[0] = None

def p_no_nl(p):
	"optnl :"
	p[0] = None

def p_declare_var(p):
	"stmt : LET optws IDENTIFIER"
	p[0] = ast.Declare(p[3])

def p_declare_init(p):
	"stmt : INIT optws IDENTIFIER optws AT optws NUMBER"
	p[0] = ast.InitialValueDeclaration(p[3], p[7])

def p_forever(p):
	"stmt : FOREVER"
	p[0] = ast.Forever()

def p_output(p):
	"stmt : OUTPUT optws expr"
	p[0] = ast.Output(p[3])

def p_expr_as_stmt(p):
	"stmt : expr"
	p[0] = ast.ExprLine(p[1])

def p_assign(p):
	"expr : IDENTIFIER optws EQUALS optws expr"
	p[0] = ast.Assignment(p[1], p[5])

def p_input(p):
	"expr : INPUT"
	p[0] = ast.Input()

def p_var(p):
	"expr : IDENTIFIER"
	p[0] = ast.VariableRef(p[1])

def p_error(p):
	if not p:
		print("Error at eof")
		return

	print("Syntax error on line", p.lineno, p.type, repr(p.value))

def main():
	import sys
	import argparse

	ap = argparse.ArgumentParser(description="Compile .hc files")
	ap.add_argument("input", default=None)

	args = ap.parse_args()

	program = None
	if args.input is None:
		program = sys.stdin.read()
	else:
		with open(args.input) as f:
			program = f.read()

	result = parser.parse(program, tracking=True)
	print(result)

parser = yacc.yacc()

if __name__ == "__main__":
	main()
