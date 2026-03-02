from compiler.assembly_generator import generate_assembly
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.ir import IRVar, LoadIntConst, Copy, Call
from compiler.ir_generator import generate_ir

from compiler.type_checker import SymTab, type_mappings, typecheck

def test_assembly_generator() -> None:
    reserved_names=set(type_mappings.keys())
    tokens = tokenize("""fun factorial(x: Int): Int {
    var result = 0;
    if x > 1 then {
        result = x * factorial(x - 1);
    } else {
        result = 1;
    }
    return result;
}

factorial(5)""")
    expressions = parse(tokens)
    typecheck(expressions)
    print(expressions)
    ir = generate_ir(reserved_names=reserved_names, root_expr=expressions)
    for irn in ir:
        print(irn)
    print(generate_assembly(ir))

