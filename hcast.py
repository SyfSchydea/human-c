import string
import math
from dataclasses import dataclass

import hrminstr as hrmi
from hcexceptions import HCTypeError

class HCInternalError(Exception):
	pass

# Generate a unique name according using an index
def generate_name(idx):
	name = ""

	while True:
		idx, rem = divmod(idx, 26)

		name += string.ascii_lowercase[rem]

		if idx == 0:
			return name

# Generate a function which will validate an expression
# Function returns a tuple of:
# (
#	AbstractExpr to replace this expression with. May be the same expression,
#	List of statements to inject before the containing statement in order to prepare for this expression.
# )
def get_validate_func(method_name):
	def validate_func(expr, namespace):
		if not hasattr(expr, method_name):
			raise HCInternalError("Expression cannot be validated", expr)
		
		new_expr, injected_stmts = getattr(expr, method_name)(namespace)

		# Individual validate functions may return new_expr=None to mean, don't replace anything
		if new_expr is None:
			new_expr = expr
		elif not isinstance(new_expr, AbstractExpr):
			raise HCInternalError("Unexpected expression replacement type")

		# Individual validate functions may return a single AbstractLine, None, or an iterable of AbstractLines
		if isinstance(injected_stmts, AbstractLine):
			injected_stmts = [injected_stmts]
		elif injected_stmts is None:
			injected_stmts = []
		elif all(isinstance(s, AbstractLine) for s in injected_stmts):
			injected_stmts = [*injected_stmts]
		else:
			raise HCInternalError("Unexpected injected statements type", injected_stmts)

		return (new_expr, injected_stmts)
	
	return validate_func

validate_expr_branchable = get_validate_func("validate_branchable")
validate_expr            = get_validate_func("validate")

class AbstractLine:
	__slots__ = [
		"block",

		"indent",
		"lineno",
	]

	def __init__(self, indent="", lineno=None):
		self.indent = indent
		self.lineno = lineno

	# Get list of memory values and variable assigned by this statement
	# Defaults to returning an empty tuple, since most statements don't add any
	def get_memory_map(self):
		return ()

	# Create a block of HRM instructions to represent this line
	# Assign to self.block
	# Doesn't need to assign_next yet
	def create_block(self):
		raise NotImplementedError("AbstractLine.createBlock", self)
	
	# Fetch a list of variables used in this line
	def get_namespace(self):
		raise NotImplementedError("AbstractLine.get_namespace", self)

# eg: init Zero @ 10
class InitialValueDeclaration(AbstractLine):
	__slots__ = [
		"name",
		"loc",
	]

	def create_block(self):
		# Empty block
		self.block = hrmi.Block(self.lineno)
	
	def get_memory_map(self):
		return (MemoryLocation(self.name, self.loc),)

	def __init__(self, name, loc, indent=""):
		super().__init__(indent)
		self.name = name
		self.loc = loc

	def get_namespace(self):
		return Namespace(self.name)

	def validate(self, namespace):
		return None

	def __repr__(self):
		return ("InitialValueDeclaration("
			+ repr(self.name) + ", "
			+ repr(self.loc) + ", "
			+ repr(self.indent) + ")")

@dataclass
class MemoryLocation:
	name: str
	loc: int

