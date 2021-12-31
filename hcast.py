import string
import math
from dataclasses import dataclass

import hrminstr as hrmi

class HCTypeError(Exception):
	pass

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
			raise HCTypeError("Expression cannot be validated", expr)
		
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
		"indent",
		"block"
	]

	def __init__(self, indent=""):
		self.indent = indent

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

# eg: let x
class Declare(AbstractLine):
	__slots__ = ["name"]

	def create_block(self):
		# Empty block
		self.block = hrmi.Block()

	def __init__(self, name, indent=""):
		super().__init__(indent)
		self.name = name

	def get_namespace(self):
		return Namespace(self.name)

	def validate(self, namespace):
		return None

	def __repr__(self):
		return ("Declare("
			+ repr(self.name) + ", "
			+ repr(self.indent) + ")")

# eg: init Zero @ 10
class InitialValueDeclaration(AbstractLine):
	__slots__ = [
		"name",
		"loc",
	]

	def create_block(self):
		# Empty block
		self.block = hrmi.Block()
	
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
					raise HCTypeError(f"Variable {mem.name} declared twice")
				if mem.loc in memory_by_loc:
					raise HCTypeError(f"Multiple variables declared at {mem.loc}")

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

	def __init__(self, stmts=None):
		self.stmts = stmts
		if self.stmts is None:
			self.stmts = []
	
	def __repr__(self):
		return f"StatementList({repr(self.stmts)})"

# forever loop
class Forever(AbstractLine):
	__slots__ = ["body"]

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

	def __init__(self, body=None):
		self.body = body

		if self.body is None:
			self.body = StatementList()

	def __repr__(self):
		return f"Forever({repr(self.body)})"

class If(AbstractLine):
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

	def create_block(self):
		# Fill in empty else block
		if self.else_block is None:
			self.else_block = StatementList()

		self.then_block.create_blocks()
		self.else_block.create_blocks()

		condition_block = hrmi.Block()

		if isinstance(self.condition, Boolean):
			if self.condition.value:
				code_block = self.then_block
			else:
				code_block = self.else_block

			condition_block.assign_next(code_block.first_block)
			self.block = hrmi.CompoundBlock(code_block.first_block, [code_block.last_block])

		elif isinstance(self.condition, AbstractBinaryOperator):
			self.condition.left.add_to_block(condition_block)

			if not (isinstance(self.condition.right, Number) and self.condition.right.value == 0):
				raise HCInternalError("Unable to directly compare to non-zero values", self)

			then_bl = self.then_block
			else_bl = self.else_block

			negate = isinstance(self.condition, CompareNe)
			if negate:
				then_bl, else_bl = else_bl, then_bl

			condition_block.assign_jz(then_bl.first_block)
			condition_block.assign_next(else_bl.first_block)

			self.block = hrmi.IfThenElseBlock(condition_block, self.then_block.last_block, self.else_block.last_block)

		else:
			raise HCInternalError("Unable to generate code for if statement with non-comparison condition", self.condition)

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
		self.block = hrmi.Block()
		self.expr.add_to_block(self.block)
		self.block.add_instruction(hrmi.Output())

	def __repr__(self):
		return ("Output("
			+ repr(self.expr) + ", "
			+ repr(self.indent) + ")")

class ExprLine(AbstractLineWithExpr):
	def create_block(self):
		self.block = hrmi.Block()
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

class VariableRef(AbstractExpr):
	__slots__ = ["name"]

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

class Number(AbstractExpr):
	__slots__ = ["value"]

	def __init__(self, value):
		self.value = value

	def add_to_block(self, block):
		block.add_instruction(hrmi.LoadConstant(self.value))

	def validate(self, namespace):
		return (None, None)

	def has_side_effects(self):
		return False

	def get_namespace(self):
		return Namespace()

	def __repr__(self):
		return ("Number("
			+ repr(self.value) + ")")

def is_zero(expr):
	return isinstance(expr, Number) and expr.value == 0

# Boolean value.
# Currently not directly producable by the source code
class Boolean(AbstractExpr):
	__slots__ = ["value"]

	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return ("Boolean("
			+ repr(self.value) + ")")


class Input(AbstractExpr):
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

class Add(AbstractBinaryOperator):
	def add_to_block(self, block):
		self.left.add_to_block(block)

		if isinstance(self.right, VariableRef):
			block.add_instruction(hrmi.Add(self.right.name))
		else:
			raise HCInternalError("Unable to directly add right operand",
					self.right)

	def validate(self, namespace):
		injected_stmts = []

		while True:
			# Recurse on both operands
			self.left, left_injected = validate_expr(self.left, namespace)
			injected_stmts.extend(left_injected)

			self.right, right_injected = validate_expr(self.right, namespace)
			injected_stmts.extend(right_injected)

			# Handle constant values
			if isinstance(self.left, Number) and isinstance(self.right, Number):
				return (Number(self.left.value + self.right.value), injected_stmts)

			if is_zero(self.left):
				return (self.right, injected_stmts)

			if is_zero(self.right):
				return (self.left, injected_stmts)

			if isinstance(self.right, VariableRef):
				break

			# If the right hand side is an add node, rotate
			# to put the child add on the left
			# Relies on associativity
			if isinstance(self.right, Add):
				# a + (b + c) -> (a + b) + c
				a = self.left
				b = self.right.left
				c = self.right.right
				self.left = Add(a, b)
				self.right = c
				continue

			if isinstance(self.right, Subtract):
				# a + (b - c) -> (a + b) - c
				a = self.left
				b = self.right.left
				c = self.right.right
				self.left = Subtract(Add(a, b), c)
				self.right = Number(0)
				continue

			# Swap operands. Relies on commutativity
			self.left, self.right = self.right, self.left

			if self.right.has_side_effects():
				var_name = namespace.get_unique_name()
				new_assign = ExprLine(Assignment(var_name, self.right))
				injected_stmts.append(new_assign)
				self.right = VariableRef(var_name)

		return (None, injected_stmts)

