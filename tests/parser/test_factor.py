import pytest

from ats.parser.parser import parse


def test_factor_restricted_keyword_as_var():
    for x in ["if", "then", "else", "while", "procedure"]:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ a = {x}; }}")


def test_factor_restricted_keyword_as_var_with_adding():
    for x in ["if", "then", "else", "while", "procedure"]:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ a = {x} + 8; }}")
