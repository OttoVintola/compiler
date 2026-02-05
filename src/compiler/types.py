from dataclasses import dataclass



@dataclass
class Type:
    """Base Type Class"""

@dataclass
class Int(Type):
    #value: int
    pass

@dataclass
class Bool(Type):
    #value: bool
    pass

@dataclass
class FunType(Type):
    params: list[Type]
    return_type: Type

@dataclass
class Unit(Type):
    pass