# Sequence of AbstractLine objects, to be run in order
class StatementList:
	__slots__ = [
		"stmts",

		"first_block",
		"last_block",
	]

	def append(self, stmt):
		self.stmts.append(stmt)

	def create_blocks(self):
		if len(self.stmts) == 0:
			self.first_block = self.last_block = hrmi.Block()
			return

		for stmt in self.stmts:
			stmt.create_block()

		# Assign each to jump to the next one
		for i in range(1, len(self.stmts)):
			self.stmts[i - 1].block.assign_next(self.stmts[i].block)
		
		# Last block is left with no jump specified

		self.first_block = self.stmts[0].block
		self.last_block = self.stmts[-1].block

	# Look up memory locations of variables specified by the program
	# Returns as an iterable of MemoryLocation objects
	def get_memory_map(self):
		memory_by_name = {}
		memory_by_loc = {}

		for stmt in self.stmts:
			new_memory = stmt.get_memory_map()
			for mem in new_memory:
				if mem.name in memory_by_name:
					raise HCTypeError(f"Variable '{mem.name}' declared twice "
							f"on line {stmt.lineno}")
				if mem.loc in memory_by_loc:
					raise HCTypeError(f"Multiple variables declared at floor "
							f"address {mem.loc} on line {stmt.lineno}")

				memory_by_name[mem.name] = mem
				memory_by_loc[mem.loc] = mem

		return memory_by_name.values()
	
	# Some expressions will require processing before they can be converted to instructions
	def validate_structure(self, namespace):
		i = 0
		while i < len(self.stmts):
			stmt = self.stmts[i]
			result = stmt.validate(namespace)

			# If the validation function returns a Statement, replace the current one
			if isinstance(result, AbstractLine):
				self.stmts[i] = result

			# If the validation returns a list of statements, replace the current one with all of them
			elif (isinstance(result, list)
					and all(isinstance(s, AbstractLine) for s in result)):
				self.stmts[i:i+1] = result
				i += len(result) - 1

			# If the validation function returns None, accept the validation with no modifications
			elif result is None:
				pass

			else:
				raise HCInternalError("Unexpected validation function return type", result)

			i += 1
	
	# Fetch a list of variable names used in this program tree
	def get_namespace(self):
		ns = Namespace()

		for stmt in self.stmts:
			stmt_ns = stmt.get_namespace()
			ns.merge(stmt_ns)

		return ns

	def get_last_stmt(self):
		if len(self.stmts) == 0:
			return None

		return self.stmts[-1]

	def get_entry_block(self):
		return self.first_block

	def get_exit_blocks(self):
		return self.last_block.get_exit_blocks()

	def __init__(self, stmts=None):
		self.stmts = stmts
		if self.stmts is None:
			self.stmts = []
	
	def __repr__(self):
		return f"StatementList({repr(self.stmts)})"

# Abstract class for lines/statements which contain an indented body block after
# them.
class StmtWithBody(AbstractLine):
	def get_body(self):
		raise NotImplementedError("StmtWithBody.get_body", self)

# forever loop
class Forever(StmtWithBody):
	__slots__ = ["body"]

	def __init__(self, body=None):
		self.body = body

		if self.body is None:
			self.body = StatementList()

	def get_body(self):
		return self.body

	def create_block(self):
		self.body.create_blocks()

		# Assign the last to jump back to the first
		# TODO: handle empty body properly
		self.body.stmts[-1].block.assign_next(self.body.stmts[0].block)

		self.block = hrmi.ForeverBlock(self.body.stmts[0].block)

	def get_namespace(self):
		return self.body.get_namespace()

	def validate(self, namespace):
		self.body.validate_structure(namespace)
		return None

	def __repr__(self):
		return f"Forever({repr(self.body)})"

class While(StmtWithBody):
	__slots__ = [
		"condition",
		"body",
	]

	def __init__(self, cond, body=None):
		self.condition = cond
		self.body = body if body is not None else StatementList()

	def get_body(self):
		return self.body

	def get_namespace(self):
		ns = self.condition.get_namespace()
		ns.merge(self.body.get_namespace())
		return ns

	def validate(self, namespace):
		self.condition, injected_stmts_cond = validate_expr_branchable(
				self.condition, namespace)

		if len(injected_stmts_cond) > 0:
			self.condition = InlineStatementExpr(
					injected_stmts_cond, self.condition)

		self.body.validate_structure(namespace)

		return None
	
	def create_block(self):
		self.body.create_blocks()
		exit_block = hrmi.Block(self.lineno)

		cond_block = self.condition.create_branch_block(
				self.body, exit_block, self.lineno)

		for blk in self.body.get_exit_blocks():
			blk.assign_next(cond_block.get_entry_block())

		self.block = hrmi.CompoundBlock(cond_block, [exit_block])

	def __repr__(self):
		return (type(self).__name__ + "("
			+ repr(self.condition) + ", "
			+ repr(self.body) +")")

