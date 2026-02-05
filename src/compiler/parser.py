from compiler.tokenizer import Token, TokenLocation
import compiler.ast as ast
from compiler.types import *

def parse(tokens: list[Token]) -> ast.Expression:

    # This keeps track of which token we're looking at.
    pos = 0

    # 'peek()' returns the token at 'pos',
    # or a special 'end' token if we're past the end
    # of the token list.
    # This way we don't have to worry about going past
    # the end elsewhere.
    def peek() -> Token:
        if pos < len(tokens) and len(tokens) > 0:
            return tokens[pos]
        else:
            return Token(text="", type="end", loc=tokens[-1].loc if tokens else TokenLocation(pos, pos))
        

    # 'consume()' returns the token at 'pos'
    # and increments 'pos' by one.
    #
    # If the optional parameter 'expected' is given,
    # it checks that the token being consumed has that text.
    # If 'expected' is a list, then the token must have
    # one of the texts in the list.
    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.loc}: expected {expected} but got {token.text}')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.loc}: expected one of: {comma_separated}')
        pos += 1
        return token
    
    
    # This is the parsing function for integer literals.
    # It checks that we're looking at an integer literal token,
    # moves past it, and returns a 'Literal' AST node
    # containing the integer from the token.
    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f'{peek().loc}: expected an integer literal')
        token = consume()
        return ast.Literal(value=int(token.text), location=token.loc)
    
    def parse_identifier() -> ast.Identifier: 
        if peek().type != 'identifier':
            raise Exception(f'{peek().loc}: expected an identifier')
        token = consume()
        return ast.Identifier(name=token.text, location=token.loc)
    
    def parse_unary() -> ast.UnaryOperator:
        our_op = consume(['not', '-']).text
        if peek().text == '(':
            our_right = parse_parenthesized()
        else:
            our_right = parse_factor(allow_var=False)
        our_unary = ast.UnaryOperator(op=our_op, right=our_right, location=our_right.location)
        return our_unary
            
    def parse_expression(allow_var: bool = True) -> ast.Expression:
        left = parse_expression_left(allow_var)
        if peek().text == '=':
            operator_token = consume('=')
            operator = operator_token.text
            right = parse_expression(allow_var)
            return ast.BinaryOp(left=left, op=operator, right=right, location=left.location)
        return left
    
    def parse_expression_left(allow_var: bool) -> ast.Expression:
        left_associative_binary_operators = [
            ['or'],
            ['and'],
            ['==', '!='],
            ['<', '<=', '>', '>='],
            ['+', '-'],
            ['*', '/', '%'],
        ]
        left = parse_factor(allow_var)
        for i, operators in enumerate(left_associative_binary_operators):
            while peek().text in operators:
                operator_token = consume()
                operator = operator_token.text
                right = parse_factor(allow_var=False)
                left = ast.BinaryOp(left=left, op=operator, right=right, location=left.location)
        return left

    def parse_factor(allow_var: bool = False) -> ast.Expression:
        operators = ['or', 'and', '==', '!=', '<', '<=', '>', '>=', '+', '*', '/', '%']
        assert peek().text not in operators, f'Unexpected operator {peek().text} at {peek().loc}'

        if peek().text == '(':
            return parse_parenthesized()
        if peek().text == '{':
            return parse_block()
        elif peek().text == 'if':
            return parse_if_statement()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().text in ['not', '-']:
            return parse_unary()
        elif peek().text == 'while':
            return parse_while_statement()
        elif peek().type == 'identifier' and peek().text not in ['true', 'false'] and peek().text != 'var':
            identifier = parse_identifier()

            if peek().text == '(':
                # we are in a function call
                consume('(')
                args = []
                while peek().text != ')':
                    if peek().text != ',':
                        args.append(parse_expression(allow_var=False))
                    else:
                        consume(',')
                consume(')')
                our_func = ast.FunctionCall(function_name=identifier, arguments=args, location=identifier.location)
                return our_func
            else:
                return identifier

        elif peek().text == 'var':
            if not allow_var:
                raise Exception(f'{peek().loc}: variable declarations are only allowed at top-level or directly inside blocks')
            return parse_var()
        elif peek().text == 'true':
            consume('true')
            return ast.Literal(value=True, location=peek().loc)
        elif peek().text == 'false':
            consume('false')
            return ast.Literal(value=False, location=peek().loc)
        elif peek().type == 'end':
            return ast.EmptyInput(location=peek().loc)
        else:
            raise Exception(f'{peek().loc}: expected "(", an integer literal or an identifier but got {peek().type} with {peek().text}')
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        # Recursively call the top level parsing function
        # to parse whatever is inside the parentheses.
        expr = parse_expression(allow_var=False)
        consume(')')
        return expr
    
    def parse_block() -> ast.Expression:
        consume('{')
        exprs: list[ast.Expression] = []
        has_semicolon = False
        prev_was_brace = False
        result_expression = ast.Expression(location=peek().loc)
        while peek().text != '}':
            if peek().text == ';':
                consume(';')
                has_semicolon = True
            else:
                if exprs and not has_semicolon and not prev_was_brace:
                    raise Exception(f'{peek().loc}: expected ";" between expressions in block') 
                result_expression = parse_expression(allow_var=True)
                exprs.append(result_expression)
                has_semicolon = False
                prev_was_brace = (tokens[pos - 1].text == '}')
        consume('}')
        our_block = ast.Block(expressions=exprs, has_semicolon=has_semicolon, result_expression=result_expression if not has_semicolon else ast.Literal(value=None, location=peek().loc), location=peek().loc)
        return our_block

    def parse_while_statement() -> ast.Expression:
        our_while = ast.WhileStatement(
            the_while = ast.Identifier(name=consume('while').text, location=peek().loc),
            condition_expr = parse_expression(allow_var=False),
            the_do = ast.Identifier(name=consume('do').text, location=peek().loc),
            body_expr = parse_expression(allow_var=False), location=peek().loc
        )
        return our_while
    
    def parse_if_statement() -> ast.IfStatement:
        has_else: bool = False
        our_if = ast.IfStatement(
            the_if = ast.Identifier(name=consume('if').text, location=peek().loc),
            first_expr = parse_expression(allow_var=False),
            the_then = ast.Identifier(name=consume('then').text, location=peek().loc),
            second_expr = parse_expression(allow_var=False),
            the_else = ast.Identifier(name=consume('else').text, location=peek().loc) if (has_else := peek().text == 'else') else None,
            third_expr = parse_expression(allow_var=False) if has_else else None,
            location=peek().loc
        )
        return our_if
    
    def parse_type() -> Type:
        if peek().text == '(':
            consume('(')
            param_types = [parse_type()]
            while peek().text == ',':
                consume(',')
                param_types.append(parse_type())
            consume(')')

            if peek().text == '=' and tokens[pos+1].text == '>':
                consume('=')
                consume('>')

            return_type = parse_type()

            return FunType(params=param_types, return_type=return_type)
        
        elif peek().type == 'identifier':
            type_name = consume().text
            if type_name == 'Int':
                return Int()
            elif type_name == 'Bool':
                return Bool()
            elif type_name == 'Unit':
                return Unit()
            else:
                raise Exception(f'{peek().loc}: unknown type {type_name}')
        else:
            raise Exception(f'{peek().loc}: expected a type but got {peek().text}')

    def parse_var() -> ast.VariableDeclaration:
        consume('var')
        ID = parse_identifier()
        var_type = None
        if peek().text == ':':
            consume(':')
            var_type = parse_type()

        
        consume('=')
        return ast.VariableDeclaration(ID=ID, expression=parse_expression(allow_var=False), var_type=var_type, location=ID.location)

    result = parse_expression(allow_var=True) 
    if peek().type != 'end':
        raise Exception(f'{peek().loc}: expected the end but got token {peek().text} at {pos}')
    
    return result
