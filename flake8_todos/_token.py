# built-in
from tokenize import TokenInfo
from typing import Tuple


class Token:
    def __init__(self, token: TokenInfo):
        self.token = token

    @property  # noqa: A003
    def type(self) -> int:
        return self.token[0]

    @property
    def string(self) -> str:
        return self.token[1]

    @property
    def start(self) -> Tuple[int, int]:
        return self.token[2]

    @property
    def start_row(self) -> int:
        return self.start[0]

    @property
    def start_col(self) -> int:
        return self.start[1]

    @property
    def end(self) -> Tuple[int, int]:
        return self.token[3]

    @property
    def end_row(self) -> int:
        return self.end[0]

    @property
    def end_col(self) -> int:
        return self.end[1]

    def __repr__(self) -> str:
        return '{name}({content!r})'.format(
            name=type(self).__name__,
            content=self.token,
        )

    def __str__(self) -> str:
        return self.string
