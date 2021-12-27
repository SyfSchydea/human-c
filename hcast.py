from dataclasses import dataclass

import hrminstr as hrmi

class HCTypeError(Exception):
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

	def __init__(self, body=None):
		self.body = body

		if self.body is None:
			self.body = StatementList()

	def __repr__(self):
		return f"Forever({repr(self.body)})"

# output <expr>
class Output(AbstractLine):
	__slots__ = ["expr"]

	def create_block(self):
		self.block = hrmi.Block();
		self.expr.add_to_block(self.block)
		self.block.add_instruction(hrmi.Output())

	def __init__(self, expr, indent=""):
		super().__init__(indent)
		self.expr = expr
	
	def __repr__(self):
		return ("Output("
			+ repr(self.expr) + ", "
			+ repr(self.indent) + ")")

class ExprLine(AbstractLine):
	__slots__ = "expr"

	def create_block(self):
		self.block = hrmi.Block();
		self.expr.add_to_block(self.block)

	def __init__(self, expr, indent=""):
		super().__init__(indent)
		self.expr = expr

	def __repr__(self):
		return ("ExprLine("
			+ repr(self.expr) + ", "
			+ repr(self.indent) + ")")

class AbstractExpr:
	# Add instructions to load this expression into the accumulator (hands),
	# along with any side-effects
	def add_to_block(self, block):
		raise NotImplementedError("AbstractExpr.add_to_block", self)

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

	def __repr__(self):
		return ("VariableRef("
			+ repr(self.name) + ")")

class Input(AbstractExpr):
	def add_to_block(self, block):
		block.add_instruction(hrmi.Input())

	def __repr__(self):
		return "Input()"
