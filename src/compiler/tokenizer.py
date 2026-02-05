import re 
from dataclasses import dataclass

@dataclass
class TokenLocation:
    row: int
    col: int

L = TokenLocation(-1, -1)

@dataclass
class Token:
    text: str
    type: str
    loc: TokenLocation

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Token):
            return self.loc is L or other.loc is L
        return False


def tokenize(source_code: str) -> list[Token]:
    pos = 0
    result = []
    while pos < len(source_code):
        whitespace = re.compile("( )|(\t)|(\n)|(\r)")
        whitespaces = whitespace.match(source_code, pos)
        if whitespaces is not None:
            pos+=1
        
        comment = re.compile("# [a-z]*")
        comments = comment.match(source_code, pos)
        if comments is not None:
            length = comments.span()[1] - comments.span()[0]
            pos+=length

        identifier = re.compile("([a-zA-Z_])([a-zA-Z0-9_]*)")
        identifiers = identifier.match(source_code, pos)
        if identifiers is not None:
            start = identifiers.span()[0]
            end = identifiers.span()[1]
            length = end - start
            #result.append(source_code[start:end])
            result.append(Token(source_code[start:end], "identifier", L))
            pos+=length
            

        int_literals = re.compile("[0-9]+")
        int_lits = int_literals.match(source_code, pos)
        if int_lits is not None:
            end = int_lits.span()[1]
            start = int_lits.span()[0]
            length = end - start
            result.append(Token(source_code[start:end], "int_literal", L))
            pos += length
            
        operator = re.compile("!=|==|>=|<=|[<>+-/*%=]")
        operators = operator.match(source_code, pos)
        if operators is not None:
            end = operators.span()[1]
            start = operators.span()[0]
            length = end - start
            result.append(Token(source_code[start:end], "operator", L))
            pos += length

        punctuation = re.compile("[{}():;,]")
        punctuations = punctuation.match(source_code, pos)
        if punctuations is not None:
            end = punctuations.span()[1]
            start = punctuations.span()[0]
            length = end - start
            result.append(Token(source_code[start:end], "punctuation", L))
            pos += length

    return result