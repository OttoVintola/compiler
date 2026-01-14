from compiler.tokenizer import tokenize

def test_tokenizer_basics() -> None:
    assert tokenize("if 3\nwhile") == ['if', '3', 'while']
    assert tokenize("for 3 in range 100") == ['for', '3', 'in', 'range', '100']
    assert tokenize("9 for i to 10") == ['9', 'for', 'i', 'to', '10']