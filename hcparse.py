#!/usr/bin/env python3

from ply import yacc

from hcexceptions import HCParseError
from hclex import tokens
import hcast as ast

# Phase 1 parsing:
# Creates list of lines

def p_line_list(p):
	"lines : line NL lines"
	p[1].lineno = p.lineno(1)
	p[0] = p[3]
	p[0].insert(0, p[1])

def p_null_lines(p):
	"lines : optws opt_comment"
	p[0] = []

def p_empty_line(p):
	"lines : optws opt_comment NL lines"
	p[0] = p[4]

def p_opt_comment(p):
	"""opt_comment : COMMENT
	               |"""
	pass

def p_line(p):
	"line : optws stmt"
	p[0] = p[2]
	p[0].indent = p[1]

def p_opt_ws(p):
	"optws : WS"
	p[0] = p[1]

def p_no_ws(p):
	"optws :"
	p[0] = ""

def p_keyword_init(p):
	"init : INIT optws"
	pass

def p_keyword_forever(p):
	"forever : FOREVER optws"
	pass

def p_keyword_if(p):
	"if : IF optws"
	pass

def p_keyword_else(p):
	"else : ELSE optws"
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

def p_operator_add(p):
	"add : ADD optws"
	pass

def p_operator_subtract(p):
	"subtract : SUBTRACT optws"
	pass

def p_operator_multiply(p):
	"multiply : MULTIPLY optws"
	pass

def p_operator_eq(p):
	"cmp_eq : DBL_EQUALS optws"
	pass

def p_operator_ne(p):
	"cmp_ne : NOT_EQUALS optws"
	pass

def p_operator_lt(p):
	"cmp_lt : LESS_THAN optws"
	pass

def p_operator_le(p):
	"cmp_le : LESS_THAN_OR_EQUAL optws"
	pass

def p_operator_gt(p):
	"cmp_gt : GREATER_THAN optws"
	pass

def p_operator_ge(p):
	"cmp_ge : GREATER_THAN_OR_EQUAL optws"
	pass

def p_identifier(p):
	"name : IDENTIFIER optws"
	p[0] = p[1]

def p_number(p):
	"number : NUMBER optws"
	p[0] = p[1]

def p_declare_init(p):
	"stmt : init name at number"
	p[0] = ast.InitialValueDeclaration(p[2], p[4])

def p_forever(p):
	"stmt : forever"
	p[0] = ast.Forever()

def p_if(p):
	"stmt : if expr"
	p[0] = ast.If(p[2])

def p_else(p):
	"stmt : else"
	p[0] = ast.Else()

def p_output(p):
	"stmt : output expr"
	p[0] = ast.Output(p[2])

def p_expr_as_stmt(p):
	"stmt : expr_assign"
	p[0] = ast.ExprLine(p[1])

def p_assign(p):
	"expr_assign : name equals expr_assign"
	p[0] = ast.Assignment(p[1], p[3])

def p_no_assign(p):
	"expr_assign : expr"
	p[0] = p[1]

def p_eq(p):
	"expr : expr cmp_eq expr_ineq"
	p[0] = ast.CompareEq(p[1], p[3])

def p_ne(p):
	"expr : expr cmp_ne expr_ineq"
	p[0] = ast.CompareNe(p[1], p[3])

def p_expr_ineq(p):
	"expr : expr_ineq"
	p[0] = p[1]

def p_le(p):
	"expr_ineq : expr_ineq cmp_le expr_s"
	p[0] = ast.CompareLe(p[1], p[3])

def p_ge(p):
	"expr_ineq : expr_ineq cmp_ge expr_s"
	p[0] = ast.CompareGe(p[1], p[3])

def p_lt(p):
	"expr_ineq : expr_ineq cmp_lt expr_s"
	p[0] = ast.CompareLt(p[1], p[3])

def p_gt(p):
	"expr_ineq : expr_ineq cmp_gt expr_s"
	p[0] = ast.CompareGt(p[1], p[3])

def p_expr_s(p):
	"expr_ineq : expr_s"
	p[0] = p[1]

def p_expr_m(p):
	"expr_s : expr_m"
	p[0] = p[1]

def p_add(p):
	"expr_s : expr_s add expr_m"
	p[0] = ast.Add(p[1], p[3])

def p_sub(p):
	"expr_s : expr_s subtract expr_m"
	p[0] = ast.Subtract(p[1], p[3])

def p_expr_v(p):
	"expr_m : expr_v"
	p[0] = p[1]

def p_mul(p):
	"expr_m : expr_m multiply expr_v"
	p[0] = ast.Multiply(p[1], p[3])

def p_input(p):
	"expr_v : input"
	p[0] = ast.Input()

def p_num(p):
	"expr_v : number"
	p[0] = ast.Number(p[1])

def p_var(p):
	"expr_v : name"
	p[0] = ast.VariableRef(p[1])

precedence = (
	("left",  "DBL_EQUALS", "NOT_EQUALS"),
	("right", "EQUALS"),
	("left",  "ADD", "SUBTRACT"),
	("left",  "MULTIPLY"),
)

def p_error(p):
	if not p:
		raise HCParseError("Syntax error at eof")

	raise HCParseError(f"Syntax error at {repr(p.value)} "
			f"on line {p.lineno}, col {p.colno}")

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
