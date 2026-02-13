from compiler.tokenizer import tokenize, Token, L

def test_tokenizer_basics() -> None:
    assert tokenize('aaa 123 bbb') == [
        Token(loc=L, type="identifier", text="aaa"),
        Token(loc=L, type="int_literal", text="123"),
        Token(loc=L, type="identifier", text="bbb"),
    ]

    assert tokenize('if {a > b} execute 2*x') == [
        Token(loc=L, type="identifier", text="if"),
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="identifier", text="a"),
        Token(loc=L, type="operator", text=">"),
        Token(loc=L, type="identifier", text="b"),
        Token(loc=L, type="punctuation", text="}"),
        Token(loc=L, type="identifier", text="execute"),
        Token(loc=L, type="int_literal", text="2"),
        Token(loc=L, type="operator", text="*"),
        Token(loc=L, type="identifier", text="x"),
    ]

    assert tokenize('for (i < 20) { x*x } # skip') == [
        Token(loc=L, type="identifier", text="for"),
        Token(loc=L, type="punctuation", text="("),
        Token(loc=L, type="identifier", text="i"),
        Token(loc=L, type="operator", text="<"),
        Token(loc=L, type="int_literal", text="20"),
        Token(loc=L, type="punctuation", text=")"),
        Token(loc=L, type="punctuation", text="{"),
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="operator", text="*"),
        Token(loc=L, type="identifier", text="x"),
        Token(loc=L, type="punctuation", text="}"),
    ]