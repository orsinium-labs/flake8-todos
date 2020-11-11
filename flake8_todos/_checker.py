# built-in
from functools import partial
from tokenize import TokenInfo, generate_tokens
from typing import Iterable, Iterator, Tuple

# external
import pycodestyle

# project
from ._cached_property import cached_property
from ._error import Error
from ._rules import rules
from ._token import Token


try:
    from flake8.engine import pep8 as stdin_utils
except ImportError:
    from flake8 import utils as stdin_utils


class Checker:
    name = 'flake8-todos'
    version = '1.0.0'

    rules = rules
    _tokens = None

    def __init__(self, tree=None, filename: str = None, lines: Iterable[str] = None,
                 file_tokens: Iterable[TokenInfo] = None):
        self.filename = 'stdin' if filename in ('stdin', '-', None) else filename
        if lines:
            self.lines = tuple(lines)
        self._tokens = file_tokens

    @cached_property
    def lines(self) -> Tuple[str]:
        if self.filename == 'stdin':
            return stdin_utils.stdin_get_value().splitlines(True)
        return pycodestyle.readlines(self.filename)

    @cached_property
    def tokens(self) -> Tuple[Token, ...]:
        if self._tokens is not None:
            tokens = self._tokens
        else:
            getter = partial(next, iter(self.lines))
            tokens = generate_tokens(getter)  # type: ignore
        return tuple(Token(token) for token in tokens)

    def run(self) -> Iterator[tuple]:
        for error in self.get_errors():
            yield tuple(error) + (type(self), )  # type: ignore

    def get_errors(self) -> Iterator[Error]:
        for rule in self.rules:
            yield from rule(self.tokens)
