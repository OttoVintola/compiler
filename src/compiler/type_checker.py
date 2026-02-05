import compiler.ast as ast
from compiler.types import Int, Type, Bool, Unit, FunType
from compiler.ast import *


@dataclass
class SymTab:
    """This is supposed to map variable names to types"""
    mapping: dict

    def map(self, variable_name: str) -> FunType:
        return self.mapping[variable_name]


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
                 'or': FunType([Bool(), Bool()], Bool())
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
            if p1 != p2: raise Exception(f'Operator {node.op} expects {func_type.params}, got {p1} and {p2}')
 
            return func_type.return_type
        case ast.BinaryOp() if node.op in ['==', '!=']:
            t1 = typecheck_node(node.left, symtab)
            t2 = typecheck_node(node.right, symtab)

            if type(t1) != type(t2): raise Exception(f'Expected two of the same type, got {t1} and {t2}')
            return Bool()
        
        case ast.BinaryOp() if node.op == '=':
            t1 = typecheck_node(node.left, symtab)
            t2 = typecheck_node(node.right, symtab)
            if isinstance(node.left, Identifier):
                symtab.mapping[node.left.name] = t2

            if t1 != t2: raise Exception(f'Assignment requires both sides to have the same types, got {t1} and {t2}')
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
            if type(node.value) is bool:
                return Bool()
            if type(node.value) is int:
                return Int()
            if node.value is None:
                return Unit()
            raise Exception(f'Unknown literal type {type(node.value)}')
        case ast.VariableDeclaration():
            tExpr = typecheck_node(node.expression, symtab)
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
            return symtab.map(node.name)
        case ast.Block():
            result_type: Type = Unit()
            for expr in node.expressions:
                result_type = typecheck_node(expr, symtab)
            return result_type
        
        case _:
            raise Exception(f'Unknown AST node {node}')
        

def typecheck(node: ast.Expression, symtab: SymTab | None = None) -> Type:
    if symtab is None:
        symtab = SymTab(mapping=type_mappings)

    node_type = typecheck_node(node, symtab)
    node.type = node_type
    return node_type