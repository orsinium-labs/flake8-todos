# built-in
from pathlib import Path
from textwrap import dedent

# external
import pytest

# project
from flake8_todos import Checker, _rules as rules


@pytest.fixture
def checker(tmp_path: Path, text: str) -> Checker:
    path = tmp_path / "test.py"
    path.write_text(dedent(text.strip("\n")))
    return Checker(filename=str(path))


@pytest.mark.parametrize(
    "rule, ok, text",
    [
        (rules.BadTagRule, True, "1 # TODO: i am ok"),
        (rules.BadTagRule, False, "1 # FIXME: inline"),
        (rules.BadTagRule, False, "# BUG: block"),
        (rules.BadTagRule, False, "1 # BUG: inline again"),
        (rules.BadTagRule, False, "1 # BUG: inline again"),
        (rules.MissedAuthorRule, True, "1 # TODO(author): i am ok"),
        (rules.MissedAuthorRule, False, "1 # TODO: missed author"),
        (rules.MissedAuthorRule, False, "1 # TODO(   ): empty brackets"),
        (rules.MissedAuthorRule, False, "1 # TODO(   ): empty brackets"),
        (rules.MissedAuthorRule, False, "1 # TODO[name]: wrong brackets"),
        (rules.MissedColonRule, True, "1 # TODO(author): i am ok"),
        (rules.MissedColonRule, True, "1 # TODO: i am also ok"),
        (rules.MissedColonRule, False, "1 # TODO(author) missed colon"),
        (rules.MissedColonRule, False, "1 # TODO missed author and colon"),
        (rules.MissedColonRule, False, "1 # TODO(author) not the right place :)"),
        (rules.MissedTextRule, True, "1 # TODO(author): i am ok"),
        (rules.MissedTextRule, True, "1 # TODO: i am ok"),
        (rules.MissedTextRule, True, "1 # TODO: taht is also ok:"),
        (rules.MissedTextRule, True, "1 # TODO(author): that is ok too:"),
        (rules.MissedTextRule, False, "1 # TODO(author):"),
        (rules.MissedTextRule, False, "1 # TODO:"),
        (rules.MissedTextRule, False, "1 # TODO(author):    "),
        (rules.MissedTextRule, False, "1 # TODO:     "),
        (rules.InvalidCaseRule, True, "1 # TODO: ok"),
        (rules.InvalidCaseRule, True, "1 # FIXME: ok"),
        (rules.InvalidCaseRule, True, "1 # BUG: ok"),
        (rules.InvalidCaseRule, False, "1 # ToDo: bad"),
        (rules.InvalidCaseRule, False, "1 # todo: bad"),
        (rules.InvalidCaseRule, False, "1 # FixMe: bad"),
        (rules.InvalidCaseRule, False, "1 # Bug: bad"),
        (
            rules.MissedLinkRule,
            True,
            "1 # TODO(author): url http://github.com/a/b/issues/1/",
        ),
        (
            rules.MissedLinkRule,
            True,
            "1 # TODO(author): url https://github.com/a/b/issues/1/",
        ),
        (rules.MissedLinkRule, True, "1 # TODO(author): code EIQ-911"),
        (rules.MissedLinkRule, True, "1 # TODO: no author EIQ-911"),
        (rules.MissedLinkRule, True, "1 # TODO no colon EIQ-911"),
        (rules.MissedLinkRule, False, "1 # TODO(author): no code or link"),
        (rules.MissedLinkRule, False, "1 # TODO(author): lowercase lol-911"),
    ],
)
def test_rules(rule: rules.BaseRule, ok: bool, checker: Checker):
    """Test all rules

    + `rule` goes from parametrize and used to filter errors by this rule code.
    + `ok` goes from parametrize and indicates that this rule must return error
        for given text.
    + `text` goes from parametrize into `checker` fixture.
    + `checker` fixture saves given `text` in file and init `Checker` instance
        with this file.
    """
    errors = [error for error in checker.get_errors() if error.code == rule.code]
    if ok:
        assert len(errors) == 0
    else:
        assert len(errors) == 1
        assert errors[0].row == 1


@pytest.mark.parametrize(
    "text",
    [
        """
    # TODO: multiline
    # link goes here http://github.com/a/b/issues/1/
    # TODO: new todo
    c = 15
"""
    ],
)
def test_missed_link(checker: Checker):
    errors = [error for error in checker.get_errors() if error.code == 3]
    assert {error.row for error in errors} == {3}
