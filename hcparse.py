#!/usr/bin/env python3

from ply import yacc

from hclex import tokens
import hcast as ast

# Phase 1 parsing:
# Creates list of lines

def p_line_list(p):
	"lines : line NL lines"
	p[0] = p[3]
	p[0].insert(0, p[1])

def p_final_line(p):
	"lines : line optnl"
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
	"""optnl : NL
	         |"""
	pass

def p_keyword_let(p):
	"let : LET optws"
	pass

def p_keyword_init(p):
	"init : INIT optws"
	pass

def p_keyword_forever(p):
	"forever : FOREVER optws"
	pass

def p_keyword_output(p):
	"output : OUTPUT optws"
	pass

def p_keyword_input(p):
	"input : INPUT optws"
	pass

def p_operator_at(p):
	"at : AT optws"
	pass

def p_operator_equals(p):
	"equals : EQUALS optws"
	pass

def p_identifier(p):
	"name : IDENTIFIER optws"
	p[0] = p[1]

def p_number(p):
	"number : NUMBER optws"
	p[0] = p[1]

def p_declare_var(p):
	"stmt : let name"
	p[0] = ast.Declare(p[2])

def p_declare_init(p):
	"stmt : init name at number"
	p[0] = ast.InitialValueDeclaration(p[2], p[4])

def p_forever(p):
	"stmt : forever"
	p[0] = ast.Forever()

def p_output(p):
	"stmt : output expr"
	p[0] = ast.Output(p[2])

def p_expr_as_stmt(p):
	"stmt : expr"
	p[0] = ast.ExprLine(p[1])

def p_assign(p):
	"expr : name equals expr"
	p[0] = ast.Assignment(p[1], p[3])

def p_expr_input(p):
	"expr : input"
	p[0] = ast.Input()

def p_var(p):
	"expr : name"
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