class If(StmtWithBody):
	__slots__ = [
		"condition",
		"then_block",
		"else_block",
	]

	def __init__(self, cond, then_block=None, else_block=None):
		self.condition = cond
		self.then_block = then_block
		self.else_block = else_block

		if self.then_block is None:
			self.then_block = StatementList()

	def get_body(self):
		# This always returns the then_block. This function is used by the phase
		# 2 parser, which handles else statements specially.
		return self.then_block

	def create_block(self):
		# Fill in empty else block
		if self.else_block is None:
			self.else_block = StatementList()

		self.then_block.create_blocks()
		self.else_block.create_blocks()

		self.block = self.condition.create_branch_block(
				self.then_block, self.else_block, self.lineno)

	def get_namespace(self):
		ns = self.condition.get_namespace()
		ns.merge(self.then_block.get_namespace())

		if self.else_block is not None:
			ns.merge(self.else_block.get_namespace())

		return ns

	def validate(self, namespace):
		self.condition, injected_stmts = validate_expr_branchable(self.condition, namespace)

		self.then_block.validate_structure(namespace)
		if self.else_block is not None:
			self.else_block.validate_structure(namespace)

		injected_stmts.append(self)
		return injected_stmts

	def __repr__(self):
		s = "If(" + repr(self.condition)
		s += ", " + repr(self.then_block)

		if self.else_block is not None:
			s += ", " + repr(self.else_block)

		return s + ")"

# Pseudo node used in parsing
class Else(AbstractLine):
	def __repr__(self):
		return "Else()"

class AbstractLineWithExpr(AbstractLine):
	__slots = ["expr"]

	def __init__(self, expr, indent=""):
		super().__init__(indent)
		self.expr = expr

	def validate(self, namespace):
		self.expr, injected_stmts = validate_expr(self.expr, namespace)
		injected_stmts.append(self)
		return injected_stmts

	def get_namespace(self):
		return self.expr.get_namespace()

# output <expr>
class Output(AbstractLineWithExpr):
	__slots__ = ["expr"]

	def create_block(self):
		self.block = hrmi.Block(self.lineno)
		self.expr.add_to_block(self.block)
		self.block.add_instruction(hrmi.Output())

	def __repr__(self):
		return ("Output("
			+ repr(self.expr) + ", "
			+ repr(self.indent) + ")")

class ExprLine(AbstractLineWithExpr):
	def create_block(self):
		self.block = hrmi.Block(self.lineno)
		self.expr.add_to_block(self.block)

	def __repr__(self):
		return ("ExprLine("
			+ repr(self.expr) + ", "
			+ repr(self.indent) + ")")

class AbstractExpr:
	# Add instructions to load this expression into the accumulator (hands),
	# along with any side-effects
	def add_to_block(self, block):
		raise NotImplementedError("AbstractExpr.add_to_block", self)

	def validate(self, namespace):
		raise NotImplementedError("AbstractExpr.validate", self)

	def has_side_effects(self):
		raise NotImplementedError("AbstractExpr.has_side_effects", self)

	def get_namespace(self):
		raise NotImplementedError("AbstractExpr.get_namespace", self)

	# Fetch the return type of this expression
	def get_type(self):
		if hasattr(self, "hctype"):
			return self.hctype

		raise NotImplementedError("AbstractExpr.get_type", self)

# eg. name = expr
class Assignment(AbstractExpr):
	__slots__ = [
		"name",
		"expr",
	]

	def add_to_block(self, block):
		self.expr.add_to_block(block)
		block.add_instruction(hrmi.Save(self.name))

	def __init__(self, name, expr):
		self.name = name
		self.expr = expr

	def validate(self, namespace):
		self.expr, injected_stmts = validate_expr(self.expr, namespace)
		return (None, injected_stmts)

	def get_namespace(self):
		ns = self.expr.get_namespace()
		ns.add_name(self.name)
		return ns

	def __repr__(self):
		return ("Assignment("
			+ repr(self.name) + ", "
			+ repr(self.expr) + ")")

class Primitive(AbstractExpr):
	__slots__ = ["value"]

	def __init__(self, value):
		self.value = value

	@classmethod
	def get_type(cls):
		return cls

	def __repr__(self):
		return (type(self).__name__ + "(" + repr(self.value) + ")")

class Number(Primitive):
	def add_to_block(self, block):
		block.add_instruction(hrmi.LoadConstant(self.value))

	def validate(self, namespace):
		return (None, None)

	def has_side_effects(self):
		return False

	def get_namespace(self):
		return Namespace()

# Boolean value.
# Currently not directly producable by the source code
class Boolean(Primitive):
	def create_branch_block(self, then_block, else_block, lineno=None):
		block = then_block if self.value else else_block
		return hrmi.CompoundBlock(
				block.get_entry_block(), block.get_exit_blocks())

