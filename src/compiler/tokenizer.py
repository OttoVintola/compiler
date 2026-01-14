import re 

def tokenize(source_code: str) -> list[str]:
    pos = 0
    result = []
    while pos < len(source_code):
        whitespace = re.compile("( )|(\t)|(\n)|(\r)")
        whitespaces = whitespace.match(source_code, pos)
        if whitespaces is not None:
            pos+=1
            continue
        
        comment = re.compile("# [a-z]*")
        comments = comment.match(source_code, pos)
        if comments is not None:
            length = comments.span()[1] - comments.span()[0]
            pos+=length
            continue

        identifier = re.compile("([a-zA-Z_])([a-zA-Z0-9_]*)")
        identifiers = identifier.match(source_code, pos)
        if identifiers is not None:
            start = identifiers.span()[0]
            end = identifiers.span()[1]
            length = end - start
            result.append(source_code[start:end])
            pos+=length

        int_literals = re.compile("[0-9]+")
        int_lits = int_literals.match(source_code, pos)
        if int_lits is not None:
            end = int_lits.span()[1]
            start = int_lits.span()[0]
            length = end - start
            result.append(source_code[start:end])
            pos += length

    return result