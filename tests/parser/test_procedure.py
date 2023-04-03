import pytest

from ats.parser.parser import parse
from ats.parser.utils import RESTRICTED_TOKENS


def test_empty_procedure_no_name():
    with pytest.raises(ValueError, match="Token '{' is not a valid NAME_TOKEN"):
        parse("procedure {}")


def test_empty_procedure_no_brackets():
    with pytest.raises(ValueError, match="Expected token '{', got end of file"):
        parse("procedure proc")


def test_procedure_expects_expr():
    with pytest.raises(ValueError, match="Token '}' is not a valid NAME_TOKEN"):
        parse("procedure proc {}")


def test_procedure_expects_assignment():
    parse(
        """
        procedure proc {
            test = 8;
        }
    """
    )


def test_procedure_multiple_statements():
    parse(
        """
        procedure proc {
            test1 = 8;
            test2 = 8;
        }
    """
    )


def test_procedure_restricted_keyword_as_name():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure {x} {{ a = 8; }}")
