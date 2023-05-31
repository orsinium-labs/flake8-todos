from __future__ import annotations

import re
from tokenize import COMMENT, NEWLINE, NL
from typing import ClassVar, Iterator

from ._constants import ALL_TAGS, BAD_TAGS
from ._error import Error
from ._token import Token


REX_ALL_TAGS = re.compile(r'#\s*({tags})'.format(tags='|'.join(ALL_TAGS)), re.I)
REX_BAD_TAGS = re.compile(r'#\s*({tags})'.format(tags='|'.join(BAD_TAGS)), re.I)

REX_ISSUE = re.compile(r'[A-Z]{1,6}\-?\d+')
REX_TICKET = re.compile(r'\s\#\d+')

# registry with all rules
rules: list[BaseRule] = []


def register_rule(rule: type[BaseRule]) -> type[BaseRule]:
    for other in rules:
        if other.code == rule.code:
            raise ValueError('duplicate codes for rules')
    rules.append(rule())
    return rule


class BaseRule:
    code: ClassVar[int]
    text: ClassVar[str]

    def __call__(self, tokens: list[Token]) -> Iterator[Error]:
        for token in tokens:
            if self._check(token=token):
                continue
            yield Error(
                row=token.start_row,
                col=token.start_col,
                code=self.code,
                text=self.text,
            )

    def _check(self, token: Token) -> bool:
        raise NotImplementedError


@register_rule
class BadTagRule(BaseRule):
    code = 1
    text = 'use TODO instead of {tag} for consistency'

    _rex = REX_BAD_TAGS

    def __call__(self, tokens: list[Token]) -> Iterator[Error]:
        for token in tokens:
            if token.type != COMMENT:
                continue
            match = self._rex.search(token.string)
            if not match:
                continue
            yield Error(
                row=token.start_row,
                col=token.start_col,
                code=self.code,
                text=self.text.format(tag=match.group(1)),
            )


@register_rule
class MissedAuthorRule(BaseRule):
    code = 2
    text = 'add author into TODO'

    _rex = REX_ALL_TAGS

    def _check(self, token: Token) -> bool:
        if token.type != COMMENT:
            return True
        match = self._rex.search(token.string)
        if not match:
            return True

        body = token.string[match.end():].strip()
        body = body.split(':', maxsplit=1)[0]
        if not body:
            return False
        # check brackets format
        if body[0] == '(' and body[-1] == ')':
            return bool(body[1:-1].strip())
        # check alternative format using @
        if body[0] == '@':
            return bool(body[1:].strip())
        return False


@register_rule
class MissedLinkRule(BaseRule):
    code = 3
    text = 'add link on issue into TODO'

    _rex = REX_ALL_TAGS
    _rex_issue = REX_ISSUE
    _rex_ticket = REX_TICKET

    def __call__(self, tokens: list[Token]) -> Iterator[Error]:
        groups: list[str] = []
        start_tokens: list[Token] = []
        group: list[str] = []
        for token in tokens:
            if token.type in (NEWLINE, NL):
                continue

            # end of todo
            if token.type != COMMENT and group:
                groups.append('\n'.join(group))
                group = []
                continue

            # just some lines of code
            if token.type != COMMENT and not group:
                continue

            # new todo started
            if self._rex.search(token.string):
                if group:
                    # save previous todo
                    groups.append('\n'.join(group))
                start_tokens.append(token)
                group = [token.string]
                continue

            # continuation of todo
            if group:
                group.append(token.string)

        # save latest todo
        if group:
            groups.append('\n'.join(group))

        for token, text_group in zip(start_tokens, groups):
            if self._check(group=text_group):
                continue
            yield Error(
                row=token.start_row,
                col=token.start_col,
                code=self.code,
                text=self.text,
            )

    def _check(self, group: str) -> bool:  # type: ignore
        # link on issue
        if 'http://' in group or 'https://' in group:
            return True
        # issue ticket code (EIQ-911)
        if self._rex_issue.search(group):
            return True
        # issue ticket code (#911)
        if self._rex_ticket.search(group):
            return True
        return False


@register_rule
class MissedColonRule(BaseRule):
    code = 4
    text = 'missed colon in TODO'

    _rex = REX_ALL_TAGS

    def _check(self, token: Token) -> bool:
        if token.type != COMMENT:
            return True
        match = self._rex.search(token.string)
        if not match:
            return True

        if ':' not in token.string:
            return False
        body = token.string[match.end():].strip()
        return body[0] == ':' or '):' in body


@register_rule
class MissedTextRule(BaseRule):
    code = 5
    text = 'missed text in TODO'

    _rex = REX_ALL_TAGS

    def _check(self, token: Token) -> bool:
        if token.type != COMMENT:
            return True
        match = self._rex.search(token.string)
        if not match:
            return True
        body = token.string[match.end():].strip()
        if not body:
            return False
        if body[0] == ':':      # no author, but has colon
            return bool(body[1:].strip())
        if '):' not in body:    # no author and colon
            return True
        body = body.split('):', maxsplit=1)[-1].strip()
        return bool(body)


@register_rule
class InvalidCaseRule(BaseRule):
    code = 6
    text = 'write {good} instead of {bad}'

    _rex = REX_ALL_TAGS

    def __call__(self, tokens: list[Token]) -> Iterator[Error]:
        for token in tokens:
            if token.type != COMMENT:
                continue
            match = self._rex.search(token.string)
            if not match:
                continue
            if match.group(1).isupper():
                continue
            yield Error(
                row=token.start_row,
                col=token.start_col,
                code=self.code,
                text=self.text.format(
                    bad=match.group(1),
                    good=match.group(1).upper(),
                ),
            )


@register_rule
class MissedSpaceRule(BaseRule):
    code = 7
    text = 'missed space after colon in TODO'

    _rex = REX_ALL_TAGS

    def _check(self, token: Token) -> bool:
        if token.type != COMMENT:
            return True

        match = self._rex.search(token.string)
        if not match:
            return True

        if ' ' not in token.string:
            return False

        body = token.string[match.end():].strip()
        return body[:2] == ': ' or '): ' in body
