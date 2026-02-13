from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.tokenizer import Token, TokenLocation, L
from compiler.ast import *
from compiler.types import Int, Bool


def test_parser_basics() -> None:
    assert parse([
                    Token('a', 'identifier', loc=L), 
                    Token('+', 'operator', loc=L),
                    Token('b', 'identifier', loc=L)
                ]) == BinaryOp(
        left=Identifier(name='a', location=L), op="+", right=Identifier(name='b', location=L), location=L)
    
    try:
        unaccepted = parse(tokenize("a + b c"))
        if (unaccepted):
            assert unaccepted != Exception
    except Exception as e:
        pass
    
    assert parse([]) == EmptyInput(location=TokenLocation(0,0))

    assert parse(tokenize("42")) == Literal(value=42, location=L, type=Int())

    assert parse(tokenize("x * (y + 3)")) == BinaryOp(left=Identifier(name='x', location=L), op='*', 
                                                      right=BinaryOp(left=Identifier(name='y', location=L), 
                                                                     op='+', right=Literal(value=3, location=L, type=Int()), location=L), location=L)
    
    # Else is optional
    assert parse(tokenize("if a then b")) == IfStatement(the_if=Identifier(name='if', location=L), 
                                                        first_expr=Identifier(name='a', location=L),
                                                        the_then=Identifier(name='then', location=L),
                                                        second_expr=Identifier(name='b', location=L),
                                                        the_else=None,
                                                        third_expr=None,
                                                        location=L)
    
    assert parse(tokenize("if x then y else z")) == IfStatement(the_if=Identifier(name='if', location=L),
                                                              first_expr=Identifier(name='x', location=L),
                                                              the_then=Identifier(name='then', location=L),
                                                              second_expr=Identifier(name='y', location=L),
                                                              the_else=Identifier(name='else', location=L),
                                                              third_expr=Identifier(name='z', location=L),
                                                              location=L)
    
    assert parse(tokenize("1 + if 10 then 2 else 3")) == BinaryOp(left=Literal(value=1, location=L, type=Int()),
                                                                  op='+',
                                                                  right=IfStatement(the_if=Identifier(name='if', location=L),
                                                                                   first_expr=Literal(value=10, location=L, type=Int()),
                                                                                   the_then=Identifier(name='then', location=L),
                                                                                   second_expr=Literal(value=2, location=L, type=Int()),
                                                                                   the_else=Identifier(name='else', location=L),
                                                                                   third_expr=Literal(value=3, location=L, type=Int()),
                                                                                   location=L),
                                                                  location=L)
    
    assert parse(tokenize("if a then if b then c else d")) == IfStatement(the_if=Identifier(name='if', location=L),
                                                              first_expr=Identifier(name='a', location=L),
                                                              the_then=Identifier(name='then', location=L),
                                                                second_expr=IfStatement(the_if=Identifier(name='if', location=L),
                                                                                            first_expr=Identifier(name='b', location=L),
                                                                                            the_then=Identifier(name='then', location=L),
                                                                                            second_expr=Identifier(name='c', location=L),
                                                                                            the_else=Identifier(name='else', location=L),
                                                                                            third_expr=Identifier(name='d', location=L),
                                                                                            location=L),
                                                                the_else=None,
                                                                third_expr=None,
                                                                location=L)
    
    

    assert parse(tokenize('f(a, b + c)')) == FunctionCall(function_name=Identifier(name='f', location=L),
                                                        arguments=[Identifier(name='a', location=L),
                                                                   BinaryOp(left=Identifier(name='b', location=L),
                                                                            op='+',
                                                                            right=Identifier(name='c', location=L),
                                                                            location=L)],
                                                        location=L)  
    
    assert parse(tokenize('g()')) == FunctionCall(function_name=Identifier(name='g', location=L),
                                                arguments=[],
                                                location=L)
    
    assert parse(tokenize('4 % 2')) == BinaryOp(left=Literal(value=4, location=L, type=Int()),
                                                op='%',
                                                right=Literal(value=2, location=L, type=Int()),
                                                location=L)
    
    assert parse(tokenize('-5 + 5')) == BinaryOp(left=UnaryOperator(op='-', right=Literal(value=5, location=L, type=Int()), location=L),
                                                op='+',
                                                right=Literal(value=5, location=L, type=Int()),
                                                location=L)
    

    assert parse(tokenize('not a and b')) == BinaryOp(left=UnaryOperator(op='not', right=Identifier(name='a', location=L), location=L),
                                                    op='and',
                                                    right=Identifier(name='b', location=L),
                                                    location=L)
    
    
    assert parse(tokenize('not not true')) == UnaryOperator(op='not',
                                                right=UnaryOperator(op='not',
                                                                    right=Literal(value=True, location=L),
                                                                    location=L),
                                                location=L)
    
    assert parse(tokenize("""{
                                f(a);
                                x = y;
                                f(x)
                            }""")) == Block(expressions=[FunctionCall(function_name=Identifier(name='f', location=L), arguments=[Identifier(name='a', location=L)], location=L),
                                                         BinaryOp(left=Identifier(name='x', location=L), op='=', right=Identifier(name='y', location=L), location=L),
                                                         FunctionCall(function_name=Identifier(name='f', location=L), arguments=[Identifier(name='x', location=L)], location=L)
                                                        ],
                                                        has_semicolon=False,
                                                        result_expression=FunctionCall(function_name=Identifier(name='f', location=L), arguments=[Identifier(name='x', location=L)], location=L),
                                                        location=L)
    
    assert parse(tokenize("var x: Int = 120")) == VariableDeclaration(ID=Identifier(name='x', location=L), expression=Literal(value=120, location=L, type=Int()), var_type=Int(), location=L)

    assert parse(tokenize("{ { x } { y } }")) == Block(expressions=[Block(expressions=[Identifier(name='x', location=L)], has_semicolon=False, result_expression=Identifier(name='x', location=L), location=L),
                                                                    Block(expressions=[Identifier(name='y', location=L)], has_semicolon=False, result_expression=Identifier(name='y', location=L), location=L)], 
                                                                    has_semicolon=False, result_expression=Block(expressions=[Identifier(name='y', location=L)], has_semicolon=False, result_expression=Identifier(name='y', location=L), location=L), location=L)
    

    try:
        parse(tokenize("{ a b }"))
        assert False, "Should have raised an exception"
    except Exception:
        pass


    assert parse(tokenize("{ if true then { a } b }")) == Block(
        expressions=[
            IfStatement(
                the_if=Identifier(name='if', location=L),
                first_expr=Literal(value=True, location=L),
                the_then=Identifier(name='then', location=L),
                second_expr=Block(expressions=[Identifier(name='a', location=L)], has_semicolon=False, result_expression=Identifier(name='a', location=L), location=L),
                the_else=None,
                third_expr=None,
                location=L
            ),
            Identifier(name='b', location=L)
        ],
        has_semicolon=False,
        result_expression=Identifier(name='b', location=L),
        location=L
    )

    assert parse(tokenize("{ if true then { a }; b }")) == Block(
        expressions=[
            IfStatement(
                the_if=Identifier(name='if', location=L),
                first_expr=Literal(value=True, location=L),
                the_then=Identifier(name='then', location=L),
                second_expr=Block(expressions=[Identifier(name='a', location=L)], has_semicolon=False, result_expression=Identifier(name='a', location=L), location=L),
                the_else=None,
                third_expr=None,
                location=L
            ),
            Identifier(name='b', location=L)
        ],
        has_semicolon=False,
        result_expression=Identifier(name='b', location=L),
        location=L
    )

    try:
        parse(tokenize("{ if true then { a } b c }"))
        assert False, "Should have raised an exception"
    except Exception:
        pass

    assert parse(tokenize("{ if true then { a } b; c }")) == Block(
        expressions=[
            IfStatement(
                the_if=Identifier(name='if', location=L),
                first_expr=Literal(value=True, location=L),
                the_then=Identifier(name='then', location=L),
                second_expr=Block(expressions=[Identifier(name='a', location=L)], has_semicolon=False, result_expression=Identifier(name='a', location=L), location=L),
                the_else=None,
                third_expr=None,
                location=L
            ),
            Identifier(name='b', location=L),
            Identifier(name='c', location=L)
        ],
        has_semicolon=False,
        result_expression=Identifier(name='c', location=L),
        location=L
    )

    assert parse(tokenize("{ if true then { a } else { b } c }")) == Block(
        expressions=[
            IfStatement(
                the_if=Identifier(name='if', location=L),
                first_expr=Literal(value=True, location=L),
                the_then=Identifier(name='then', location=L),
                second_expr=Block(expressions=[Identifier(name='a', location=L)], has_semicolon=False, result_expression=Identifier(name='a', location=L), location=L),
                the_else=Identifier(name='else', location=L),
                third_expr=Block(expressions=[Identifier(name='b', location=L)], has_semicolon=False, result_expression=Identifier(name='b', location=L), location=L),
                location=L
            ),
            Identifier(name='c', location=L)
        ],
        has_semicolon=False,
        result_expression=Identifier(name='c', location=L),
        location=L
    )

    assert parse(tokenize("x = { { f(a) } { b } }")) == BinaryOp(
        left=Identifier(name='x', location=L),
        op='=',
        right=Block(
            expressions=[
                Block(
                    expressions=[FunctionCall(function_name=Identifier(name='f', location=L), arguments=[Identifier(name='a', location=L)], location=L)],
                    has_semicolon=False,
                    result_expression=FunctionCall(function_name=Identifier(name='f', location=L), arguments=[Identifier(name='a', location=L)], location=L),
                    location=L
                ),
                Block(
                    expressions=[Identifier(name='b', location=L)],
                    has_semicolon=False,
                    result_expression=Identifier(name='b', location=L),
                    location=L
                )
            ],
            has_semicolon=False,
            result_expression=Block(
                expressions=[Identifier(name='b', location=L)],
                has_semicolon=False,
                result_expression=Identifier(name='b', location=L),
                location=L
            ),
            location=L
        ),
        location=L
    )

    assert parse(tokenize('while (x < 10) do x = x + 1')) == WhileStatement(location=TokenLocation(row=-1, col=-1), the_while=Identifier(location=TokenLocation(row=-1, col=-1), name='while'), 
                                                                            condition_expr=BinaryOp(location=TokenLocation(row=-1, col=-1), left=Identifier(location=TokenLocation(row=-1, col=-1), name='x'), 
                                                                                                    op='<', right=Literal(location=TokenLocation(row=-1, col=-1), value=10, type=Int())), 
                                                                            the_do=Identifier(location=TokenLocation(row=-1, col=-1), name='do'), 
                                                                            body_expr=BinaryOp(location=TokenLocation(row=-1, col=-1), left=Identifier(location=TokenLocation(row=-1, col=-1), name='x'), op='=', 
                                                                                               right=BinaryOp(location=TokenLocation(row=-1, col=-1), left=Identifier(location=TokenLocation(row=-1, col=-1), name='x'), 
                                                                                                              op='+', right=Literal(location=TokenLocation(row=-1, col=-1), value=1, type=Int()))))