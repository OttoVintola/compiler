from compiler import ir
import dataclasses
from compiler import intrinsics

global_funcs = {'print_int', 'print_bool', 'read_int'}

user_funcs: set[str] = set()

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        # ...  # Completed in task 1
        self._var_to_location = {}
        bytes_used = 0
        for var in variables:
            byte_alignment = 8 + bytes_used
            stack_loc: str = f'-{byte_alignment}(%rbp)'
            self._var_to_location[var] = stack_loc
            bytes_used += 8
        self._stack_used = bytes_used

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def get_all_ir_variables_in_range(instructions: list[ir.Instruction], start: int, end: int) -> list[ir.IRVar]:
    """Get all IR variables from instructions[start:end]"""
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions[start:end]:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                if value.name not in global_funcs and value.name not in intrinsics.all_intrinsics and value.name not in user_funcs:
                    add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        if v.name not in global_funcs and v.name not in intrinsics.all_intrinsics and v.name not in user_funcs:
                            add(v)
    return result_list
    
def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    return get_all_ir_variables_in_range(instructions, 0, len(instructions))

def generate_assembly(instructions: list[ir.Instruction]) -> str:
    lines = []
    def emit(line: str) -> None: lines.append(line)

    user_funcs: set[str] = set()
    for insn in instructions:
        if isinstance(insn, ir.FunctionStart):
            user_funcs.add(insn.name)

    main_end = len(instructions)
    for i, insn in enumerate(instructions):
        if isinstance(insn, ir.FunctionStart):
            main_end = i
            break

    main_vars = get_all_ir_variables_in_range(instructions, 0, main_end)
    locals = Locals(variables=main_vars)
    
    current_locals = locals

    arg_regs = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']

    # ... Emit initial declarations and stack setup here ...
    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')
    emit('.global main')
    emit('.type main, @function')
    emit('.section .text')

    emit('main:')
    emit(f'pushq %rbp')
    emit(f'movq %rsp, %rbp')

    emit(f'subq ${locals.stack_used()}, %rsp')

    i = 0
    we_done = False
    while i < len(instructions):
        insn = instructions[i]
        emit('# ' + str(insn))
        match insn:
            # ass...
            case ir.FunctionStart():
                if not we_done:
                    emit(f'movq %rbp, %rsp')
                    emit(f'popq %rbp')
                    emit('ret')
                    we_done = True
                
                func_end = i + 1
                while func_end < len(instructions):
                    end_insn = instructions[func_end]
                    if isinstance(end_insn, ir.FunctionEnd) and end_insn.name == insn.name:
                        break
                    func_end += 1
                
                func_vars = get_all_ir_variables_in_range(instructions, i, func_end + 1)
                func_locals = Locals(variables=func_vars)
                current_locals = func_locals
                
                emit('')
                emit(f'.global {insn.name}')
                emit(f'.type {insn.name}, @function')
                emit(f'{insn.name}:')
                emit(f'pushq %rbp')
                emit(f'movq %rsp, %rbp')
                emit(f'subq ${func_locals.stack_used()}, %rsp')
                
                # move args to their places
                for j, param_var in enumerate(insn.params):
                    if j < len(arg_regs):
                        emit(f'movq {arg_regs[j]}, {func_locals.get_ref(param_var)}')
                
            case ir.FunctionEnd():
                emit(f'movq %rbp, %rsp')
                emit(f'popq %rbp')
                emit('ret')
                current_locals = locals
                
            case ir.Return():
                emit(f'movq {current_locals.get_ref(insn.value)}, %rax')
                emit(f'movq %rbp, %rsp')
                emit(f'popq %rbp')
                emit('ret')
                
            case ir.Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{insn.name}:')
            case ir.LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f'movq ${insn.value}, {current_locals.get_ref(insn.dest)}')
                else:
                    # Due to a quirk of x86-64, we must use
                    # a different instruction for large integers.
                    # It can only write to a register,
                    # not a memory location, so we use %rax
                    # as a temporary.
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {current_locals.get_ref(insn.dest)}')
            case ir.Jump():
                emit(f'jmp .L{insn.label.name}')
            # ...  # Completed in task 2
            case ir.LoadBoolConst():
                if insn.value:
                    emit(f'movq $1, {current_locals.get_ref(insn.dest)}')
                else:
                    emit(f'movq $0, {current_locals.get_ref(insn.dest)}')
            case ir.Copy():
                if insn.source.name in global_funcs:
                    emit(f'leaq {insn.source.name}(%rip), %rax')
                elif insn.source.name in user_funcs:
                    emit(f'leaq {insn.source.name}(%rip), %rax')
                else:
                    emit(f'movq {current_locals.get_ref(insn.source)}, %rax')
                emit(f'movq %rax, {current_locals.get_ref(insn.dest)}')

            case ir.CondJump():
                emit(f'cmpq $0, {current_locals.get_ref(insn.cond)}')
                emit(f'jne .L{insn.then_label.name}')
                emit(f'jmp .L{insn.else_label.name}')

            case ir.Call():
                if insn.fun.name in intrinsics.all_intrinsics:
                    arg_registers = [current_locals.get_ref(ir_var) for ir_var in insn.args]
                    intrinsics.all_intrinsics[insn.fun.name](intrinsics.IntrinsicArgs(arg_refs=arg_registers, result_register=f'%rax', emit=emit))
                    emit(f'movq %rax, {current_locals.get_ref(insn.dest)}')
                elif insn.fun.name in global_funcs:
                    for j, arg in enumerate(insn.args):
                        if j < len(arg_regs):
                            emit(f'movq {current_locals.get_ref(arg)}, {arg_regs[j]}')
                    emit(f'call {insn.fun.name}')
                    emit(f'movq %rax, {current_locals.get_ref(insn.dest)}')
                elif insn.fun.name in user_funcs:
                    for j, arg in enumerate(insn.args):
                        if j < len(arg_regs):
                            emit(f'movq {current_locals.get_ref(arg)}, {arg_regs[j]}')
                    emit(f'call {insn.fun.name}')
                    emit(f'movq %rax, {current_locals.get_ref(insn.dest)}')
                else:
                    # use pointer call. I don't know why but this seems garbage but hey it works
                    for j, arg in enumerate(insn.args):
                        if j < len(arg_regs):
                            emit(f'movq {current_locals.get_ref(arg)}, {arg_regs[j]}')
                    emit(f'call *{current_locals.get_ref(insn.fun)}')
                    emit(f'movq %rax, {current_locals.get_ref(insn.dest)}')
            
        i += 1
                
        
    if not we_done: 
        # even without functions, need to return... 
        # i dont know why but I get a crash without this
        # maybe its about the caller's stack frame
        emit(f'movq %rbp, %rsp')
        emit(f'popq %rbp')
        emit('ret')

    return '\n'.join(lines) + '\n'