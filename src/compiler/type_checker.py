import compiler.ast as ast
from compiler.types import Int, Type, Bool, Unit, FunType
from compiler.ast import *
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class SymTab(Generic[T]):
    """This is supposed to map variable names to types"""
    mapping: dict[str, T]
    current_return_type: Type | None = None

    def map(self, variable_name: str) -> T:
        return self.mapping[variable_name]
    
    def add_local(self, variable_name: str, variable: T) -> None:
        self.mapping[variable_name] = variable


# Missing currently: ==, != and = (handled as special cases)
type_mappings = {'+': FunType([Int(), Int()], Int()),
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
                 'print_int': FunType([Int()], Unit()),
                 'print_bool': FunType([Bool()], Unit()),
                 'read_int': FunType([], Int()),
                 '=': FunType([Unit(), Unit()], Unit()),
                 '==': FunType([Unit(), Unit()], Bool()),
                 '!=': FunType([Unit(), Unit()], Bool()),
                 'not': FunType([Bool()], Bool())
                }

def typecheck_node(node: ast.Expression, symtab: SymTab) -> Type:

    match node:
        case ast.BinaryOp() if node.op not in ['==', '!=', '=']:
            t1 = typecheck_node(node.left, symtab)
            t2 = typecheck_node(node.right, symtab)
            if node.op not in symtab.mapping: raise Exception(f'Got an unexpected operator {node.op}')
            
            func_type = symtab.map(node.op)
            if not isinstance(func_type, FunType): raise Exception(f'Got {func_type}, not FunType in type checking a BinaryOp')

            p1, p2 = func_type.params[0], func_type.params[1]
            if t1 != p1 or t2 != p2: raise Exception(f'Operator {node.op} expects {func_type.params}, got {t1} and {t2}')
            node.type = func_type.return_type
            return func_type.return_type
        case ast.BinaryOp() if node.op in ['==', '!=', 'or', 'and']:
            t1 = typecheck_node(node.left, symtab)
            t2 = typecheck_node(node.right, symtab)

            if type(t1) != type(t2): raise Exception(f'Expected two of the same type, got {t1} and {t2}')
            node.type = Bool()
            return Bool()
        
        case ast.BinaryOp() if node.op == '=':
            t1 = typecheck_node(node.left, symtab)
            typecheck_node(node.right, symtab)
            # For chained assignment (a = b = c), find the innermost assigned value's type.
            rhs = node.right
            while isinstance(rhs, ast.BinaryOp) and rhs.op == '=':
                rhs = rhs.right
            t_value = rhs.type
            if isinstance(node.left, Identifier):
                symtab.mapping[node.left.name] = t_value

            if t1 != t_value: raise Exception(f'Assignment requires both sides to have the same types, got {t1} and {t_value}')
            
            node.type = Unit()
            return Unit()
        case ast.IfStatement():
            t1 = typecheck_node(node.first_expr, symtab)
            if t1 != Bool():
                raise Exception(f"Was expecting the condition to be type Bool but got {t1}")
            t2 = typecheck_node(node.second_expr, symtab)
            if node.the_else is not None and node.third_expr is not None:
                t3 = typecheck_node(node.third_expr, symtab)
                if t2 != t3:
                    raise Exception(f"Was expecting the 2nd and 3rd expressions to have same types but got {t2} and {t3}")
            return t2
        case ast.Literal():
            result: Type
            if type(node.value) is bool:
                result = Bool()
            elif type(node.value) is int:
                result = Int()
            elif node.value is None:
                return Unit()
            else: 
                raise Exception(f'Unknown literal type {type(node.value)}')
            node.type = result
            return result
        case ast.VariableDeclaration():
            tExpr = typecheck_node(node.expression, symtab)
            if node.ID.name in symtab.mapping:
                raise Exception(f'Variable {node.ID.name} already declared in this scope')
            symtab.mapping[node.ID.name] = tExpr
            if node.var_type is not None and tExpr != node.var_type:
                raise Exception(f'Variable declaration type mismatch: declared {node.var_type}, got {tExpr}')
            return Unit()
        case ast.UnaryOperator():
            tRight = typecheck_node(node.right, symtab)
            
            if node.op == '-' and not isinstance(tRight, Int): raise Exception(f'- expects an Int, got {tRight}')
            if node.op == 'not' and not isinstance(tRight, Bool): raise Exception(f'not expects a Bool, got {tRight}')
            return tRight

        case ast.FunctionCall():
            function_name: Identifier = node.function_name
            function_type: FunType = symtab.map(function_name.name)
            function_type.params
            for i, (node_param, func_param) in enumerate(zip(node.arguments, function_type.params)):
                # typecheck(node.arg) has to match function_type.params
                param_type: Type = typecheck_node(node_param, symtab)

                if param_type != func_param: raise Exception(f'Parameter {i} of function {function_name.name} expects {func_param}, got {param_type}')

            return function_type.return_type
        
        case ast.WhileStatement():
            tCond = typecheck_node(node.condition_expr, symtab)
            if not isinstance(tCond, Bool): raise Exception(f'While condition expects Bool, got {tCond}')
            return Unit()
        case ast.Identifier():
            if node.name not in symtab.mapping:
                raise Exception(f'Undefined identifier {node.name}')
            node.type = symtab.map(node.name)
            return node.type
        case ast.Block():
            # Create a new scope for the block
            block_symtab = SymTab(mapping=symtab.mapping.copy(), current_return_type=symtab.current_return_type)
            for expr in node.expressions:
                typecheck_node(expr, block_symtab)
                
            if node.result_expression is not None:
                result_type = typecheck_node(node.result_expression, block_symtab)
            else:
                result_type = Unit()
            node.type = result_type
            return result_type
        
        case ast.Break():
            node.type = Unit()
            return Unit()
        
        case ast.Continue():
            node.type = Unit()
            return Unit()
        
        case ast.FunctionDefinition():
            param_types = [param_type for _, param_type in node.params]
            func_type = FunType(params=param_types, return_type=node.return_type)
            
            if node.name.name in symtab.mapping:
                raise Exception(f'Function {node.name.name} already declared in this scope')
            symtab.mapping[node.name.name] = func_type
            
            func_symtab = SymTab(mapping=symtab.mapping.copy(), current_return_type=node.return_type)
            
            for param_name, param_type in node.params:
                func_symtab.mapping[param_name.name] = param_type
            
            typecheck_node(node.body, func_symtab)
            
            node.type = Unit()
            return Unit()
        
        case ast.Return():
            value_type = typecheck_node(node.value, symtab)
            if symtab.current_return_type is None:
                raise Exception(f'Return statement outside of function')
            if value_type != symtab.current_return_type:
                raise Exception(f'Return type mismatch: expected {symtab.current_return_type}, got {value_type}')
            node.type = value_type
            return value_type
        
        case _:
            raise Exception(f'Unknown AST node {node}')
        

def typecheck(node: ast.Expression, symtab: SymTab | None = None) -> Type:
    if symtab is None:
        symtab = SymTab(mapping=type_mappings)

    node_type = typecheck_node(node, symtab)
    node.type = node_type
    return node_type