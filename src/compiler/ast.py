from dataclasses import dataclass, field
from compiler.tokenizer import TokenLocation
from compiler.types import Type, Unit

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    location: TokenLocation
    type: Type = field(kw_only=True, default_factory=lambda: Unit())

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

@dataclass
class IfStatement(Expression):
    """AST node for if-then-else statement where else is optional.
    
        Example: if E1 then E2 else E3
    """
    the_if: Identifier
    first_expr: Expression
    the_then: Identifier
    second_expr: Expression
    the_else: Identifier | None
    third_expr: Expression | None
    

@dataclass
class FunctionCall(Expression):
    """Function call 

    Example: ID(E1, E2, ..., En)
    """
    function_name: Identifier
    arguments: list[Expression]

@dataclass
class UnaryOperator(Expression):
    """

    Example: either -E or not E
    """
    op: str
    right: Expression

@dataclass 
class Block(Expression):
    """
    Block: { E1; E2; ...; En } or { E1; E2; ...; En; } (may be empty, last semicolon optional).
        Semicolons after subexpressions that end in } are optional.
    """
    expressions: list[Expression]
    has_semicolon: bool
    result_expression: Expression | Literal

@dataclass
class VariableDeclaration(Expression):
    ID: Identifier
    expression: Expression
    var_type: Type | None

@dataclass
class WhileStatement(Expression):
    """AST node for while loop statement.
    
        Example: while E1 do E2
    """
    the_while: Identifier
    condition_expr: Expression
    the_do: Identifier
    body_expr: Expression
    

@dataclass
class EmptyInput(Expression):
    pass
