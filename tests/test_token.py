# built-in
from functools import partial
from tokenize import NAME, generate_tokens

# project
from flake8_todos import Token


def test_token_fields():
    getter = partial(next, iter(['a = "b"']))
    tokens = [Token(token) for token in generate_tokens(getter)]
    assert len(tokens) == 5

    assert tokens[0].type == NAME
    assert tokens[0].string == 'a'
    assert tokens[0].start_row == 1
    assert tokens[0].start_col == 0
    assert tokens[0].end_row == 1
    assert tokens[0].end_col == 1
