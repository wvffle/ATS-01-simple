import pytest

from ats.parser.parser import parse
from ats.parser.utils import RESTRICTED_TOKENS


def test_empty_if_no_var():
    with pytest.raises(ValueError, match="Token 'then' is a reserved keyword"):
        parse(
            """
            procedure proc {
                if then {}
            }
        """
        )


def test_empty_if_no_then():
    with pytest.raises(ValueError, match="Expected token 'then', got '{'"):
        parse(
            """
            procedure proc {
                if test {}
            }
        """
        )


def test_empty_if_no_brackets():
    with pytest.raises(ValueError, match="Expected token '{', got '}"):
        parse(
            """
            procedure proc {
                if test then
            }
        """
        )


def test_if_expects_expr():
    with pytest.raises(ValueError, match="Token '}' is not a valid NAME_TOKEN"):
        parse(
            """
            procedure proc {
                if test then {}
            }
        """
        )


def test_empty_if_no_else():
    with pytest.raises(ValueError, match="Expected token 'else', got '}'"):
        parse(
            """
            procedure proc {
                if test then {
                    test = 3;
                }
            }
        """
        )


def test_empty_if_else_no_brackets():
    with pytest.raises(ValueError, match="Expected token '{', got '}"):
        parse(
            """
            procedure proc {
                if test then {
                    test = 1;
                } else
            }
        """
        )


def test_if_else_expects_expr():
    with pytest.raises(ValueError, match="Token '}' is not a valid NAME_TOKEN"):
        parse(
            """
            procedure proc {
                if test then {
                    test = 2;
                } else {}
            }
        """
        )


def test_if_expects_assignment():
    parse(
        """
        procedure proc {
            if test then {
                test = 8;
            }
            else {
                test = 2;
            }
        }
    """
    )


def test_if_multiple_statements():
    parse(
        """
        procedure proc {
            if test then {
                test1 = 8;
                test2 = 8;
            }
            else {
                test3 = 1;
            }
        }
    """
    )


def test_if_restricted_keyword_as_var():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ if {x} {{ a = 8; }} }}")