def is_zero(expr):
	return isinstance(expr, Number) and expr.value == 0

class VariableRef(AbstractExpr):
	__slots__ = ["name"]

	hctype = Number

	def add_to_block(self, block):
		block.add_instruction(hrmi.Load(self.name))

	def __init__(self, name):
		self.name = name

	def validate(self, namespace):
		return (None, None)

	def has_side_effects(self):
		return False

	def get_namespace(self):
		return Namespace(self.name)

	def __repr__(self):
		return ("VariableRef("
			+ repr(self.name) + ")")

class Input(AbstractExpr):
	hctype = Number

	def add_to_block(self, block):
		block.add_instruction(hrmi.Input())

	def validate(self, namespace):
		return (None, None)

	def has_side_effects(self):
		return True

	def get_namespace(self):
		return Namespace()

	def __repr__(self):
		return "Input()"

# Any operator with a left and right operand
class AbstractBinaryOperator(AbstractExpr):
	__slots__ = [
		"left",
		"right",
	]

	def __init__(self, left, right):
		self.left = left
		self.right = right

	def has_side_effects(self):
		return self.left.has_side_effects() or self.right.has_side_effects()

	def get_namespace(self):
		ns_l = self.left.get_namespace()
		ns_r = self.right.get_namespace()
		ns_l.merge(ns_r)
		return ns_l

	def __repr__(self):
		return (type(self).__name__ + "("
			+ repr(self.left) + ", "
			+ repr(self.right) + ")")

class AbstractAdditiveOperator(AbstractBinaryOperator):
	hctype = Number

	# True in subclasses if left and right operands may
	# be swapped without affecting the operation.
	commutative = False

	# True in subclasses if the right operand is negated by the operation
	negate_right_operand = False

	# True in subclasses if this variable evaluates to pseudo instructions
	pseudo = False

	def validate(self, namespace):
		injected_stmts = []

		# Recurse on both operands
		self.left, left_injected = validate_expr(self.left, namespace)
		injected_stmts.extend(left_injected)

		self.right, right_injected = validate_expr(self.right, namespace)
		injected_stmts.extend(right_injected)

		# Handle constant values
		if isinstance(self.left, Number) and isinstance(self.right, Number):
			return (self.eval_static(self.left.value, self.right.value),
					injected_stmts)

		if is_zero(self.right):
			return (self.left, injected_stmts)

		if not self.negate_right_operand and is_zero(self.left):
			return (self.left, injected_stmts)

		if not self.pseudo and isinstance(self.right, VariableRef):
			return (None, injected_stmts)

		# If the right hand side is another additive operator,
		# rotate to put the child add/subtract on the left.
		# Relies on associativity on additive operations
		if (not self.pseudo
				and isinstance(self.right, AbstractAdditiveOperator)
				and not self.right.pseudo):
			# a + (b + c) -> (a + b) + c
			# a + (b - c) -> (a + b) - c
			# a - (b + c) -> (a - b) - c
			# a - (b - c) -> (a - b) + c
			a = self.left
			b = self.right.left
			c = self.right.right

			negate_b = self.negate_right_operand
			negate_c = self.negate_right_operand != self.right.negate_right_operand

			l_expr = (Subtract if negate_b else Add)(a,      b)
			expr   = (Subtract if negate_b else Add)(l_expr, c)

			expr, rot_stmts = validate_expr(expr, namespace)
			injected_stmts.extend(rot_stmts)
			return expr, injected_stmts

		# Swap operands if left operand is a variable reference.
		if self.commutative and isinstance(self.left, VariableRef):
			self.left, self.right = self.right, self.left
			return (self, injected_stmts)

		# Must move the right operand out to a new variable.

		# Must take into account side effects, as this operation
		# may change the order of evaluation.
		if self.left.has_side_effects() and self.right.has_side_effects():
			if self.commutative:
				self.left, self.right = self.right, self.left
			else:
				left_name = namespace.get_unique_name()
				left_assign = ExprLine(Assignment(left_name, self.left))
				injected_stmts.append(left_assign)
				self.left = VariableRef(left_name)

		right_name = namespace.get_unique_name()
		right_assign = ExprLine(Assignment(right_name, self.right))
		injected_stmts.append(right_assign)
		self.right = VariableRef(right_name)

		return (None, injected_stmts)

	# Evaluate the value of the expression given statically
	def eval_static(self, left, right):
		raise NotImplementedError("AbstractAdditiveOperator.eval_static",
				self)

