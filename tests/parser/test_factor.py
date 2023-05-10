import pytest

from ats.parser.parser import parse
from ats.parser.utils import RESTRICTED_TOKENS


def test_factor_restricted_keyword_as_var():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ a = {x}; }}")


def test_factor_restricted_keyword_as_var_in_plus_expr():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ a = {x} + 8; }}")


def test_factor_restricted_keyword_as_var_in_minus_expr():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ a = {x} - 8; }}")


def test_factor_bracket():
    parse(
        """
        procedure proc {
            test = ( b * 2 );
        }
    """
    )


def test_factor_bracket_complex_plus():
    parse(
        """
        procedure proc {
            test = 2 + ( b * 2 );
        }
    """
    )


def test_factor_bracket_complex_minus():
    parse(
        """
        procedure proc {
            test = 2 - ( b * 2 );
        }
    """
    )
