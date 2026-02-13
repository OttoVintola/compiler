from compiler.assembly_generator import generate_assembly
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.ir import IRVar, LoadIntConst, Copy, Call
from compiler.ir_generator import generate_ir

from compiler.type_checker import SymTab, type_mappings

def test_assembly_generator() -> None:
    reserved_names=set(type_mappings.keys())
    tokens = tokenize('''{ var x = true; if x then 1 else 2; }''')
    expressions = parse(tokens)
    ir = generate_ir(reserved_names=reserved_names, root_expr=expressions)
    #print(generate_assembly(ir))