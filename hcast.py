from dataclasses import dataclass

import hrminstr as hrmi

class HCTypeError(Exception):
	pass

class HCInternalError(Exception):
	pass

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

	# Most statements don't require validation
	# def validate(self):
	# 	return None

	# Create a block of HRM instructions to represent this line
	# Assign to self.block
	# Doesn't need to assign_next yet
	def create_block(self):
		raise NotImplementedError("AbstractLine.createBlock", self)

# eg: let x
class Declare(AbstractLine):
	__slots__ = ["name"]

	def create_block(self):
		# Empty block
		self.block = hrmi.Block()

	def __init__(self, name, indent=""):
		super().__init__(indent)
		self.name = name
	
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
	
	def __repr__(self):
		return ("Declare("
			+ repr(self.name) + ", "
			+ repr(self.loc) + ", "
			+ repr(self.indent) + ")")

@dataclass
class MemoryLocation:
	name: str
	loc: int

# Sequence of AbstractLine objects, to be run in order
class StatementList:
	__slots__ = ["stmts"]

	def append(self, stmt):
		self.stmts.append(stmt)

	def create_blocks(self):
		for stmt in self.stmts:
			stmt.create_block()

		# Assign each to jump to the next one
		for i in range(1, len(self.stmts)):
			self.stmts[i - 1].block.assign_next(self.stmts[i].block)
		
		# Last block is left with no jump specified

	# Look up memory locations of variables specified by the program
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
	def validate_structure(self):
		i = 0
		while i < len(self.stmts):
			stmt = self.stmts[i]
			result = stmt.validate()

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

	def validate(self):
		self.body.validate_structure()
		return None

	def __init__(self, body=None):
		self.body = body

		if self.body is None:
			self.body = StatementList()

	def __repr__(self):
		return f"Forever({repr(self.body)})"

class AbstractLineWithExpr(AbstractLine):
	__slots = ["expr"]

	def __init__(self, expr, indent=""):
		super().__init__(indent)
		self.expr = expr

	def validate(self):
		new_expr, injected_stmts = self.expr.validate()
		if isinstance(new_expr, AbstractExpr):
			self.expr = new_expr
		elif new_expr is not None:
			raise HCInternalError("Unexpected expression replacement type", new_expr)

		if isinstance(injected_stmts, AbstractLine):
			injected_stmts = [injected_stmts]

		if (isinstance(injected_stmts, list)
				and all(isinstance(s, AbstractLine) for s in injected_stmts)):
			return [*injected_stmts, self]
		elif injected_stmts is None:
			return None
		else:
			raise HCInternalError("Unexpected injected statements type", injected_stmts)

# output <expr>
class Output(AbstractLineWithExpr):
	__slots__ = ["expr"]

	def create_block(self):
		self.block = hrmi.Block();
		self.expr.add_to_block(self.block)
		self.block.add_instruction(hrmi.Output())

	def __repr__(self):
		return ("Output("
			+ repr(self.expr) + ", "
			+ repr(self.indent) + ")")

class ExprLine(AbstractLineWithExpr):
	def create_block(self):
		self.block = hrmi.Block();
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

	def validate(self):
		raise NotImplementedError("AbstractExpr.validate", self)

	def has_side_effects(self):
		raise NotImplementedError("AbstractExpr.has_side_effects", self)

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

	def validate(self):
		new_expr, injected_stmts = self.expr.validate()

		if isinstance(new_expr, AbstractExpr):
			self.expr = new_expr
		elif new_expr is not None:
			raise HCInternalError("Unexpected expression replacement type", new_expr)

		if isinstance(injected_stmts, AbstractLine):
			injected_stmts = [injected_stmts]
		elif injected_stmts is None:
			return (None, None)

		injected_stmts.append(self)
		return (None, injected_stmts)

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

	def validate(self):
		return (None, None)

	def has_side_effects(self):
		return False

	def __repr__(self):
		return ("VariableRef("
			+ repr(self.name) + ")")

class Input(AbstractExpr):
	def add_to_block(self, block):
		block.add_instruction(hrmi.Input())

	def validate(self):
		return (None, None)

	def has_side_effects(self):
		return True

	def __repr__(self):
		return "Input()"

class Add(AbstractExpr):
	__slots__ = [
		# Expressions on the left and right side of the operator
		"left",
		"right",
	]

	def __init__(self, left, right):
		self.left = left
		self.right = right

	def add_to_block(self, block):
		self.left.add_to_block(block)

		if isinstance(self.right, VariableRef):
			block.add_instruction(hrmi.Add(self.right.name))

		else:
			raise HCInternalError("Unable to directly add right operand", self.right)

	def validate(self):
		injected_stmts = []

		while True:
			# Recurse on left side
			new_left, left_injected = self.left.validate()
			if isinstance(new_left, AbstractExpr):
				self.left = new_left
			elif new_left is not None:
				raise HCInternalError("Unexpected expression replacement type", new_left)

			if isinstance(left_injected, AbstractLine):
				injected_stmts.append(left_injected)
			elif (isinstance(left_injected, list)
					and all(isinstance(s, AbstractLine) for s in left_injected)):
				injected_stmts.extend(left_injected)
			elif left_injected is not None:
				raise HCInternalError("Unexpected injected statements type", left_injected)

			if isinstance(self.right, VariableRef):
				break

			# If the right hand side is an add node, rotate to put the child add on the left
			# Relies on associativity
			elif isinstance(self.right, Add):
				a = self.left
				b = self.right.left
				c = self.right.right
				self.left = Add(a, b)
				self.right = c
				continue

			# Swap operands. Relies on commutativity
			self.left, self.right = self.right, self.left
		
			if self.right.has_side_effects():
				# TODO: assign unique name somehow
				var_name = "new_var_who_dis"
				new_assign = ExprLine(Assignment(var_name, self.right))
				injected_stmts.append(new_assign)
				self.right = VariableRef(var_name)

		return (None, injected_stmts)

	def has_side_effects(self):
		return self.left.has_side_effects() or self.right.has_side_effects()

	def __repr__(self):
		return ("Add("
			+ repr(self.left) + ", "
			+ repr(self.right) + ")")