class Add(AbstractAdditiveOperator):
	commutative = True

	def add_to_block(self, block):
		self.left.add_to_block(block)

		if isinstance(self.right, VariableRef):
			block.add_instruction(hrmi.Add(self.right.name))
		else:
			raise HCInternalError("Unable to directly add right operand",
					self.right)

	def eval_static(self, left, right):
		return Number(left + right)

class Subtract(AbstractAdditiveOperator):
	negate_right_operand = True

	def add_to_block(self, block):
		self.left.add_to_block(block)

		if isinstance(self.right, VariableRef):
			block.add_instruction(hrmi.Subtract(self.right.name))
		else:
			raise HCInternalError("Unable to directly subtract right operand",
					self.right)

	# Evaluate the value of the expression given statically
	def eval_static(self, left, right):
		return Number(left - right)

# Pseudo operator.
# Like subtraction, but may represent either (x - y) or (y - x) in cases
# where either is correct, but one may be more efficient than the other.
class Difference(AbstractAdditiveOperator):
	commutative = True
	pseudo = True

	def add_to_block(self, block):
		if not isinstance(self.left, VariableRef) or not isinstance(self.right, VariableRef):
			raise HCInternalError("Unable to convert Difference "
				+ "operator with non variable reference operands")

		block.add_instruction(hrmi.Difference(self.left.name, self.right.name))

_primes = [2]

def get_primes():
	for p in _primes:
		yield p

	i = _primes[-1]
	while True:
		i += 1
		is_prime = True

		for p in _primes:
			quot, rem = divmod(i, p)

			if rem == 0:
				is_prime = False
				break

			if quot < p:
				break

		if is_prime:
			_primes.append(i)
			yield i

def prime_factors(n):
	if n == 1:
		return [1]

	factors = []

	primes = get_primes()
	p = next(primes)
	while n != 1:
		quot, rem = divmod(n, p)

		if rem == 0:
			factors.append(p)
			n = quot
		elif quot < p:
			factors.append(n)
			break
		else:
			p = next(primes)

	return factors

# Holds a strategy for multiplying up to a large number.
# Consists of a series of multiplications (factors),
# then a small addition (offset).
class MultiplicationStrategy:
	__slots__ = [
		"factors",
		"offset",

		# Value this strategy will multiply up to
		"value",

		# Estimated number of instructions taken
		# to perform this multiplication.
		"instructions",
	]

	def __init__(self, factors, offset):
		self.factors = sorted(factors, reverse=True)
		self.offset = offset

		self.value = math.prod(factors) + offset

		for i in range(len(self.factors)):
			f = self.factors[i]
			if f > 5 and f < self.value:
				self.factors[i] = find_multiplication_strategy(f)

		self.instructions = self.offset
		for f in self.factors:
			if isinstance(f, MultiplicationStrategy):
				self.instructions += f.instructions
			else:
				self.instructions += f

	def __str__(self):
		return (" * ".join(f"({f})" if isinstance(f, MultiplicationStrategy)
					else str(f) for f in self.factors)
				+ (" + " + str(self.offset) if self.offset != 0 else ""))

# Lookup table for memoising multiplication stategies
_multiplication_stategies = {}

# Find the best strategy for multiplying by addition.
# Returns (a list of prime factors, and number to add at the end)
# Any value in the prime factors could be replaced
# with another tuple of a similar form.
def find_multiplication_strategy(n):
	if n in _multiplication_stategies:
		return _multiplication_stategies[n]

	best_strategy = None

	i = 0
	while best_strategy is None or i < best_strategy.instructions:
		product = n - i
		factors = prime_factors(product)

		strategy = MultiplicationStrategy(factors, i)

		if (best_strategy is None
				or strategy.instructions < best_strategy.instructions):
			best_strategy = strategy

		i += 1

	_multiplication_stategies[n] = best_strategy
	return best_strategy

# Nest repeated addition nodes
def nest_addition(expr, n):
	if n == 0:
		return Number(0)

	if n == 1:
		return expr

	return Add(nest_addition(expr, n - 1), expr)

