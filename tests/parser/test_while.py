import pytest

from ats.parser.parser import parse
from ats.parser.utils import RESTRICTED_TOKENS


def test_empty_while_no_var():
    with pytest.raises(ValueError, match="Token '{' is not a valid NAME_TOKEN"):
        parse(
            """
            procedure proc {
                while {}
            }
        """
        )


def test_empty_while_no_brackets():
    with pytest.raises(ValueError, match="Expected token '{', got '}"):
        parse(
            """
            procedure proc {
                while test
            }
        """
        )


def test_while_expects_expr():
    with pytest.raises(ValueError, match="Token '}' is not a valid NAME_TOKEN"):
        parse(
            """
            procedure proc {
                while test {}
            }
        """
        )


def test_while_expects_assignment():
    parse(
        """
        procedure proc {
            while test {
                test = 8;
            }
        }
    """
    )


def test_while_multiple_statements():
    parse(
        """
        procedure proc {
            while test {
                test1 = 8;
                test2 = 8;
            }
        }
    """
    )


def test_while_restricted_keyword_as_var():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ while {x} {{ a = 8; }} }}")
