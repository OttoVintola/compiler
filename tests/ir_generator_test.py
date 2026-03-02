
from compiler import ast, ir
from compiler.type_checker import SymTab, type_mappings, typecheck
from compiler.types import Bool, Int, Unit
from compiler.ir import IRVar, Call
from compiler.tokenizer import L, tokenize
from compiler.parser import parse
from compiler.ir_generator import generate_ir

def test_ir_generator() -> None:

    # print(parse(tokenize("1")).type)

    # print(generate_ir(
    #     reserved_names=set(type_mappings.keys()),
    #     root_expr=parse(tokenize("1"))
    # ))
    # root_expr=parse(tokenize("if (2 > 1) then 3 else 4"))
    # root_expr = parse(tokenize("while (2 > 1) do print_int(3)"))
    # root_expr = parse(tokenize("var x = 2"))
    root_expr = parse(tokenize("2 + 2"))
    typecheck(root_expr)
    # print("\n", root_expr)
    # print(root_expr)
    ir_list = generate_ir(
        reserved_names=set(type_mappings.keys()),
        root_expr=root_expr
    )

    #for instr in ir_list:
    #    print(instr)