# Expand a multiplication strategy into its various additions and assignments.
# Returns (the new expression which holds the result of the multiplication,
# and a list of injected statements used in the calculation)
def expand_multiplication_strategy(strategy, expr, namespace):
	if isinstance(strategy, int):
		return (nest_addition(expr, strategy), [])

	injected_stmts = []
	working_product = expr
	for fact in strategy.factors:
		working_product, fact_stmts = expand_multiplication_strategy(
				fact, working_product, namespace)
		injected_stmts.extend(fact_stmts)

		var_name = namespace.get_unique_name()
		injected_stmts.append(ExprLine(Assignment(var_name, working_product)))
		working_product = VariableRef(var_name)

	offset_add = nest_addition(expr, strategy.offset)
	final_add = Add(working_product, offset_add)

	final_add, injected_final = validate_expr(final_add, namespace)
	injected_stmts.extend(injected_final)

	return (final_add, injected_stmts)

# Find an efficient way to multiply an expression by a constant using only addition.
# Returns (a new expression node, and a list of injected statements)
def validate_expr_mul_const(expr, n, namespace):
	injected_stmts = []

	if expr.has_side_effects() and n > 1:
		var_name = namespace.get_unique_name()
		new_assign = ExprLine(Assignment(var_name, expr))
		injected_stmts.append(new_assign)
		expr = VariableRef(var_name)

	strategy = find_multiplication_strategy(n)

	expanded_expr, expanded_stmts = (
			expand_multiplication_strategy(strategy, expr, namespace))
	injected_stmts.extend(expanded_stmts)

	return (expanded_expr, injected_stmts)

class Multiply(AbstractBinaryOperator):
	hctype = Number

	def validate(self, namespace):
		self.left,  injected_stmts       = validate_expr(self.left,  namespace)
		self.right, injected_stmts_right = validate_expr(self.right, namespace)

		injected_stmts.extend(injected_stmts_right)

		left_const  = isinstance(self.left,  Number)
		right_const = isinstance(self.right, Number)

		if left_const and right_const:
			return (Number(self.left.value * self.right.value), None)

		# Ensure any constant term is on the right
		if left_const:
			self.left,  self.right  = self.right,  self.left
			left_const, right_const = right_const, left_const

		if right_const and self.right.value == 0:
			if self.left.has_side_effects():
				injected_stmts.append(ExprLine(self.left))

			return (Number(0), injected_stmts)

		if right_const and self.right.value > 0:
			expr, injected_stmts_mul = validate_expr_mul_const(
					self.left, self.right.value, namespace)
			injected_stmts.extend(injected_stmts_mul)

			return (expr, injected_stmts)

		raise HCTypeError("Unable to multiply", self.left, "with", self.right)