class Subtract(AbstractBinaryOperator):
	def add_to_block(self, block):
		self.left.add_to_block(block)

		if isinstance(self.right, VariableRef):
			block.add_instruction(hrmi.Subtract(self.right.name))
		else:
			raise HCInternalError("Unable to directly subtract right operand",
					self.right)

	def validate(self, namespace):
		injected_stmts = []

		while True:
			# Recurse on both operands
			self.left, left_injected = validate_expr(self.left, namespace)
			injected_stmts.extend(left_injected)

			self.right, right_injected = validate_expr(self.right, namespace)
			injected_stmts.extend(right_injected)

			# Handle constant values
			if isinstance(self.left, Number) and isinstance(self.right, Number):
				return (Number(self.left.value - self.right.value), injected_stmts)

			if is_zero(self.right):
				return (self.left, injected_stmts)

			if isinstance(self.right, VariableRef):
				break

			# If the right hand side is an add node, rotate
			# to put the child add on the left
			# Relies on associativity
			if isinstance(self.right, Add):
				# a - (b + c) -> (a - b) - c
				a = self.left
				b = self.right.left
				c = self.right.right
				self.left = Subtract(a, b)
				self.right = c
				continue

			if isinstance(self.right, Subtract):
				# a - (b - c) -> (a - b) + c
				a = self.left
				b = self.right.left
				c = self.right.right
				self.left = Add(Subtract(a, b), c)
				self.right = Number(0)
				continue

			# If we get here, we haven't got anything directly subtractable
			# into the right hand side, so we need to store the value
			# of the rhs in a new variable.
			if self.left.has_side_effects() and self.right.has_side_effects():
				left_name = namespace.get_unique_name()
				left_assign = ExprLine(Assignment(left_name, self.left))
				injected_stmts.append(new_assign)
				self.left = VariableRef(left_name)

			right_name = namespace.get_unique_name()
			right_assign = ExprLine(Assignment(right_name, self.right))
			injected_stmts.append(new_assign)
			self.right = VariableRef(right_name)

		return (None, injected_stmts)

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
		# print("Finding strategy for", product, "as product of", factors)

		strategy = MultiplicationStrategy(factors, i)
		# print("Able to reach", product, "in", strategy.instructions, "instructions")

		if (best_strategy is None
				or strategy.instructions < best_strategy.instructions):
			best_strategy = strategy

		i += 1

	# print("Optimal strategy for", n, "is", best_strategy, "(", best_strategy.instructions, "steps)")
	_multiplication_stategies[n] = best_strategy
	return best_strategy

# Nest repeated addition nodes
def nest_addition(expr, n):
	if n == 0:
		return Number(0)

	if n == 1:
		return expr

	return Add(nest_addition(expr, n - 1), expr)

# Find an efficient way to multiply an expression by a constant using only addition.
# Returns (a new expression node, and a list of injected statements)
def validate_expr_mul_const(expr, n, namespace):
	injected_stmts = []

	if expr.has_side_effects() and n > 1:
		var_name = namespace.get_unique_name()
		new_assign = ExprLine(Assignment(var_name, expr))
		injected_stmts.append(new_assign)
		expr = VariableRef(var_name)

	factors, offset = find_multiplication_strategy(n)
	factors.sort(reverse=True)

	product_expr = expr
	product_name = namespace.get_unique_name()

	# For each factor except the last
	for fact in factors[0:-1]:
		# Multiply by this prime factor by repeated addition
		nested_add = nest_addition(product_expr, fact)
		nested_add, injected_nested = validate_expr(nested_add, namespace)
		injected_stmts.extend(injected_nested)

		injected_stmts.append(ExprLine(Assignment(product_name, nested_add)))
		product_expr = VariableRef(product_name)

	nested_add = nest_addition(product_expr, factors[-1])
	nested_add = Add(nested_add, nest_addition(expr, offset))
	nested_add, injected_nested = validate_expr(nested_add, namespace)
	injected_stmts.extend(injected_nested)

	return (nested_add, injected_stmts)

class Multiply(AbstractBinaryOperator):
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
	negate = False

	def validate_branchable(self, namespace):
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
			raise HCInternalError("Cannot make comparison branchable", self)

class CompareEq(AbstractEqualityOperator):
	pass

class CompareNe(AbstractEqualityOperator):
	negate = True

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
