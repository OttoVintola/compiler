
from compiler.type_checker import typecheck, SymTab
from compiler.ast import *
from compiler.types import Int, Bool, Unit, FunType
from compiler.tokenizer import TokenLocation

def test_type_checker_features() -> None:
	L = TokenLocation(-1, -1)
	symtab = SymTab(mapping={
		**{
			'+': FunType([Int(), Int()], Int()),
			'-': FunType([Int(), Int()], Int()),
			'*': FunType([Int(), Int()], Int()),
			'/': FunType([Int(), Int()], Int()),
			'%': FunType([Int(), Int()], Int()),
			'>': FunType([Int(), Int()], Bool()),
			'<': FunType([Int(), Int()], Bool()),
			'>=': FunType([Int(), Int()], Bool()),
			'<=': FunType([Int(), Int()], Bool()),
			'and': FunType([Bool(), Bool()], Bool()),
			'or': FunType([Bool(), Bool()], Bool()),
		},
		'print_int': FunType([Int()], Unit()),
	})

	# Literals
	assert typecheck(Literal(value=42, location=L), symtab) == Int()
	assert typecheck(Literal(value=True, location=L), symtab) == Bool()
	assert typecheck(Literal(value=None, location=L), symtab) == Unit()

	# Variable declaration (untyped)
	var_decl = VariableDeclaration(ID=Identifier(name='x', location=L), expression=Literal(value=2, location=L), var_type=None, location=L)
	assert typecheck(var_decl, symtab) == Unit()
	assert symtab.mapping['x'] == Int()

	# Assignment (x = 3)
	assign = BinaryOp(left=Identifier(name='x', location=L), op='=', right=Literal(value=3, location=L), location=L)
	# symtab.mapping['x'] = Int()
	assert typecheck(assign, symtab) == Unit()

	# Unary operator: -x
	unary = UnaryOperator(op='-', right=Literal(value=5, location=L), location=L)
	assert typecheck(unary, symtab) == Int()

	# Binary operator: x + 1
	binop = BinaryOp(left=Identifier(name='x', location=L), op='+', right=Literal(value=1, location=L), location=L)
	# symtab.mapping['x'] = Int()
	assert typecheck(binop, symtab) == Int()

	# == and !=
	eq = BinaryOp(left=Literal(value=1, location=L), op='==', right=Literal(value=2, location=L), location=L)
	assert typecheck(eq, symtab) == Bool()
	neq = BinaryOp(left=Literal(value=1, location=L), op='!=', right=Literal(value=2, location=L), location=L)
	assert typecheck(neq, symtab) == Bool()

	# Function call: print_int(123)
	call = FunctionCall(function_name=Identifier(name='print_int', location=L), arguments=[Literal(value=123, location=L)], location=L)
	assert typecheck(call, symtab) == Unit()

	# Function-typed variable: var f: (Int) => Unit = print_int; f(123)
	ftype = FunType([Int()], Unit())
	symtab.mapping['print_int'] = ftype
	var_f = VariableDeclaration(ID=Identifier(name='f', location=L), expression=Identifier(name='print_int', location=L), var_type=ftype, location=L)
	assert typecheck(var_f, symtab) == Unit()
	symtab.mapping['f'] = ftype
	call_f = FunctionCall(function_name=Identifier(name='f', location=L), arguments=[Literal(value=123, location=L)], location=L)
	assert typecheck(call_f, symtab) == Unit()

	# Block: { x = 1; x + 2 }
	block = Block(expressions=[
		BinaryOp(left=Identifier(name='x', location=L), op='=', right=Literal(value=1, location=L), location=L),
		BinaryOp(left=Identifier(name='x', location=L), op='+', right=Literal(value=2, location=L), location=L)
	], has_semicolon=True, result_expression=BinaryOp(left=Identifier(name='x', location=L), op='+', right=Literal(value=2, location=L), location=L), location=L)
	# symtab.mapping['x'] = Int()
	assert typecheck(block, symtab) == Int()

	# If expression: if True then 1 else 2
	ifexpr = IfStatement(
		the_if=Identifier(name='if', location=L),
		first_expr=Literal(value=True, location=L),
		the_then=Identifier(name='then', location=L),
		second_expr=Literal(value=1, location=L),
		the_else=Identifier(name='else', location=L),
		third_expr=Literal(value=2, location=L),
		location=L
	)
	assert typecheck(ifexpr, symtab) == Int()

	# While expression: while True do x = 1
	whileexpr = WhileStatement(
		the_while=Identifier(name='while', location=L),
		condition_expr=Literal(value=True, location=L),
		the_do=Identifier(name='do', location=L),
		body_expr=BinaryOp(left=Identifier(name='x', location=L), op='=', right=Literal(value=1, location=L), location=L),
		location=L
	)
	assert typecheck(whileexpr, symtab) == Unit()