class AbstractEqualityOperator(AbstractBinaryOperator):
	hctype = Boolean

	negate = False

	# Check if the types of the operands of this operation indicate that this is
	# performing XOR rather than equality.
	def is_xor(self):
		return (self.left.get_type() is Boolean and
				self.right.get_type() is Boolean)

	def validate_branchable(self, namespace):
		if self.is_xor():
			return self.validate_branchable_as_xor(namespace)

		self.left,  injected_stmts    = validate_expr(self.left,  namespace)
		self.right, injected_stmts_rt = validate_expr(self.right, namespace)

		injected_stmts.extend(injected_stmts_rt)

		if isinstance(self.left, Number) and isinstance(self.right, Number):
			value = self.left.value == self.right.value
			if self.negate:
				value = not value
			return (Boolean(value), None)
		elif is_zero(self.right):
			return (None, injected_stmts)
		elif is_zero(self.left):
			self.left, self.right = self.right, self.left
			return (None, injected_stmts)
		else:
			# (x == y) -> (x - y == 0)
			diff = None
			left_var  = isinstance(self.left,  VariableRef)
			right_var = isinstance(self.right, VariableRef)
			if left_var and right_var:
				# If both operands are just variables,
				# decide on the order later
				diff = Difference(self.left, self.right)
			elif right_var:
				diff = Subtract(self.left, self.right)
			elif left_var:
				diff = Subtract(self.right, self.left)
			else:
				var_name = namespace.get_unique_name()
				injected_stmts.append(ExprLine(
						Assignment(var_name, self.right)))
				self.right = VariableRef(var_name)

			self.left, injected_left = validate_expr(diff, namespace)
			injected_stmts.extend(injected_left)
			self.right = Number(0)

			return (None, injected_stmts)

	def validate_branchable_as_xor(self, namespace):
		self.left, injected_stmts = validate_expr_branchable(
				self.left, namespace)
		self.right, injected_stmts_right = validate_expr_branchable(
				self.right, namespace)

		injected_stmts.extend(injected_stmts_right)
		return (None, injected_stmts)

	# Create a Compound condition block which branches to one block
	# if it passes the condition, or another if it fails.
	# then_block and else_block are both CompoundBlock objects
	def create_branch_block(self, then_block, else_block, lineno):
		if self.is_xor():
			return self.create_xor_block(then_block, else_block, lineno)

		if not is_zero(self.right):
			raise HCInternalError("Unable to directly compare "
					+ "to non-zero values", self)

		if self.negate:
			then_block, else_block = else_block, then_block

		cond_block = hrmi.Block(lineno)
		self.left.add_to_block(cond_block)
		cond_block.assign_jz(then_block.first_block)
		cond_block.assign_next(else_block.first_block)

		return hrmi.CompoundBlock(cond_block,
				[*then_block.get_exit_blocks(), *else_block.get_exit_blocks()])

	def create_xor_block(self, then_block, else_block, lineno):
		# XOR is compiled such that there are two copies of the right condition:
		# one for each possible outcome of the left condition.
		right_true_block = self.right.create_branch_block(
				then_block, else_block, lineno)
		right_false_block = self.right.create_branch_block(
				else_block, then_block, lineno)

		if self.negate:
			(right_true_block, right_false_block) = (
					right_false_block, right_true_block)

		return self.left.create_branch_block(
				right_true_block, right_false_block, lineno)

class CompareEq(AbstractEqualityOperator):
	pass

class CompareNe(AbstractEqualityOperator):
	negate = True

class AbstractInequalityOperator(AbstractBinaryOperator):
	hctype = Boolean

	# Set to True by subclasses if the comparison
	# is implemented as the negative of another.
	negative = False

	# Set to True by subclasses of the positive version of the
	# comparison includes equality as passing the condition.
	includes_zero = False

	def validate_branchable(self, namespace):
		self.left,  injected_stmts    = validate_expr(self.left,  namespace)
		self.right, injected_stmts_rt = validate_expr(self.right, namespace)

		injected_stmts.extend(injected_stmts_rt)

		if isinstance(self.left, Number) and isinstance(self.right, Number):
			value = self.eval_static(self.left.value, self.right.value)
			return (value, injected_stmts)

		if is_zero(self.right):
			return (None, injected_stmts)

		if is_zero(self.left):
			return (self.swap_operands(), injected_stmts)

		# eg. (x < y) -> (x - y < 0)
		diff, diff_injected = validate_expr(
				Subtract(self.left, self.right), namespace)
		injected_stmts.extend(diff_injected)

		self.left = diff
		self.right = Number(0)

		return (self, injected_stmts)

	# Create a Compound condition block which branches to one block
	# if it passes the condition, or another if it fails.
	# then_block and else_block are both CompoundBlock objects
	def create_branch_block(self, then_block, else_block, lineno):
		if not is_zero(self.right):
			raise HCInternalError("Unable to directly compare "
					+ "against a value other than zero", self)

		if self.negative:
			then_block, else_block = else_block, then_block

		neg_cond_block = hrmi.Block(lineno)
		self.left.add_to_block(neg_cond_block)
		neg_cond_block.assign_jn(then_block.get_entry_block())

		if self.includes_zero:
			zero_cond_block = hrmi.Block(lineno)
			zero_cond_block.assign_jz(then_block.get_entry_block())
			zero_cond_block.assign_next(else_block.get_entry_block())

			neg_cond_block.assign_next(zero_cond_block)
		else:
			neg_cond_block.assign_next(else_block.get_entry_block())

		return hrmi.CompoundBlock(neg_cond_block,
				[*then_block.get_exit_blocks(), *else_block.get_exit_blocks()])

	def eval_static(self, left, right):
		val = left < right or (self.includes_zero and left == right)

		if self.negative:
			val = not val

		return Boolean(val)

	# Create an reversed version of this operation.
	# Does not need to check for side effects of operands,
	# as this should be handled by the calling function.
	def swap_operands(self):
		raise NotImplementedError(
				"AbstractInequalityOperator.swap_operands", self)

# Less than
class CompareLt(AbstractInequalityOperator):
	def swap_operands(self):
		return CompareGt(self.right, self.left)

# Less than or equal to
class CompareLe(AbstractInequalityOperator):
	includes_zero = True

	def swap_operands(self):
		return CompareGe(self.right, self.left)

# Greater than
class CompareGt(AbstractInequalityOperator):
	negative = True
	includes_zero = True

	def swap_operands(self):
		return CompareLt(self.right, self.left)

# Greater than or equal to
class CompareGe(AbstractInequalityOperator):
	negative = True

	def swap_operands(self):
		return CompareLe(self.right, self.left)

class LogicalNot(AbstractExpr):
	__slots = (
		"operand",
	)

	def __init__(self, operand):
		self.operand = operand

	def has_side_effects(self):
		return self.operand.has_side_effects()

	def get_namespace(self):
		return self.operand.get_namespace()

	def validate_branchable(self, namespace):
		self.operand, injected_stmts = validate_expr_branchable(self.operand, namespace)

		if isinstance(self.operand, Boolean):
			return (Boolean(not self.operand.value), None)

		return (None, injected_stmts)

	def create_branch_block(self, then_block, else_block, lineno=None):
		return self.operand.create_branch_block(else_block, then_block, lineno)

	def __repr__(self):
		return (type(self).__name__ + "("
			+ repr(self.operand) + ")")

# Parent class for && and ||
class AbstractLogicalBinaryOperator(AbstractBinaryOperator):
	def validate_branchable(self, namespace):
		self.left, injected_stmts = validate_expr_branchable(
				self.left, namespace)
		self.right, injected_stmts_right = validate_expr_branchable(
				self.right, namespace)

		if len(injected_stmts_right) > 0:
			self.right = InlineStatementExpr(injected_stmts_right, self.right)

		return (None, injected_stmts)

class LogicalAnd(AbstractLogicalBinaryOperator):
	def create_branch_block(self, then_block, else_block, lineno):
		right_block = self.right.create_branch_block(
				then_block, else_block, lineno)
		left_block = self.left.create_branch_block(
				right_block, else_block, lineno)

		return left_block

class LogicalOr(AbstractLogicalBinaryOperator):
	def create_branch_block(self, then_block, else_block, lineno):
		right_block = self.right.create_branch_block(
				then_block, else_block, lineno)
		left_block = self.left.create_branch_block(
				then_block, right_block, lineno)

		return left_block

# Allows for statements to be evaluated in the middle of an expression.
# Similar to C's ({ ... }) syntax.
class InlineStatementExpr(AbstractExpr):
	__slots__ = (
		# StatementList of statements to evaluate.
		"body",

		# Expression used to return a value to
		# the parent statement or expression.
		"return_expr",
	)

	def __init__(self, body, return_expr):
		self.body = body
		self.return_expr = return_expr

		if not isinstance(self.body, StatementList):
			self.body = StatementList(self.body)

	def create_branch_block(self, then_block, else_block, lineno):
		self.body.create_blocks()

		branch = self.return_expr.create_branch_block(
				then_block, else_block, lineno)

		for blk in self.body.get_exit_blocks():
			blk.assign_next(branch)

		return hrmi.CompoundBlock(self.body.first_block,
				branch.get_exit_blocks())

# Collection of names used in a part or whole of the program
class Namespace:
	__slots__ = [
		"names",
		"next_generated_id",
	]

	# names may initialise to a string, iterable of strings, or None
	def __init__(self, names=None):
		if isinstance(names, str):
			self.names = set((names,))
		elif names is None:
			self.names = set()
		else:
			self.names = set(*names)

		self.next_generated_id = 0

	# Merge another Namespace into this one
	def merge(self, other):
		self.names |= other.names
		if other.next_generated_id > self.next_generated_id:
			self.next_generated_id = other.next_generated_id

	def add_name(self, name):
		self.names.add(name)

	def get_unique_name(self):
		while True:
			name = generate_name(self.next_generated_id)
			self.next_generated_id += 1

			if name not in self.names:
				self.add_name(name)
				return name
